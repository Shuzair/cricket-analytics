"""
Database connection utilities for cricket analytics project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables from .env file
# This looks for .env in the project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


def get_connection():
    """
    Create and return a database connection.
    Uses environment variables for configuration.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "cricket"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "cricket123")
    )


def get_connection_dict_cursor():
    """
    Returns connection with dictionary cursor (results as dicts instead of tuples).
    """
    conn = get_connection()
    return conn, conn.cursor(cursor_factory=RealDictCursor)


def execute_query(query: str, params: tuple = None):
    """
    Execute a query and return results.
    """
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            if cur.description:  # SELECT query
                return cur.fetchall()
            conn.commit()  # INSERT/UPDATE/DELETE
            return None
    finally:
        conn.close()


def execute_sql_file(filepath: str):
    """
    Execute a SQL file.
    Useful for running migrations manually.
    """
    with open(filepath, 'r') as f:
        sql = f.read()
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
        print(f"Successfully executed: {filepath}")
    finally:
        conn.close()


# Quick test when running this file directly
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("✅ Successfully connected to PostgreSQL!")
        
        # Test query
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")
