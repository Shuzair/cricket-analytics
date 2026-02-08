import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Generator

import pandas as pd



def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def file_sha256(filepath: str, buf_size: int = 65536) -> str:
    """Compute SHA-256 hash of a file using buffered reads."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(buf_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def extract_record(filepath: str) -> dict | None:
    """
    Extract a single record from a Cricsheet JSON file.
    Returns None if the file is invalid or unreadable.
    """
    try:
        data = load_json(filepath)
    except (json.JSONDecodeError, ValueError, OSError) as e:
        print(f"[WARN] Skipping {filepath}: {e}", file=sys.stderr)
        return None

    info = data.get("info")
    if info is None:
        print(f"[WARN] Skipping {filepath}: missing 'info' section", file=sys.stderr)
        return None

    # 1. Start date – first element of the dates array
    dates = info.get("dates")
    start_date = dates[0] if dates and isinstance(dates, list) else None

    # 2. Team type – 'club' or 'international'
    team_type = info.get("team_type")

    # 3. Match type – Test, ODI, T20, IT20, ODM, MDM, or club competition code
    match_type = info.get("match_type")

    # 4. Gender
    gender = info.get("gender")

    # 5. Match ID – derived from the filename (Cricsheet convention: <id>.json)
    match_id = Path(filepath).stem

    # 6. Teams
    teams = info.get("teams", [])
    # Store as a consistent string "Team1 vs Team2" for easy querying
    teams_str = " vs ".join(teams) if isinstance(teams, list) and teams else None

    # 7. File path (absolute)
    file_path = os.path.abspath(filepath)

    # 8. File hash (SHA-256)
    try:
        file_hash = file_sha256(filepath)
    except OSError as e:
        print(f"[WARN] Could not hash {filepath}: {e}", file=sys.stderr)
        file_hash = None

    return {
        "start_date": start_date,
        "team_type": team_type,
        "match_type": match_type,
        "gender": gender,
        "match_id": match_id,
        "teams": teams_str,
        "file_path": file_path,
        "file_hash": file_hash,
    }


def iter_records(data_dir: str) -> Generator[dict, None, None]:
    """Yield one record dict per valid JSON file in data_dir (non-recursive)."""
    dir_path = Path(data_dir)
    if not dir_path.is_dir():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    for entry in sorted(dir_path.iterdir()):
        if entry.suffix.lower() == ".json" and entry.is_file():
            record = extract_record(str(entry))
            if record is not None:
                yield record


def build_dataframe(data_dir: str = "data") -> pd.DataFrame:
    """
    Build a DataFrame from all Cricsheet JSON files in `data_dir`.

    Columns:
        start_date  : str   (YYYY-MM-DD)
        team_type   : str   ('club' | 'international')
        match_type  : str   (Test, ODI, T20, IT20, ODM, MDM, or competition code)
        gender      : str   ('male' | 'female')
        match_id    : str   (filename stem, e.g. '1234567')
        teams       : str   ('Team A vs Team B')
        file_path   : str   (absolute path)
        file_hash   : str   (SHA-256 hex digest)
    """
    records = list(iter_records(data_dir))

    if not records:
        print("[INFO] No valid JSON files found.", file=sys.stderr)
        return pd.DataFrame(
            columns=[
                "start_date", "team_type", "match_type", "gender",
                "match_id", "teams", "file_path", "file_hash",
            ]
        )

    df = pd.DataFrame(records)

    # Convert start_date to datetime for efficient querying; invalid dates become NaT
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")

    # Use categoricals for low-cardinality columns to save memory
    for col in ("team_type", "match_type", "gender"):
        df[col] = df[col].astype("category")

    return df


# ── Main ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    data_directory = sys.argv[1] if len(sys.argv) > 1 else "data"
    df = build_dataframe(data_directory)
    print(f"Loaded {len(df)} matches from '{data_directory}'")
    print(df.head(10).to_string(index=False))
    print(f"\nDtypes:\n{df.dtypes}")