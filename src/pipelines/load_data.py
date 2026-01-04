"""
Sample data pipeline for cricket analytics.
This demonstrates how to load data into PostgreSQL.
"""

import pandas as pd
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.connection import get_connection


def load_sample_data():
    """
    Load sample cricket data into the database.
    Replace this with your actual data loading logic.
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # Sample data - replace with your actual data source
    sample_matches = [
        ('2024-01-15', 'Mumbai', 'India', 'Australia', 'India', 'ODI'),
        ('2024-01-18', 'Sydney', 'Australia', 'India', 'Australia', 'ODI'),
        ('2024-01-21', 'Melbourne', 'Australia', 'India', 'India', 'ODI'),
    ]
    
    insert_query = """
        INSERT INTO matches (match_date, venue, team_1, team_2, winner, match_type)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """
    
    for match in sample_matches:
        cur.execute(insert_query, match)
    
    conn.commit()
    print(f"✅ Loaded {len(sample_matches)} sample matches")
    
    cur.close()
    conn.close()


def load_from_csv(filepath: str, table_name: str):
    """
    Load data from a CSV file into a table.
    
    Args:
        filepath: Path to CSV file
        table_name: Target table name
    """
    df = pd.read_csv(filepath)
    
    conn = get_connection()
    
    # Using pandas to_sql for convenience
    from sqlalchemy import create_engine
    import os
    
    engine = create_engine(
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', 'cricket123')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'cricket')}"
    )
    
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"✅ Loaded {len(df)} rows into {table_name}")


if __name__ == "__main__":
    print("Running sample data load...")
    load_sample_data()
