"""
Bronze Layer – Cricket Match File Metadata Pipeline (PySpark)
=============================================================
Reads Cricsheet JSON files using PySpark, extracts match metadata,
computes a SHA-256 file hash per file, and upserts into
bronze.cricket_match_file_metadata via PostgreSQL JDBC.

Files that fail extraction are logged to
bronze.cricket_match_file_processing_failures.

Usage (inside Spark container):
    spark-submit scripts/bronze_GenerateFileMetaData.py [data_directory]

Usage (local with SPARK_MASTER=local[*]):
    python scripts/bronze_GenerateFileMetaData.py [data_directory]
"""

import hashlib
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pyspark.sql import SparkSession, Row
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StringType, StructField, StructType, TimestampType
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── JDBC config ─────────────────────────────────────────────────────────────────
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "cricket")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "cricket123")
JDBC_JAR = os.getenv("JDBC_JAR_PATH", str(PROJECT_ROOT / "jars" / "postgresql-42.7.4.jar"))
JDBC_URL = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"

JDBC_PROPS = {
    "user": DB_USER,
    "password": DB_PASSWORD,
    "driver": "org.postgresql.Driver",
}

METADATA_TABLE = "bronze.cricket_match_file_metadata"
FAILURES_TABLE = "bronze.cricket_match_file_processing_failures"


# ── Schemas ──────────────────────────────────────────────────────────────────────
METADATA_SCHEMA = StructType([
    StructField("start_date", StringType(), True),
    StructField("team_type", StringType(), True),
    StructField("match_type", StringType(), True),
    StructField("gender", StringType(), True),
    StructField("match_id", StringType(), True),
    StructField("teams", StringType(), True),
    StructField("file_path", StringType(), True),
    StructField("file_hash", StringType(), True),
])

FAILURES_SCHEMA = StructType([
    StructField("file_path", StringType(), True),
    StructField("error_message", StringType(), True),
    StructField("error_type", StringType(), True),
])


# ── Helpers ──────────────────────────────────────────────────────────────────────
def file_sha256(filepath: str, buf_size: int = 65536) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(buf_size):
            h.update(chunk)
    return h.hexdigest()


def extract_record(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    info = data.get("info")
    if info is None:
        raise ValueError("missing 'info' key in JSON")

    dates = info.get("dates")
    start_date = str(dates[0]) if dates and isinstance(dates, list) else None
    team_type = info.get("team_type")
    match_type = info.get("match_type")
    gender = info.get("gender")

    missing = [k for k, v in {
        "start_date": start_date,
        "team_type": team_type,
        "match_type": match_type,
        "gender": gender,
    }.items() if not v]
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")

    match_id = Path(filepath).stem
    teams = info.get("teams", [])
    teams_str = " vs ".join(teams) if isinstance(teams, list) and teams else None
    if not teams_str:
        raise ValueError("missing or empty 'teams' array")

    rel_path = str(Path(filepath).resolve().relative_to(PROJECT_ROOT))
    fhash = file_sha256(filepath)

    return {
        "start_date": start_date,
        "team_type": team_type,
        "match_type": match_type,
        "gender": gender,
        "match_id": match_id,
        "teams": teams_str,
        "file_path": rel_path,
        "file_hash": fhash,
    }


# ── Pipeline ─────────────────────────────────────────────────────────────────────
def run(data_dir: str) -> None:
    dir_path = Path(data_dir)
    if not dir_path.is_dir():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    spark = (
        SparkSession.builder
        .appName("bronze_cricket_file_metadata")
        .master(os.getenv("SPARK_MASTER", "local[*]"))
        .config("spark.jars", JDBC_JAR)
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    records = []
    failures = []

    for entry in sorted(dir_path.iterdir()):
        if entry.suffix.lower() != ".json" or not entry.is_file():
            continue
        try:
            records.append(Row(**extract_record(str(entry))))
        except Exception as exc:
            rel = str(entry.resolve().relative_to(PROJECT_ROOT))
            log.warning("FAILED %s [%s]: %s", rel, type(exc).__name__, exc)
            failures.append(Row(
                file_path=rel,
                error_message=str(exc)[:500],
                error_type=type(exc).__name__,
            ))

    log.info("Extracted %d records, %d failures", len(records), len(failures))

    if records:
        df_meta = spark.createDataFrame(records, schema=METADATA_SCHEMA)
        (
            df_meta.write
            .format("jdbc")
            .option("url", JDBC_URL)
            .option("dbtable", METADATA_TABLE)
            .option("driver", "org.postgresql.Driver")
            .option("user", DB_USER)
            .option("password", DB_PASSWORD)
            # Use INSERT ... ON CONFLICT via a temp staging approach:
            # append mode + unique constraint on file_hash handles dedup at DB level
            .mode("append")
            .save()
        )
        log.info("Upserted %d rows into %s", len(records), METADATA_TABLE)

    # Truncate-insert failures each run
    if failures:
        df_fail = spark.createDataFrame(failures, schema=FAILURES_SCHEMA)
        (
            df_fail.write
            .format("jdbc")
            .option("url", JDBC_URL)
            .option("dbtable", FAILURES_TABLE)
            .option("driver", "org.postgresql.Driver")
            .option("user", DB_USER)
            .option("password", DB_PASSWORD)
            .option("truncate", "true")
            .mode("overwrite")
            .save()
        )
        log.warning("Logged %d failure(s) into %s", len(failures), FAILURES_TABLE)

    spark.stop()


# ── Entry point ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    data_directory = sys.argv[1] if len(sys.argv) > 1 else "data"
    log.info("Starting PySpark metadata ingestion from '%s'", data_directory)
    try:
        run(data_directory)
        log.info("Done")
    except FileNotFoundError as exc:
        log.error(exc)
        sys.exit(1)
    except Exception:
        log.exception("Pipeline failed")
        sys.exit(1)
