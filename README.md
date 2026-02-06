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

---

## Step 1: Clone the Repository

```bash
# Go to where you want the project
cd ~

# Clone the repo (replace YOUR_USERNAME)
git clone git@github.com:YOUR_USERNAME/cricket-analytics.git

# Enter the folder
cd cricket-analytics
```

---

## Step 2: Configure Git Identity (Optional)

If this is a personal project on a work machine:

```bash
cd cricket-analytics
git config user.name "Your Name"
git config user.email "your.personal.email@gmail.com"
```

This sets your identity for this repo only.

---

## Step 3: Set Up Environment File

```bash
cp .env.example .env
```

Edit `.env` if you want to change the default database password.

---

## Step 4: Start PostgreSQL (Docker)

### 4.1 Start Docker Desktop

Make sure Docker Desktop is running (open the app).

### 4.2 Start the Database

```bash
docker-compose up -d
```

### 4.3 Verify It's Running

```bash
docker ps
```

You should see `cricket_postgres` in the list.

---

## Step 5: Set Up Python Environment

### Mac/Linux:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Windows (PowerShell):

```powershell
# Create virtual environment
python -m venv venv

# Activate it (Option A - recommended)
.\venv\Scripts\Activate.bat

# OR if that doesn't work, enable scripts first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Windows (Command Prompt):

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 6: Test the Connection

```bash
python src/db/connection.py
```

✅ Success: `Successfully connected to PostgreSQL!`

---

## Step 7: Set Up Your SQL IDE

Connect your preferred SQL IDE (DBeaver, pgAdmin, DataGrip, etc.) with these settings:

| Setting | Value |
|---------|-------|
| Host | `localhost` |
| Port | `5432` |
| Database | `cricket` |
| User | `postgres` |
| Password | `cricket123` (or your .env value) |

---

## Setup Complete! 🎉

Your environment is ready:
- ✅ PostgreSQL running in Docker
- ✅ Python environment configured
- ✅ Connected to GitHub

---

# PART 2: WORKFLOW

## Project Structure Overview

```
cricket-analytics/
├── sql/
│   ├── init/           # Auto-runs on first DB start
│   ├── migrations/     # Schema changes
│   ├── tables/         # Table definitions
│   ├── functions/      # Stored functions
│   ├── views/          # SQL views
│   ├── procedures/     # Stored procedures
│   └── triggers/       # Database triggers
├── models/             # ERD diagrams and exports
├── src/                # Python code
├── scripts/            # Utility scripts
├── data/               # Data files (git ignored)
└── notebooks/          # Jupyter notebooks
```

---

## The Golden Rule

> **If it's not in a file in your project folder, it won't go to GitHub.**

When you create something in your SQL IDE (function, view, table), it lives in the database only. You must save it to a `.sql` file.

---

## Daily Workflow

### Starting Your Day

**Mac/Linux:**
```bash
# 1. Start Docker (if not running)
docker-compose up -d

# 2. Activate Python environment
source venv/bin/activate

# 3. Open your SQL IDE and connect
```

**Windows:**
```powershell
# 1. Start Docker (if not running)
docker-compose up -d

# 2. Activate Python environment
.\venv\Scripts\Activate.bat

# 3. Open your SQL IDE and connect
```

---

## How to Save SQL Work to Git

### Understanding the Database Structure

By default, PostgreSQL uses a schema called `public`. Think of schemas as folders inside your database that organize tables, functions, and views.

```
Database: cricket
└── Schema: public (default)
    ├── Tables
    ├── Functions
    └── Views
```

If you create custom schemas (e.g., `analytics`, `staging`, `raw_data`), your structure becomes:

```
Database: cricket
├── Schema: public
│   └── (default tables)
├── Schema: analytics
│   ├── Tables
│   └── Views
├── Schema: staging
│   └── Tables
└── Schema: raw_data
    └── Tables
```

---

### Method A: Write SQL Files First (Recommended)

This is the safest approach — your work is always in Git from the start.

**1. Create a SQL file:**

```bash
# Create a new file for your function
touch sql/functions/calculate_average.sql
```

**What this does:** Creates an empty file named `calculate_average.sql` in the `sql/functions/` folder. This file will be tracked by Git.

**2. Write your SQL in the file:**

```sql
-- sql/functions/calculate_average.sql
-- This function calculates batting average
-- Formula: runs / (innings - not_outs)

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

**3. Run the file to load into database:**

**Option A — From terminal:**

```bash
docker exec -i cricket_postgres psql -U postgres -d cricket < sql/functions/calculate_average.sql
```

**Breaking down this command:**
| Part | What it does |
|------|--------------|
| `docker exec` | Run a command inside a Docker container |
| `-i` | Interactive mode (allows input from file) |
| `cricket_postgres` | Name of your PostgreSQL container |
| `psql` | PostgreSQL command-line tool |
| `-U postgres` | Connect as user "postgres" |
| `-d cricket` | Connect to database "cricket" |
| `< sql/functions/calculate_average.sql` | Feed this SQL file as input |

**Option B — From your SQL IDE:**
- Open the `.sql` file in your IDE
- Connect to the database
- Execute it (usually `Ctrl+Enter` or `Cmd+Enter`)

**4. Test it in your SQL IDE:**

```sql
SELECT calculate_batting_average(500, 10, 2);
-- Should return: 62.50
```

**5. Commit to Git:**

```bash
git add sql/functions/calculate_average.sql
git commit -m "Add batting average function"
git push
```

**Breaking down these commands:**
| Command | What it does |
|---------|--------------|
| `git add sql/functions/calculate_average.sql` | Stage this specific file for commit |
| `git commit -m "Add batting average function"` | Save the staged changes with a message |
| `git push` | Upload your commits to GitHub |

---

### Method B: Create in SQL IDE, Then Export

If you prefer designing in your IDE first, you'll need to export your work to files.

**1. Create your function/view/table in the SQL IDE**

Write and execute your SQL directly in the IDE.

**2. Export to a file using the script:**

```bash
# Make sure venv is activated first
source venv/bin/activate  # Mac/Linux
.\venv\Scripts\Activate.bat  # Windows

# Export all database objects to SQL files
python scripts/export_db_objects.py --all
```

**What this does:** The script connects to your database, reads all functions/views/tables, and writes them to `.sql` files in the appropriate folders.

**Export specific types only:**

```bash
# Export only functions
python scripts/export_db_objects.py --functions

# Export only views
python scripts/export_db_objects.py --views

# Export only table schemas (structure, not data)
python scripts/export_db_objects.py --tables

# Export a specific function by name
python scripts/export_db_objects.py --function calculate_batting_average

# Export a specific view by name
python scripts/export_db_objects.py --view player_summary
```

**3. Check the exported files:**

```bash
ls sql/functions/   # List all exported functions
ls sql/views/       # List all exported views
ls sql/tables/      # List all exported table schemas
```

**4. Commit to Git:**

```bash
git add .                              # Stage all changes
git commit -m "Export database objects" # Commit with message
git push                               # Push to GitHub
```

---

### Working with Custom Schemas

If you create your own schemas instead of using the default `public` schema, you need to organize your files and commands accordingly.

#### Directory Structure for Custom Schemas

```
sql/
├── schemas/                    # Schema creation scripts
│   ├── create_analytics.sql
│   ├── create_staging.sql
│   └── create_raw_data.sql
├── analytics/                  # Objects in 'analytics' schema
│   ├── tables/
│   ├── functions/
│   └── views/
├── staging/                    # Objects in 'staging' schema
│   ├── tables/
│   └── functions/
├── raw_data/                   # Objects in 'raw_data' schema
│   └── tables/
└── public/                     # Objects in default 'public' schema
    ├── tables/
    ├── functions/
    └── views/
```

#### Creating a Schema

**sql/schemas/create_analytics.sql:**
```sql
-- Create the analytics schema
-- This schema holds all analytical views and functions

CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant usage to postgres user
GRANT ALL ON SCHEMA analytics TO postgres;

-- Set comment for documentation
COMMENT ON SCHEMA analytics IS 'Schema for analytical views and reporting functions';
```

**Run it:**
```bash
docker exec -i cricket_postgres psql -U postgres -d cricket < sql/schemas/create_analytics.sql
```

#### Creating Objects in Custom Schemas

When creating objects in a custom schema, you must specify the schema name:

**sql/analytics/functions/calculate_team_stats.sql:**
```sql
-- Function in the 'analytics' schema
-- Note: schema_name.function_name

CREATE OR REPLACE FUNCTION analytics.calculate_team_stats(
    p_team_name VARCHAR
)
RETURNS TABLE (
    total_matches INTEGER,
    wins INTEGER,
    losses INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_matches,
        COUNT(*) FILTER (WHERE winner = p_team_name)::INTEGER as wins,
        COUNT(*) FILTER (WHERE winner != p_team_name)::INTEGER as losses
    FROM public.matches
    WHERE team_1 = p_team_name OR team_2 = p_team_name;
END;
$$ LANGUAGE plpgsql;
```

**sql/analytics/views/team_summary.sql:**
```sql
-- View in the 'analytics' schema

CREATE OR REPLACE VIEW analytics.team_summary AS
SELECT 
    team_name,
    COUNT(*) as matches_played,
    SUM(wins) as total_wins
FROM public.matches
GROUP BY team_name;
```

#### Running Custom Schema Files

The command structure stays the same, just use the correct file path:

```bash
# Run a function in analytics schema
docker exec -i cricket_postgres psql -U postgres -d cricket < sql/analytics/functions/calculate_team_stats.sql

# Run a view in analytics schema
docker exec -i cricket_postgres psql -U postgres -d cricket < sql/analytics/views/team_summary.sql

# Run all files in analytics/functions folder (Mac/Linux)
for f in sql/analytics/functions/*.sql; do
  echo "Running $f..."
  docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"
done
```

#### Querying Objects in Custom Schemas

```sql
-- Must include schema name when querying
SELECT * FROM analytics.team_summary;
SELECT analytics.calculate_team_stats('India');

-- Or set search path to include your schema
SET search_path TO analytics, public;
SELECT * FROM team_summary;  -- Now works without schema prefix
```

#### Setting Default Search Path

If you want to avoid typing schema names every time, set the search path in your session or permanently:

**Per session (in SQL IDE):**
```sql
SET search_path TO analytics, staging, public;
```

**Permanently for the database:**
```sql
ALTER DATABASE cricket SET search_path TO analytics, staging, public;
```

---

### Summary: Where to Save What

| What you create | Where to save | Example path |
|-----------------|---------------|--------------|
| Schema creation | `sql/schemas/` | `sql/schemas/create_analytics.sql` |
| Table (public) | `sql/tables/` | `sql/tables/matches.sql` |
| Table (custom schema) | `sql/{schema}/tables/` | `sql/analytics/tables/stats.sql` |
| Function (public) | `sql/functions/` | `sql/functions/calc_average.sql` |
| Function (custom schema) | `sql/{schema}/functions/` | `sql/analytics/functions/calc_stats.sql` |
| View (public) | `sql/views/` | `sql/views/player_summary.sql` |
| View (custom schema) | `sql/{schema}/views/` | `sql/analytics/views/team_summary.sql` |
| Schema changes | `sql/migrations/` | `sql/migrations/004_add_index.sql` |

---

## SQL File Organization

### Default Structure (Using Public Schema)

| Type | Location | When to Use |
|------|----------|-------------|
| Initial schema | `sql/init/` | Tables/setup that run on first DB start |
| Schema changes | `sql/migrations/` | Adding/altering tables after initial setup |
| Table definitions | `sql/tables/` | Exported table schemas |
| Functions | `sql/functions/` | Stored functions |
| Views | `sql/views/` | SQL views |
| Procedures | `sql/procedures/` | Stored procedures |
| Triggers | `sql/triggers/` | Database triggers |

### With Custom Schemas

| Type | Location | Example |
|------|----------|---------|
| Schema creation | `sql/schemas/` | `sql/schemas/create_analytics.sql` |
| Tables in custom schema | `sql/{schema_name}/tables/` | `sql/analytics/tables/` |
| Functions in custom schema | `sql/{schema_name}/functions/` | `sql/analytics/functions/` |
| Views in custom schema | `sql/{schema_name}/views/` | `sql/analytics/views/` |

---

## Naming Conventions

### Migrations (run in order)
```
sql/migrations/
├── 001_initial_schema.sql
├── 002_add_player_stats.sql
├── 003_add_indexes.sql
└── 004_add_bowling_tables.sql
```

### Functions/Views (by name)
```
sql/functions/
├── calculate_strike_rate.sql
├── calculate_batting_average.sql
└── get_player_stats.sql

sql/views/
├── player_summary.sql
├── match_summary.sql
└── team_standings.sql
```

---

## Running SQL Files

### Understanding the Command

The basic command to run a SQL file:

```bash
docker exec -i cricket_postgres psql -U postgres -d cricket < path/to/file.sql
```

| Part | Meaning |
|------|---------|
| `docker exec` | Execute a command inside a running container |
| `-i` | Interactive mode — allows piping input from a file |
| `cricket_postgres` | The name of your PostgreSQL container (from docker-compose.yml) |
| `psql` | PostgreSQL's command-line interface |
| `-U postgres` | Username to connect as |
| `-d cricket` | Database name to connect to |
| `< path/to/file.sql` | Redirect the file contents as input |

### Single File

**Mac/Linux:**
```bash
docker exec -i cricket_postgres psql -U postgres -d cricket < sql/functions/my_function.sql
```

**Windows (PowerShell):**
```powershell
Get-Content sql/functions/my_function.sql | docker exec -i cricket_postgres psql -U postgres -d cricket
```

**Why different?** PowerShell doesn't support `<` for input redirection the same way. `Get-Content` reads the file and `|` pipes it to the command.

**Windows (Command Prompt):**
```cmd
docker exec -i cricket_postgres psql -U postgres -d cricket < sql/functions/my_function.sql
```

### All Files in a Folder

**Mac/Linux:**
```bash
for f in sql/functions/*.sql; do
  echo "Running $f..."
  docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"
done
```

**What this does:**
1. `for f in sql/functions/*.sql` — Loop through all `.sql` files in the folder
2. `echo "Running $f..."` — Print which file is being executed
3. `docker exec ... < "$f"` — Run each file against the database
4. `done` — End the loop

**Windows (PowerShell):**
```powershell
Get-ChildItem sql/functions/*.sql | ForEach-Object {
    Write-Host "Running $_..."
    Get-Content $_.FullName | docker exec -i cricket_postgres psql -U postgres -d cricket
}
```

### Running Files for Custom Schemas

If you have custom schemas, use the same commands with the appropriate path:

```bash
# Run all files in analytics schema's functions folder
for f in sql/analytics/functions/*.sql; do
  echo "Running $f..."
  docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"
done

# Run all files in staging schema's tables folder
for f in sql/staging/tables/*.sql; do
  echo "Running $f..."
  docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"
done
```

---

## Git Workflow

### Understanding Git Commands

| Command | What it does |
|---------|--------------|
| `git status` | Shows which files have been changed/added/deleted |
| `git diff` | Shows the actual changes in files (line by line) |
| `git add .` | Stages ALL changed files for commit |
| `git add <file>` | Stages a specific file for commit |
| `git commit -m "message"` | Saves staged changes with a description |
| `git push` | Uploads your commits to GitHub |
| `git pull` | Downloads latest changes from GitHub |

### Before You Start Working

Always pull latest changes to avoid conflicts:
```bash
git pull
```

**What this does:** Downloads any changes made by you (on another machine) or collaborators since your last pull.

### After Making Changes

```bash
# 1. See what changed
git status
```
This shows:
- Red files = changed but not staged
- Green files = staged and ready to commit
- Untracked files = new files not yet added to Git

```bash
# 2. Review actual changes (optional but recommended)
git diff
```
Shows line-by-line what was added (+) and removed (-).

```bash
# 3. Export any IDE work (if you used Method B)
python scripts/export_db_objects.py --all
```

```bash
# 4. Stage changes
git add .                    # Stage everything
# OR
git add sql/functions/       # Stage only the functions folder
# OR
git add sql/functions/my_function.sql  # Stage one specific file
```

```bash
# 5. Commit with a clear message
git commit -m "Add player statistics functions"
```

```bash
# 6. Push to GitHub
git push
```

### Good Commit Messages

```bash
# ✅ Good
git commit -m "Add calculate_strike_rate function"
git commit -m "Create player_summary view"
git commit -m "Add indexes to matches table"
git commit -m "Fix batting average calculation for not-outs"

# ❌ Bad
git commit -m "update"
git commit -m "changes"
git commit -m "fix"
```

---

## Setting Up on a New Machine

When you clone the repo on a different computer:

```bash
# 1. Clone
git clone git@github.com:YOUR_USERNAME/cricket-analytics.git
cd cricket-analytics

# 2. Set up environment
cp .env.example .env
docker-compose up -d

# 3. Set up Python
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

# 4. Database auto-creates with sql/init/ files

# 5. Apply additional SQL files (migrations, functions, etc.)
# Mac/Linux:
for f in sql/migrations/*.sql; do docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"; done
for f in sql/functions/*.sql; do docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"; done
for f in sql/views/*.sql; do docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"; done
```

---

## Useful Commands Reference

### Docker

| Task | Command |
|------|---------|
| Start database | `docker-compose up -d` |
| Stop database | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Restart database | `docker-compose restart` |
| Reset database (delete all data) | `docker-compose down -v && docker-compose up -d` |

### Database CLI

```bash
# Connect to PostgreSQL CLI
docker exec -it cricket_postgres psql -U postgres -d cricket

# Inside psql:
\dt          # List tables
\df          # List functions
\dv          # List views
\d tablename # Describe table
\q           # Quit
```

### Python

| Task | Mac/Linux | Windows |
|------|-----------|---------|
| Activate venv | `source venv/bin/activate` | `.\venv\Scripts\Activate.bat` |
| Deactivate venv | `deactivate` | `deactivate` |
| Test DB connection | `python src/db/connection.py` | `python src/db/connection.py` |
| Export DB objects | `python scripts/export_db_objects.py --all` | `python scripts/export_db_objects.py --all` |

### Git

| Task | Command |
|------|---------|
| Check status | `git status` |
| Pull latest | `git pull` |
| Stage all changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push` |
| View history | `git log --oneline` |

---

## Troubleshooting

### Docker not starting
- Make sure Docker Desktop is open and running
- Try: `docker-compose down && docker-compose up -d`

### Can't connect to database
- Check container is running: `docker ps`
- Check logs: `docker-compose logs postgres`
- Verify port 5432 is not used by another app

### Python venv won't activate (Windows)
- Use `.\venv\Scripts\Activate.bat` instead
- Or enable scripts: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Or use Command Prompt instead of PowerShell

### Permission denied (Git)
- Make sure SSH key is added to GitHub: https://github.com/settings/keys
- Test with: `ssh -T git@github.com`

### "Module not found" in Python
- Make sure venv is activated (you should see `(venv)` in terminal)
- Reinstall: `pip install -r requirements.txt`

---

## Summary

### Setup (One Time)
1. Install prerequisites (Git, Docker, Python)
2. Set up SSH key and add to GitHub
3. Clone the repository
4. Run `docker-compose up -d`
5. Set up Python venv and install dependencies
6. Connect your SQL IDE

### Daily Workflow
1. Start Docker: `docker-compose up -d`
2. Activate venv: `source venv/bin/activate`
3. Pull latest: `git pull`
4. Do your work (write SQL in files or export from IDE)
5. Commit and push: `git add . && git commit -m "message" && git push`

### Remember
- **Write SQL in files** → automatically tracked in Git
- **Create in IDE** → must export with `python scripts/export_db_objects.py --all`
- **Always commit** your `.sql` files to keep everything version controlled