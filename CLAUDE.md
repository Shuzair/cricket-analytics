# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- **PostgreSQL 16** — all analytics storage, run via Docker
- **PySpark 3.5** — bronze layer ingestion (reads Cricsheet JSON, writes via JDBC)
- **dbt-postgres 1.9** — all transformations (bronze → silver → gold_ba / gold_ml)
- **bitnami/spark:3.5** and **ghcr.io/dbt-labs/dbt-postgres:1.9.latest** Docker images

## Commands

### Start all services
```bash
docker compose up -d
```

### Run the bronze ingestion pipeline (inside spark container)
```bash
docker compose exec spark spark-submit /opt/spark/scripts/bronze_GenerateFileMetaData.py /opt/spark/data
```

### Run dbt commands
```bash
docker compose run --rm dbt dbt debug          # test connection
docker compose run --rm dbt dbt run            # run all models
docker compose run --rm dbt dbt run --select silver   # run one layer
docker compose run --rm dbt dbt test           # run dbt tests
```

### Export live DB objects back to SQL files (for version control)
```bash
python scripts/export_db_objects.py --all
python scripts/export_db_objects.py --functions
python scripts/export_db_objects.py --views
```
> Note: `export_db_objects.py` still uses `src/db/connection.py` (psycopg3). If that module is removed, update the script to use a direct psycopg3 connection.

### Run Python tests
```bash
pytest
```

### Local Python setup
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then edit .env with your passwords
```

## Architecture

### Data flow
```
Cricsheet JSON files (data/)
    → PySpark (scripts/bronze_GenerateFileMetaData.py)
        → bronze.cricket_match_file_metadata       [PostgreSQL]
        → bronze.cricket_match_file_processing_failures
    → dbt models (dbt/models/silver/)
        → silver schema
    → dbt models (dbt/models/gold_ba/ or gold_ml/)
        → gold_ba schema (business analytics)
        → gold_ml schema (ML features)
```

### Medallion layers (PostgreSQL schemas)

| Schema | Owner | Purpose |
|---|---|---|
| `bronze` | PySpark | Raw file metadata, one row per Cricsheet JSON file |
| `silver` | dbt | Cleaned and typed data from bronze |
| `gold_ba` | dbt | Business analytics aggregations |
| `gold_ml` | dbt | Feature tables for ML models |
| `ref` | manual | Reference / dimension tables |
| `public` | init SQL | Seed example tables (matches, players, batting/bowling stats) |

### JDBC dependency
PySpark connects to PostgreSQL via `jars/postgresql-42.7.4.jar`. This file is git-ignored — download it manually:
```bash
curl -L https://jdbc.postgresql.org/download/postgresql-42.7.4.jar -o jars/postgresql-42.7.4.jar
```
The jar is mounted read-only into the spark container at `/opt/bitnami/spark/jars/postgresql.jar`.

### dbt project layout
- `dbt/profiles.yml` — reads connection from env vars (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`); default schema is `bronze` (source)
- `dbt/dbt_project.yml` — each model subfolder maps to its target schema (`silver`, `gold_ba`, `gold_ml`), all materialized as tables by default
- Models go in `dbt/models/<layer>/` — filenames become table names in the corresponding schema

### SQL version control convention
- All DB object definitions live in `sql/` and are committed to git
- After editing objects in a SQL IDE, export them back with `export_db_objects.py`
- `sql/init/` files auto-run once when the Postgres container first starts
- `sql/migrations/` files are numbered (`003_`, `004_`, …) and run manually

### DBeaver access
Connect with `localhost:5432`, database `cricket`, credentials from `.env`. No extra config needed.
