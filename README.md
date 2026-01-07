# Cricket Analytics Project

A cross-platform cricket data analytics project using PostgreSQL and Python.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac/Windows/Linux)
- [DBeaver](https://dbeaver.io/download/) (Free database GUI + visual modeling)
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

### 3. Start PostgreSQL (Docker)

```bash
docker-compose up -d
```

### 4. Install DBeaver

| OS | Command |
|----|---------|
| Mac | `brew install --cask dbeaver-community` |
| Windows | `choco install dbeaver` or download from website |
| Linux | `sudo snap install dbeaver-ce` |

### 5. Connect DBeaver to Database

1. Open DBeaver
2. **Database → New Connection → PostgreSQL**
3. Enter:
   - Host: `localhost`
   - Port: `5432`
   - Database: `cricket`
   - User: `postgres`
   - Password: `cricket123`
4. Test Connection → Finish

### 6. Set up Python environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 7. Test the connection

```bash
python src/db/connection.py
```

## Project Structure

```
cricket-analytics/
├── docker-compose.yml        # PostgreSQL container
├── postgresql.conf           # Database config with monitoring
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
├── models/                   # DBeaver ERD exports
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

## DBeaver Features

### View ERD (Visual Data Model)
1. Expand `cricket` → `Schemas` → `public` → `Tables`
2. Select tables → Right-click → **View Diagram**

### Create ERD
1. Right-click database → **Create → ER Diagram**
2. Drag tables or create new ones visually

### Run SQL Files
1. Open `.sql` file in DBeaver
2. Press `Ctrl+Enter` (or `Cmd+Enter` on Mac)

## Saving Work to Git

| Created in... | How to save to Git |
|---------------|-------------------|
| DBeaver ERD | Export SQL → `sql/migrations/`, Image → `models/` |
| DBeaver (function/view) | Run `python scripts/export_db_objects.py --all` |
| SQL file directly | Already tracked - just commit |

See **WORKFLOW_GUIDE.md** for detailed workflow.

## Monitoring

### Query Performance
```sql
-- View slowest queries
SELECT * FROM query_stats;
```

### Database Health
```sql
-- Table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Active connections
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

## Common Commands

```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# View logs
docker-compose logs -f

# Connect via terminal
docker exec -it cricket_postgres psql -U postgres -d cricket

# Reset database (delete all data)
docker-compose down -v
docker-compose up -d

# Export DB objects to SQL files
python scripts/export_db_objects.py --all

# Run a SQL file
docker exec -i cricket_postgres psql -U postgres -d cricket < sql/migrations/003_add_bowling_stats.sql
```

## Connection Details

| Setting | Value |
|---------|-------|
| Host | localhost |
| Port | 5432 |
| Database | cricket |
| User | postgres |
| Password | cricket123 (or your .env value) |
