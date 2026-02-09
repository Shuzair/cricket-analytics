"""
Bronze Layer – Cricket Match File Metadata Pipeline
====================================================
Extract metadata from Cricsheet JSON files and upsert into
bronze.cricket_match_file_metadata.

Files that fail extraction are logged to
bronze.cricket_match_file_processing_failures (truncate-insert per run).

Usage:
    python scripts/bronze_GenerateFileMetaData.py [data_directory]
"""

import hashlib
import json
import logging
import sys
from pathlib import Path
from typing import Generator

# ── Project imports ─────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from db.connection import get_connection

# ── Logging ─────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────────────────────
BATCH_SIZE = 500  # rows per INSERT batch – balances memory vs round-trips
PROJECT_ROOT = Path(__file__).resolve().parent.parent

UPSERT_SQL = """
    INSERT INTO bronze.cricket_match_file_metadata
        (start_date, team_type, match_type, gender, match_id, teams, file_path, file_hash)
    VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (file_hash) DO UPDATE SET
        last_modified_timestamp = CURRENT_TIMESTAMP
"""

TRUNCATE_FAILURES_SQL = "TRUNCATE TABLE bronze.cricket_match_file_processing_failures RESTART IDENTITY"

INSERT_FAILURE_SQL = """
    INSERT INTO bronze.cricket_match_file_processing_failures
        (file_path, error_message, error_type)
    VALUES
        (%s, %s, %s)
"""


# ── Helpers ─────────────────────────────────────────────────────────────────────

def file_sha256(filepath: str, buf_size: int = 65536) -> str:
    """Compute SHA-256 hash using buffered reads (constant memory)."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(buf_size):
            h.update(chunk)
    return h.hexdigest()


def extract_record(filepath: str) -> tuple:
    """
    Parse a single Cricsheet JSON file and return a tuple ready for INSERT.
    Raises ValueError for validation issues, lets OSError / JSONDecodeError propagate.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    info = data.get("info")
    if info is None:
        raise ValueError("missing 'info' key in JSON")

    dates = info.get("dates")
    start_date = dates[0] if dates and isinstance(dates, list) else None

    team_type = info.get("team_type")
    match_type = info.get("match_type")
    gender = info.get("gender")

    missing = [k for k, v in {"start_date": start_date, "team_type": team_type,
                               "match_type": match_type, "gender": gender}.items() if not v]
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")

    match_id = Path(filepath).stem
    teams = info.get("teams", [])
    teams_str = " vs ".join(teams) if isinstance(teams, list) and teams else None
    if not teams_str:
        raise ValueError("missing or empty 'teams' array")

    rel_path = str(Path(filepath).resolve().relative_to(PROJECT_ROOT))
    fhash = file_sha256(filepath)

    return (start_date, team_type, match_type, gender, match_id, teams_str, rel_path, fhash)


def iter_files(data_dir: str) -> Generator[tuple | tuple, None, None]:
    """
    Yield (record_tuple, None) for successes or (None, failure_tuple) for failures
    per valid JSON file (sorted, non-recursive).
    """
    dir_path = Path(data_dir)
    if not dir_path.is_dir():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    for entry in sorted(dir_path.iterdir()):
        if entry.suffix.lower() != ".json" or not entry.is_file():
            continue

        filepath = str(entry)
        rel_path = str(entry.resolve().relative_to(PROJECT_ROOT))

        try:
            record = extract_record(filepath)
            yield (record, None)
        except Exception as exc:
            error_type = type(exc).__name__
            error_msg = str(exc)[:500]  # cap length for DB column
            log.warning("FAILED %s [%s]: %s", rel_path, error_type, error_msg)
            yield (None, (rel_path, error_msg, error_type))


# ── Database loader ─────────────────────────────────────────────────────────────

def load_to_db(data_dir: str) -> tuple[int, int]:
    """
    Stream records from JSON files into PostgreSQL in batches.
    - Upserts successful records into bronze.cricket_match_file_metadata
    - Truncates then inserts failures into bronze.cricket_match_file_processing_failures
    Returns (rows_upserted, rows_failed).
    """
    conn = get_connection()
    total = 0
    batch: list[tuple] = []
    failures: list[tuple] = []

    try:
        with conn.cursor() as cur:
            # Truncate failures table at the start of every run
            cur.execute(TRUNCATE_FAILURES_SQL)
            conn.commit()
            log.info("Truncated bronze.cricket_match_file_processing_failures")

            # ── Stream files ────────────────────────────────────────────────
            for record, failure in iter_files(data_dir):
                if failure is not None:
                    failures.append(failure)
                    continue

                batch.append(record)
                if len(batch) >= BATCH_SIZE:
                    cur.executemany(UPSERT_SQL, batch)
                    conn.commit()
                    total += len(batch)
                    log.info("Committed batch – %d rows so far", total)
                    batch.clear()

            # flush remaining successes
            if batch:
                cur.executemany(UPSERT_SQL, batch)
                conn.commit()
                total += len(batch)

            # ── Flush failures in one batch ─────────────────────────────────
            if failures:
                cur.executemany(INSERT_FAILURE_SQL, failures)
                conn.commit()
                log.warning("Logged %d failure(s) to processing_failures table", len(failures))

    except Exception:
        conn.rollback()
        log.exception("Pipeline failed – transaction rolled back")
        raise
    finally:
        conn.close()

    return total, len(failures)


# ── Entry point ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    data_directory = sys.argv[1] if len(sys.argv) > 1 else "data"
    log.info("Starting metadata ingestion from '%s'", data_directory)

    try:
        rows, failed = load_to_db(data_directory)
        log.info(
            "Done – %d rows upserted, %d failures logged", rows, failed
        )
        if failed:
            log.warning("Check bronze.cricket_match_file_processing_failures for details")
    except FileNotFoundError as exc:
        log.error(exc)
        sys.exit(1)
    except Exception:
        log.error("Pipeline failed")
        sys.exit(1)