# Cricket Analytics Project — Complete Guide

This document covers everything you need to set up and work with the Cricket Analytics project.

---

# PART 1: SETUP

## Prerequisites

Install these before starting:

| Software | Mac | Windows | Linux |
|----------|-----|---------|-------|
| **Git** | `brew install git` | https://git-scm.com/download/win | `sudo apt install git` |
| **Docker Desktop** | https://docker.com/products/docker-desktop | https://docker.com/products/docker-desktop | https://docker.com/products/docker-desktop |
| **Python 3.10+** | `brew install python` | https://python.org/downloads (✅ Check "Add to PATH") | `sudo apt install python3 python3-venv python3-pip` |

> **PySpark and dbt run inside Docker** — you do not need to install them locally.

---

## Step 1: Clone the Repository

```bash
cd ~
git clone git@github.com:YOUR_USERNAME/cricket-analytics.git
cd cricket-analytics
```

---

## Step 2: Configure Git Identity (Optional)

If this is a personal project on a work machine:

```bash
git config user.name "Your Name"
git config user.email "your.personal.email@gmail.com"
```

---

## Step 3: Set Up Environment File

```bash
cp .env.example .env
```

Edit `.env` if you want to change the default database password.

---

## Step 4: Download the PostgreSQL JDBC Driver

PySpark uses JDBC to write to PostgreSQL. Download the driver into the `jars/` folder:

```bash
curl -L https://jdbc.postgresql.org/download/postgresql-42.7.4.jar -o jars/postgresql-42.7.4.jar
```

This file is git-ignored (binary). You need to re-download it on each new machine.

---

## Step 5: Start PostgreSQL

Make sure Docker Desktop is running, then start only the database:

```bash
docker compose up postgres -d
```

Verify it's running:

```bash
docker ps
```

You should see `cricket_postgres` in the list.

> **Why only postgres?** Spark and dbt are run on-demand for specific tasks — they don't need to stay running. See the [Daily Workflow](#daily-workflow) section.

---

## Step 6: Set Up Python Environment (for local scripts)

### Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.bat
pip install -r requirements.txt
```

### Windows (Command Prompt):

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 7: Connect Your SQL IDE (DBeaver / pgAdmin / DataGrip)

| Setting | Value |
|---------|-------|
| Host | `localhost` |
| Port | `5432` |
| Database | `cricket` |
| User | `postgres` |
| Password | `cricket123` (or your `.env` value) |

---

## Setup Complete!

Your environment is ready:
- ✅ PostgreSQL running in Docker
- ✅ JDBC driver in `jars/`
- ✅ Python environment configured
- ✅ SQL IDE connected

---

# PART 2: ARCHITECTURE

## Data Stack

| Tool | Version | Role |
|------|---------|------|
| **PostgreSQL** | 16 | Storage — runs always |
| **PySpark** | 3.5 | Bronze layer ETL — reads Cricsheet JSON, writes via JDBC |
| **dbt** | 1.9 | Transformations — bronze → silver → gold |

All three services share a Docker network (`cricket_net`). Spark and dbt reach the database using the hostname `postgres` (the Docker service name), not `localhost`.

## Medallion Architecture

```
Cricsheet JSON files  (data/)
        │
        ▼
   PySpark ETL  (scripts/bronze_GenerateFileMetaData.py)
        │
        ├──▶  bronze.cricket_match_file_metadata
        └──▶  bronze.cricket_match_file_processing_failures
                        │
                        ▼
                 dbt silver models  (dbt/models/silver/)
                        │
                        ├──▶  silver schema
                        │
                        ▼
              dbt gold models
                        ├──▶  gold_ba schema  (business analytics)
                        └──▶  gold_ml schema  (ML features)
```

## PostgreSQL Schemas

| Schema | Populated by | Purpose |
|--------|-------------|---------|
| `bronze` | PySpark | Raw file metadata from Cricsheet JSON |
| `silver` | dbt | Cleaned and typed data |
| `gold_ba` | dbt | Business analytics aggregations |
| `gold_ml` | dbt | Feature tables for ML models |
| `ref` | manual SQL | Reference / dimension tables |
| `public` | init SQL | Seed example tables (matches, players, stats) |

## Project Structure

```
cricket-analytics/
├── docker-compose.yml      # All three services + shared network
├── dbt/                    # dbt project
│   ├── dbt_project.yml
│   ├── profiles.yml        # DB connection (reads from env vars)
│   └── models/
│       ├── silver/
│       ├── gold_ba/
│       └── gold_ml/
├── scripts/
│   ├── bronze_GenerateFileMetaData.py  # PySpark bronze ETL
│   └── export_db_objects.py            # Export live DB objects to SQL files
├── sql/
│   ├── init/               # Auto-runs once on first DB start
│   ├── migrations/         # Numbered schema changes (run manually)
│   ├── schemas/            # Schema creation scripts
│   ├── tables/             # Table DDL
│   ├── functions/          # Stored functions
│   └── views/              # SQL views
├── jars/                   # JDBC driver (git-ignored)
├── data/                   # Cricsheet JSON files (git-ignored)
├── src/                    # Python utilities
└── notebooks/              # Jupyter notebooks
```

---

# PART 3: WORKFLOW

## Daily Workflow

### Starting Your Day

```bash
# 1. Start PostgreSQL (always-on)
docker compose up postgres -d

# 2. Activate Python environment (for local scripts)
source venv/bin/activate        # Mac/Linux
.\venv\Scripts\Activate.bat     # Windows

# 3. Open your SQL IDE and connect
# 4. Pull latest changes
git pull
```

### Running the Bronze Pipeline (PySpark)

PySpark starts on demand, runs the job, then stops:

```bash
docker compose run --rm spark spark-submit \
  /opt/spark/scripts/bronze_GenerateFileMetaData.py \
  /opt/spark/data
```

### Running dbt Transformations

```bash
# Test connection
docker compose run --rm dbt dbt debug

# Run all models (bronze → silver → gold)
docker compose run --rm dbt dbt run

# Run a single layer only
docker compose run --rm dbt dbt run --select silver
docker compose run --rm dbt dbt run --select gold_ba
docker compose run --rm dbt dbt run --select gold_ml

# Run dbt tests
docker compose run --rm dbt dbt test
```

---

## How to Save SQL Work to Git

### The Golden Rule

> **If it's not in a file in your project folder, it won't go to GitHub.**

When you create something in your SQL IDE (function, view, table), it lives in the database only. You must save it to a `.sql` file.

---

### Method A: Write SQL Files First (Recommended)

**1. Create a SQL file:**

```bash
touch sql/functions/calculate_average.sql
```

**2. Write your SQL in the file:**

```sql
CREATE OR REPLACE FUNCTION calculate_batting_average(
    p_runs INTEGER,
    p_innings INTEGER,
    p_not_outs INTEGER
)
RETURNS NUMERIC AS $$
BEGIN
    IF (p_innings - p_not_outs) <= 0 THEN
        RETURN p_runs;
    END IF;
    RETURN ROUND(p_runs::NUMERIC / (p_innings - p_not_outs), 2);
END;
$$ LANGUAGE plpgsql;
```

**3. Run the file against the database:**

**Mac/Linux:**
```bash
docker exec -i cricket_postgres psql -U postgres -d cricket < sql/functions/calculate_average.sql
```

**Windows (PowerShell):**
```powershell
Get-Content sql/functions/calculate_average.sql | docker exec -i cricket_postgres psql -U postgres -d cricket
```

**4. Commit to Git:**

```bash
git add sql/functions/calculate_average.sql
git commit -m "feat: add batting average function"
git push
```

---

### Method B: Create in SQL IDE, Then Export

**1. Create your function/view/table in the SQL IDE and execute it.**

**2. Export to files:**

```bash
source venv/bin/activate   # ensure venv is active

python scripts/export_db_objects.py --all        # export everything
python scripts/export_db_objects.py --functions  # functions only
python scripts/export_db_objects.py --views      # views only
python scripts/export_db_objects.py --tables     # table schemas only
```

**3. Commit the exported files.**

---

## SQL File Organization

| Type | Location | Notes |
|------|----------|-------|
| Init scripts | `sql/init/` | Auto-run once on first container start |
| Schema changes | `sql/migrations/` | Numbered (`004_`, `005_`, …), run manually |
| Table definitions | `sql/tables/` | DDL for bronze tables and public seed tables |
| Schemas | `sql/schemas/` | One file per schema (`bronze.sql`, `silver.sql`, etc.) |
| Functions | `sql/functions/` | Stored functions |
| Views | `sql/views/` | SQL views |

> **dbt models are not stored in `sql/`** — they live in `dbt/models/` and are managed by dbt.

---

## Running SQL Files

**Single file:**

```bash
# Mac/Linux
docker exec -i cricket_postgres psql -U postgres -d cricket < sql/functions/my_function.sql

# Windows (PowerShell)
Get-Content sql/functions/my_function.sql | docker exec -i cricket_postgres psql -U postgres -d cricket
```

**All files in a folder:**

```bash
# Mac/Linux
for f in sql/functions/*.sql; do
  echo "Running $f..."
  docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"
done
```

```powershell
# Windows (PowerShell)
Get-ChildItem sql/functions/*.sql | ForEach-Object {
    Write-Host "Running $_..."
    Get-Content $_.FullName | docker exec -i cricket_postgres psql -U postgres -d cricket
}
```

---

## Git Workflow

### Before You Start Working

```bash
git pull
```

### After Making Changes

```bash
git status                               # see what changed
git diff                                 # review line-by-line changes
python scripts/export_db_objects.py --all  # export any IDE work
git add .
git commit -m "feat: add player statistics view"
git push
```

### Good Commit Messages

```bash
# ✅ Good
git commit -m "feat: add calculate_strike_rate function"
git commit -m "fix: correct batting average for not-outs"
git commit -m "chore: export updated player_summary view"

# ❌ Bad
git commit -m "update"
git commit -m "changes"
```

---

## Setting Up on a New Machine

```bash
# 1. Clone
git clone git@github.com:YOUR_USERNAME/cricket-analytics.git
cd cricket-analytics

# 2. Environment
cp .env.example .env

# 3. Download JDBC driver
curl -L https://jdbc.postgresql.org/download/postgresql-42.7.4.jar -o jars/postgresql-42.7.4.jar

# 4. Start PostgreSQL (DB auto-creates from sql/init/ files)
docker compose up postgres -d

# 5. Python environment
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt

# 6. Apply migrations and functions
for f in sql/migrations/*.sql; do docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"; done
for f in sql/functions/*.sql; do docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"; done
for f in sql/views/*.sql; do docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"; done
```

---

# PART 4: REFERENCE

## Docker Commands

| Task | Command |
|------|---------|
| Start PostgreSQL (always-on) | `docker compose up postgres -d` |
| Run bronze ETL (on demand) | `docker compose run --rm spark spark-submit /opt/spark/scripts/bronze_GenerateFileMetaData.py /opt/spark/data` |
| Run dbt models | `docker compose run --rm dbt dbt run` |
| Stop all services | `docker compose down` |
| View logs | `docker compose logs -f postgres` |
| Reset database (delete all data) | `docker compose down -v && docker compose up postgres -d` |

## dbt Commands

| Task | Command |
|------|---------|
| Test DB connection | `docker compose run --rm dbt dbt debug` |
| Run all models | `docker compose run --rm dbt dbt run` |
| Run one layer | `docker compose run --rm dbt dbt run --select silver` |
| Run tests | `docker compose run --rm dbt dbt test` |

## Database CLI

```bash
# Connect to PostgreSQL CLI
docker exec -it cricket_postgres psql -U postgres -d cricket

# Inside psql:
\dt              # list tables in current schema
\dt bronze.*     # list tables in bronze schema
\df              # list functions
\dv              # list views
\dn              # list schemas
\d tablename     # describe a table
\q               # quit
```

## Python / Local Scripts

| Task | Command |
|------|---------|
| Activate venv (Mac/Linux) | `source venv/bin/activate` |
| Activate venv (Windows) | `.\venv\Scripts\Activate.bat` |
| Export DB objects to SQL files | `python scripts/export_db_objects.py --all` |
| Run tests | `pytest` |

---

## Troubleshooting

### PostgreSQL not starting
- Make sure Docker Desktop is open
- Try: `docker compose down && docker compose up postgres -d`
- Check logs: `docker compose logs postgres`

### PySpark can't connect to PostgreSQL
- Verify the JDBC jar exists: `ls jars/postgresql-42.7.4.jar`
- Confirm postgres is healthy: `docker compose ps`
- The JDBC URL must use `postgres` (the service name), not `localhost`, when running inside Docker

### dbt connection failed
- Run `docker compose run --rm dbt dbt debug` to see the full error
- Confirm `DB_HOST=postgres` is set (not `localhost`) — this is the default in `dbt/profiles.yml` when inside Docker
- Verify postgres is running: `docker compose ps`

### Can't connect via DBeaver
- Use `localhost` (not `postgres`) as the host — DBeaver runs on your machine, not inside Docker
- Verify port 5432 is not used by another app: `lsof -i :5432`

### Python venv won't activate (Windows)
- Use `.\venv\Scripts\Activate.bat` instead of the `.ps1` version
- Or enable scripts: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### "Module not found" in Python
- Make sure venv is activated (you should see `(venv)` in terminal)
- Reinstall: `pip install -r requirements.txt`

### Permission denied (Git)
- Make sure SSH key is added to GitHub: https://github.com/settings/keys
- Test with: `ssh -T git@github.com`
