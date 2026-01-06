# Cricket Analytics Project

A cross-platform cricket data analytics project using PostgreSQL and Python.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac/Windows/Linux)
- Python 3.10+ 
- Git

## Quick Start

### 1. Clone the repository

```bash
git clone git@github.com:YOUR_USERNAME/cricket-analytics.git
cd cricket-analytics
```

### 2. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your preferred settings
```

### 3. Start PostgreSQL and pgAdmin (Docker)

```bash
docker-compose up -d
```

### 4. Access pgAdmin (Database GUI)

Open http://localhost:8080 in your browser:
- **Email:** admin@cricket.local
- **Password:** admin123

The cricket database is pre-configured and ready to use!

### 5. Set up Python environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Test the connection

```bash
python src/db/connection.py
```

## Project Structure

```
cricket-analytics/
├── docker-compose.yml        # PostgreSQL + pgAdmin containers
├── postgresql.conf           # Database config with monitoring
├── pgadmin_servers.json      # Auto-configure pgAdmin connection
├── .env.example              # Environment variables template
├── .env                      # Your local config (git ignored)
├── requirements.txt          # Python dependencies
├── models/                   # pgModeler data models (.dbm files)
├── scripts/
│   └── export_db_objects.py  # Export DB objects to SQL files
├── src/
│   ├── db/
│   │   └── connection.py     # Database utilities
│   └── pipelines/
│       └── load_data.py      # Data loading scripts
├── sql/
│   ├── init/                 # Auto-run on first DB start
│   ├── migrations/           # Schema changes
│   ├── tables/               # Exported table schemas
│   ├── functions/            # Stored functions
│   ├── views/                # SQL views
│   ├── procedures/           # Stored procedures
│   └── triggers/             # Database triggers
├── notebooks/                # Jupyter notebooks
└── data/                     # Data files (git ignored)
```

## Monitoring

### In pgAdmin
1. Right-click on "Cricket Database" → "Dashboard"
2. View real-time stats: connections, transactions, queries

### Query Performance
```sql
-- View slowest queries
SELECT * FROM query_stats;

-- Reset statistics (start fresh)
SELECT pg_stat_statements_reset();
```

### Database Health
```sql
-- Table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Active connections
SELECT * FROM pg_stat_activity WHERE state = 'active';

-- Cache hit ratio (should be > 90%)
SELECT 
  sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

## SQL Workflow (Important!)

**⚠️ Always save SQL code in files, not just in pgAdmin!**

```bash
# Write SQL in sql/functions/my_function.sql, then run:
docker exec -i cricket_postgres psql -U postgres -d cricket < sql/functions/my_function.sql
```

This ensures your code is version controlled in Git.

## Common Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Connect to database via terminal
docker exec -it cricket_postgres psql -U postgres -d cricket

# Reset database (delete all data)
docker-compose down -v
docker-compose up -d

# Run a SQL file
docker exec -i cricket_postgres psql -U postgres -d cricket < sql/migrations/003_add_bowling_stats.sql
```

## Services

| Service | URL | Credentials |
|---------|-----|-------------|
| PostgreSQL | localhost:5432 | postgres / cricket123 |
| pgAdmin | http://localhost:8080 | admin@cricket.local / admin123 |

## Data Modeling with pgModeler

For visual database design, install pgModeler:

```bash
# Mac
brew install --cask pgmodeler

# Or download from https://pgmodeler.io/download
```

- Design tables visually with drag-and-drop
- See your entire schema as an ERD
- Export SQL to `sql/migrations/`
- Save models to `models/` folder

See **WORKFLOW_GUIDE.md** for complete workflow instructions.

## Saving Work to Git

| Created in... | How to save to Git |
|---------------|-------------------|
| pgModeler | Save .dbm to `models/`, export SQL to `sql/migrations/` |
| pgAdmin | Run `python scripts/export_db_objects.py --all` |
| SQL file | Already tracked - just commit |

See **WORKFLOW_GUIDE.md** for detailed workflow.
