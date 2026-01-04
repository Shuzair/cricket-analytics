# Cricket Analytics Project

A cross-platform cricket data analytics project using PostgreSQL and Python.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac/Windows/Linux)
- Python 3.10+ 
- Git

## Quick Start

### 1. Clone the repository

```bash
git clone git@github-personal:YOUR_USERNAME/cricket-analytics.git
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

### 4. Set up Python environment

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

### 5. Test the connection

```bash
python src/db/connection.py
```

### 6. Load sample data

```bash
python src/pipelines/load_data.py
```

## Project Structure

```
cricket-analytics/
├── docker-compose.yml      # PostgreSQL container config
├── .env.example            # Environment variables template
├── .env                    # Your local config (git ignored)
├── requirements.txt        # Python dependencies
├── src/
│   ├── db/
│   │   └── connection.py   # Database utilities
│   └── pipelines/
│       └── load_data.py    # Data loading scripts
├── sql/
│   └── init/               # SQL migrations (auto-run on first start)
├── notebooks/              # Jupyter notebooks for exploration
└── data/                   # Data files (git ignored)
```

## Common Commands

```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# View logs
docker-compose logs -f

# Connect to database directly
docker exec -it cricket_postgres psql -U postgres -d cricket

# Reset database (delete all data)
docker-compose down -v
docker-compose up -d
```

## Adding New Tables

1. Create a new SQL file in `sql/init/` (e.g., `002_new_tables.sql`)
2. Either:
   - Reset the database: `docker-compose down -v && docker-compose up -d`
   - Or run manually: `docker exec -i cricket_postgres psql -U postgres -d cricket < sql/init/002_new_tables.sql`

## Notes

- Database data persists in a Docker volume (survives restarts)
- The `.env` file is git-ignored for security
- SQL files in `sql/init/` run automatically on first database start
