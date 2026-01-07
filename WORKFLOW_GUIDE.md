# Database Workflow Guide
## How to Save Your PostgreSQL & DBeaver Work to GitHub

This document explains the complete workflow for:
1. Visual data modeling with DBeaver
2. Saving your database work to git
3. Keeping everything version controlled

---

## Overview: What Gets Saved to Git

```
cricket-analytics/
├── models/                    ← DBeaver ERD files (✅ saved to git)
│   └── cricket_erd.png
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

## The Golden Rule

**If it's not in a file in your project folder, it won't go to GitHub!**

When you create something in DBeaver (function, view, table), it lives in the database — NOT in your project folder. You must export it to a SQL file.

---

## Part 1: DBeaver ERD (Visual Data Modeling)

### Creating an ERD from Existing Tables

1. In DBeaver, expand: `cricket` → `Schemas` → `public` → `Tables`
2. Select all tables you want (Ctrl+Click or Cmd+Click)
3. Right-click → **View Diagram**
4. Your ERD appears!

### Creating a New ERD Design

1. Right-click on `cricket` database
2. **Create → ER Diagram**
3. Name it (e.g., "Cricket Data Model")
4. Drag tables from left panel onto canvas
5. Or create new tables visually:
   - Right-click on canvas → **Create New Table**
   - Add columns, set types, primary keys
   - Draw relationships by dragging from one column to another

### Saving ERD to Git

**Option 1: Export as Image**
1. In ERD view, click **File → Save As** or right-click → **Export**
2. Save as PNG/SVG to: `models/cricket_erd.png`
3. Good for documentation

**Option 2: Export as SQL (Recommended)**
1. In ERD view, right-click → **Generate SQL**
2. Save to: `sql/migrations/XXX_from_dbeaver.sql`
3. This is the actual code that creates your tables

**Option 3: Save DBeaver Project File**
1. DBeaver saves `.erd` files in its workspace
2. Find via: **Window → Preferences → General → Workspace**
3. Copy `.erd` file to `models/` folder

### ERD Git Workflow

```bash
# After designing in DBeaver:

# 1. Export SQL to migrations folder
# 2. Export image to models folder (optional, for docs)

git add sql/migrations/*.sql
git add models/*.png
git commit -m "Add new data model: player statistics"
git push
```

---

## Part 2: Saving DBeaver SQL Work to Git

### The Problem

When you create a function/view in DBeaver, it only exists in the database.
If you delete the Docker volume or move to another machine, it's **lost**.

### Solution: Export Script

Use the included Python script to export database objects:

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

### Workflow A: Create in DBeaver, Then Export

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Create function/view/table in DBeaver                       │
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
│  2. Write your SQL in the file (use VS Code or DBeaver editor)  │
│                    ↓                                            │
│  3. Run the file in DBeaver:                                    │
│     - Open SQL file in DBeaver                                  │
│     - Click Execute (Ctrl+Enter)                                │
│                    ↓                                            │
│  4. Test in DBeaver                                             │
│                    ↓                                            │
│  5. git add . && git commit && git push                         │
└─────────────────────────────────────────────────────────────────┘
```

**Why Workflow B is better:**
- SQL file exists from the start
- No risk of forgetting to export
- Easier to track changes in git history

### Alternative: Export Directly from DBeaver

You can also export SQL directly from DBeaver:

**Export a single function/view:**
1. In left panel, find your function under `cricket` → `Schemas` → `public` → `Functions`
2. Right-click → **Generate SQL** → **DDL**
3. Copy the SQL
4. Paste into a file: `sql/functions/my_function.sql`

**Export entire schema:**
1. Right-click on `public` schema
2. **Generate SQL** → **DDL**
3. Save to `sql/schema_backup.sql`

---

## Part 3: Daily Workflow Summary

### Starting Your Day

```bash
# 1. Start Docker
docker-compose up -d

# 2. Activate Python
source venv/bin/activate

# 3. Open tools
open -a DBeaver       # Mac
# Or just launch DBeaver from Applications

code .                # VS Code
```

### When You Create Something New

| Created in... | Save to git by... |
|---------------|-------------------|
| DBeaver ERD | Export SQL → `sql/migrations/`, Image → `models/` |
| DBeaver (function) | Run `python scripts/export_db_objects.py --functions` |
| DBeaver (view) | Run `python scripts/export_db_objects.py --views` |
| DBeaver (table) | Run `python scripts/export_db_objects.py --tables` |
| SQL file directly | Already in git! Just commit. |

### Before Pushing to Git

```bash
# Export any DBeaver work to files
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

# 5. Open DBeaver and connect to see everything
```

---

## Part 4: Folder Structure Explained

```
sql/
├── init/                  # Runs AUTOMATICALLY on first docker-compose up
│   ├── 001_initial_schema.sql
│   └── 002_enable_monitoring.sql
│
├── migrations/            # Schema changes (run manually in order)
│   ├── 003_add_bowling_stats.sql
│   └── 004_from_dbeaver_erd.sql
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
├── cricket_erd.png        # ERD diagram image (for documentation)
└── cricket_model.erd      # DBeaver ERD project file (optional)
```

---

## Part 5: Quick Reference Commands

```bash
# Export all DB objects to SQL files
python scripts/export_db_objects.py --all

# Run a SQL file against database
docker exec -i cricket_postgres psql -U postgres -d cricket < path/to/file.sql

# Run SQL file from DBeaver:
# Open file → Ctrl+Enter (or Cmd+Enter on Mac)

# Connect to database CLI
docker exec -it cricket_postgres psql -U postgres -d cricket

# View what's in the database (in psql)
\dt          # List tables
\df          # List functions
\dv          # List views
\d tablename # Describe table

# Reset database (fresh start)
docker-compose down -v
docker-compose up -d
```

---

## Part 6: DBeaver Tips

### Run SQL File
1. Open `.sql` file in DBeaver
2. Make sure connection is selected (top dropdown)
3. Press `Ctrl+Enter` (Windows/Linux) or `Cmd+Enter` (Mac)

### View Table Data
1. Double-click on table in left panel
2. Go to **Data** tab

### Edit Table Structure
1. Right-click table → **View Table** (or double-click)
2. Go to **Properties** tab
3. Modify columns, add constraints
4. Click **Save** → DBeaver generates ALTER statements

### Compare Databases
1. **Database → Compare/Migrate**
2. Useful for seeing differences between your local and a colleague's

### Export Query Results
1. Run a query
2. Right-click on results → **Export Data**
3. Choose format (CSV, Excel, SQL INSERTs, etc.)

---

## Summary

| Task | Tool | Git Files |
|------|------|-----------|
| Visual data modeling | DBeaver ERD | `models/` + `sql/migrations/` |
| Create functions/views | DBeaver SQL Editor | Export to `sql/` folder |
| Browse data | DBeaver | N/A (data isn't in git) |
| Run pipelines | Python | `src/**/*.py` |
| Version control | Git | Everything in project folder |

**Remember:** Database = temporary (in Docker). SQL files = permanent (in Git).
