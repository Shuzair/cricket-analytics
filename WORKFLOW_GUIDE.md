# Database Workflow Guide
## How to Save Your PostgreSQL Work to GitHub

This document explains the complete workflow for:
1. Visual data modeling with pgModeler
2. Saving pgAdmin work to git
3. Keeping everything version controlled

---

## Overview: What Gets Saved to Git

```
cricket-analytics/
├── models/                    ← pgModeler .dbm files (✅ saved to git)
│   └── cricket_model.dbm
├── sql/
│   ├── init/                  ← Auto-run on DB start (✅ saved to git)
│   ├── tables/                ← Table schemas (✅ saved to git)
│   ├── functions/             ← Functions (✅ saved to git)
│   ├── views/                 ← Views (✅ saved to git)
│   ├── procedures/            ← Stored procedures (✅ saved to git)
│   ├── triggers/              ← Triggers (✅ saved to git)
│   └── migrations/            ← Schema changes (✅ saved to git)
└── PostgreSQL Docker Volume   ← Actual data (❌ NOT saved to git)
```

---

## Part 1: pgModeler Setup

### What is pgModeler?
- Visual database design tool
- Create tables, relationships by drag-and-drop
- See your entire schema as an ERD (Entity Relationship Diagram)
- Export to SQL

### Install pgModeler

**Mac (Homebrew):**
```bash
brew install --cask pgmodeler
```

**Mac (Download):**
1. Go to https://pgmodeler.io/download
2. Download macOS version
3. Install the .dmg file

**Windows:**
1. Go to https://pgmodeler.io/download
2. Download Windows installer
3. Run the installer

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install pgmodeler

# Or download from website
```

### Configure pgModeler Connection

1. Open pgModeler
2. Go to **File → Connections**
3. Add new connection:
   - **Alias:** Cricket Local
   - **Host:** localhost
   - **Port:** 5432
   - **User:** postgres
   - **Password:** cricket123
   - **Database:** cricket

---

## Part 2: pgModeler Workflow

### Creating a New Model

1. **File → New Model**
2. Design your tables visually:
   - Drag "Table" from left panel
   - Add columns, set types, primary keys
   - Draw relationships between tables
3. **Save as:** `models/cricket_model.dbm`

### Exporting SQL from pgModeler

1. Design your model
2. **Export → Export to SQL file**
3. Save to: `sql/migrations/004_from_pgmodeler.sql` (use next number)
4. Review the generated SQL
5. Apply to database:
   ```bash
   docker exec -i cricket_postgres psql -U postgres -d cricket < sql/migrations/004_from_pgmodeler.sql
   ```

### Importing Existing Database into pgModeler

1. **File → Import**
2. Select your connection (Cricket Local)
3. pgModeler will reverse-engineer your database into a visual model
4. Save as: `models/cricket_model.dbm`

### pgModeler Git Workflow

```bash
# After making changes in pgModeler:

# 1. Save your .dbm file in models/ folder
# 2. Export SQL to sql/migrations/

# 3. Commit both
git add models/*.dbm
git add sql/migrations/*.sql
git commit -m "Update data model: added bowling_stats table"
git push
```

---

## Part 3: pgAdmin to Git Workflow

### The Problem
When you create a function/view in pgAdmin, it only exists in the database.
If you delete the Docker volume or move to another machine, it's **lost**.

### Solution: Export Script

I've created a script that exports your database objects to SQL files:

```bash
# Activate Python environment first
source venv/bin/activate

# Export everything (recommended after major changes)
python scripts/export_db_objects.py --all

# Export specific types
python scripts/export_db_objects.py --functions
python scripts/export_db_objects.py --views
python scripts/export_db_objects.py --tables

# Export specific object
python scripts/export_db_objects.py --function calculate_strike_rate
python scripts/export_db_objects.py --view player_summary
```

### Workflow A: Create in pgAdmin, Then Export

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Create function/view in pgAdmin                             │
│                    ↓                                            │
│  2. Test it, make sure it works                                 │
│                    ↓                                            │
│  3. Run: python scripts/export_db_objects.py --all              │
│                    ↓                                            │
│  4. Check sql/ folder - your SQL files are there                │
│                    ↓                                            │
│  5. git add . && git commit -m "Add new function" && git push   │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow B: Create in SQL File First (Recommended)

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Create SQL file: sql/functions/my_function.sql              │
│                    ↓                                            │
│  2. Write your SQL in the file                                  │
│                    ↓                                            │
│  3. Apply to database:                                          │
│     docker exec -i cricket_postgres psql -U postgres -d cricket │
│       < sql/functions/my_function.sql                           │
│                    ↓                                            │
│  4. Test in pgAdmin                                             │
│                    ↓                                            │
│  5. git add . && git commit && git push                         │
└─────────────────────────────────────────────────────────────────┘
```

**Why Workflow B is better:**
- SQL file exists from the start
- No risk of forgetting to export
- Easier to track changes in git history

---

## Part 4: Daily Workflow Summary

### Starting Your Day

```bash
# 1. Start Docker
docker-compose up -d

# 2. Activate Python
source venv/bin/activate

# 3. Open tools
open http://localhost:8080   # pgAdmin
open -a pgModeler            # pgModeler (Mac)
code .                       # VS Code
```

### When You Create Something New

| Created in... | Save to git by... |
|---------------|-------------------|
| pgModeler | Save .dbm to `models/`, export SQL to `sql/migrations/` |
| pgAdmin (function) | Run `python scripts/export_db_objects.py --functions` |
| pgAdmin (view) | Run `python scripts/export_db_objects.py --views` |
| pgAdmin (table) | Run `python scripts/export_db_objects.py --tables` |
| SQL file directly | Already in git! Just commit. |

### Before Pushing to Git

```bash
# Export any pgAdmin work to files
python scripts/export_db_objects.py --all

# Check what changed
git status
git diff

# Commit and push
git add .
git commit -m "Your descriptive message"
git push
```

### On a New Machine

```bash
# 1. Clone repo
git clone git@github.com:YOUR_USERNAME/cricket-analytics.git
cd cricket-analytics

# 2. Setup (as per SETUP_INSTRUCTIONS.md)
cp .env.example .env
docker-compose up -d

# 3. Database auto-creates with sql/init/ files

# 4. Apply any additional SQL files
for f in sql/tables/*.sql; do
  docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"
done

for f in sql/functions/*.sql; do
  docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"
done

for f in sql/views/*.sql; do
  docker exec -i cricket_postgres psql -U postgres -d cricket < "$f"
done

# 5. Open pgModeler and load models/cricket_model.dbm
```

---

## Part 5: Folder Structure Explained

```
sql/
├── init/                  # Runs AUTOMATICALLY on first docker-compose up
│   ├── 001_initial_schema.sql
│   └── 002_enable_monitoring.sql
│
├── migrations/            # Schema changes (run manually in order)
│   ├── 003_add_bowling_stats.sql
│   └── 004_from_pgmodeler.sql
│
├── tables/                # Exported table definitions
│   └── matches.sql
│
├── functions/             # Exported functions
│   └── calculate_strike_rate.sql
│
├── views/                 # Exported views
│   └── player_summary.sql
│
├── procedures/            # Exported stored procedures
│   └── update_stats.sql
│
└── triggers/              # Exported triggers
    └── audit_trigger.sql

models/
└── cricket_model.dbm      # pgModeler project file
```

---

## Quick Reference: Commands

```bash
# Export all DB objects to SQL files
python scripts/export_db_objects.py --all

# Run a SQL file against database
docker exec -i cricket_postgres psql -U postgres -d cricket < path/to/file.sql

# Connect to database CLI
docker exec -it cricket_postgres psql -U postgres -d cricket

# View what's in the database
\dt          # List tables
\df          # List functions
\dv          # List views
\d tablename # Describe table
```

---

## Summary

| Tool | Purpose | Git Files |
|------|---------|-----------|
| **pgModeler** | Visual data modeling | `models/*.dbm` + `sql/migrations/*.sql` |
| **pgAdmin** | Query, browse, quick edits | Export to `sql/` folder with script |
| **SQL files** | Version-controlled source of truth | `sql/**/*.sql` |
| **Python scripts** | Pipelines, data loading | `src/**/*.py` |

**Golden Rule:** If it's not in a file in your project folder, it won't go to GitHub!
