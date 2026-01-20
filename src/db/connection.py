"""
Database connection utilities for cricket analytics project.
Uses psycopg3 (psycopg) for PostgreSQL connections.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

# Load environment variables from .env file
# This looks for .env in the project root
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)


def get_connection_string() -> str:
    """
    Build and return the database connection string.
    """
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "cricket")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "cricket123")
    
    return f"host={host} port={port} dbname={dbname} user={user} password={password}"


def get_connection():
    """
    Create and return a database connection.
    Uses environment variables for configuration.
    """
    return psycopg.connect(get_connection_string())


def get_connection_dict():
    """
    Returns connection with dictionary row factory (results as dicts instead of tuples).
    """
    return psycopg.connect(get_connection_string(), row_factory=dict_row)


def execute_query(query: str, params: tuple = None) -> list | None:
    """
    Execute a query and return results.
    
    Args:
        query: SQL query string
        params: Optional tuple of parameters for the query
    
    Returns:
        List of dicts for SELECT queries, None for INSERT/UPDATE/DELETE
    """
    with psycopg.connect(get_connection_string(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:  # SELECT query
                return cur.fetchall()
            conn.commit()  # INSERT/UPDATE/DELETE
            return None


def execute_many(query: str, params_list: list) -> None:
    """
    Execute a query multiple times with different parameters.
    Useful for bulk inserts.
    
    Args:
        query: SQL query string with placeholders
        params_list: List of tuples, each containing parameters for one execution
    """
    with psycopg.connect(get_connection_string()) as conn:
        with conn.cursor() as cur:
            cur.executemany(query, params_list)
        conn.commit()


def execute_sql_file(filepath: str) -> None:
    """
    Execute a SQL file.
    Useful for running migrations manually.
    
    Args:
        filepath: Path to the SQL file
    """
    with open(filepath, 'r') as f:
        sql = f.read()
    
    with psycopg.connect(get_connection_string()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    
    print(f"✅ Successfully executed: {filepath}")


# Quick test when running this file directly
if __name__ == "__main__":
    try:
        with get_connection() as conn:
            print("✅ Successfully connected to PostgreSQL!")
            
            # Test query
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                print(f"PostgreSQL version: {version[0]}")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")