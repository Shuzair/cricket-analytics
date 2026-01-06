#!/usr/bin/env python3
"""
Database Export Tool
====================
Export database objects (functions, views, tables, etc.) to SQL files for version control.

Usage:
    python scripts/export_db_objects.py --all              # Export everything
    python scripts/export_db_objects.py --functions        # Export all functions
    python scripts/export_db_objects.py --views            # Export all views
    python scripts/export_db_objects.py --tables           # Export table schemas
    python scripts/export_db_objects.py --function my_func # Export specific function
    python scripts/export_db_objects.py --view my_view     # Export specific view
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from db.connection import get_connection

# Output directories
SQL_DIR = Path(__file__).parent.parent / 'sql'
FUNCTIONS_DIR = SQL_DIR / 'functions'
VIEWS_DIR = SQL_DIR / 'views'
TABLES_DIR = SQL_DIR / 'tables'
PROCEDURES_DIR = SQL_DIR / 'procedures'
TRIGGERS_DIR = SQL_DIR / 'triggers'


def ensure_dirs():
    """Create output directories if they don't exist."""
    for dir_path in [FUNCTIONS_DIR, VIEWS_DIR, TABLES_DIR, PROCEDURES_DIR, TRIGGERS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)


def get_header(object_type: str, object_name: str) -> str:
    """Generate a header comment for exported SQL files."""
    return f"""-- {object_type}: {object_name}
-- Exported from database: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- 
-- To apply this to database:
-- docker exec -i cricket_postgres psql -U postgres -d cricket < sql/{object_type.lower()}s/{object_name}.sql
--

"""


def export_functions(conn, specific_name: str = None):
    """Export functions from database to SQL files."""
    cur = conn.cursor()
    
    if specific_name:
        cur.execute("""
            SELECT proname, pg_get_functiondef(oid) as definition
            FROM pg_proc
            WHERE pronamespace = 'public'::regnamespace
            AND proname = %s
        """, (specific_name,))
    else:
        cur.execute("""
            SELECT proname, pg_get_functiondef(oid) as definition
            FROM pg_proc
            WHERE pronamespace = 'public'::regnamespace
            AND prokind = 'f'
        """)
    
    functions = cur.fetchall()
    
    if not functions:
        print("No functions found to export.")
        return
    
    for func_name, definition in functions:
        filepath = FUNCTIONS_DIR / f"{func_name}.sql"
        content = get_header("Function", func_name)
        content += f"DROP FUNCTION IF EXISTS {func_name} CASCADE;\n\n"
        content += definition + ";\n"
        
        filepath.write_text(content)
        print(f"✅ Exported function: {filepath}")
    
    cur.close()


def export_views(conn, specific_name: str = None):
    """Export views from database to SQL files."""
    cur = conn.cursor()
    
    if specific_name:
        cur.execute("""
            SELECT viewname, definition
            FROM pg_views
            WHERE schemaname = 'public'
            AND viewname = %s
        """, (specific_name,))
    else:
        cur.execute("""
            SELECT viewname, definition
            FROM pg_views
            WHERE schemaname = 'public'
            AND viewname NOT LIKE 'pg_%'
        """)
    
    views = cur.fetchall()
    
    if not views:
        print("No views found to export.")
        return
    
    for view_name, definition in views:
        # Skip our monitoring view
        if view_name == 'query_stats':
            continue
            
        filepath = VIEWS_DIR / f"{view_name}.sql"
        content = get_header("View", view_name)
        content += f"DROP VIEW IF EXISTS {view_name} CASCADE;\n\n"
        content += f"CREATE OR REPLACE VIEW {view_name} AS\n{definition}\n"
        
        filepath.write_text(content)
        print(f"✅ Exported view: {filepath}")
    
    cur.close()


def export_tables(conn, specific_name: str = None):
    """Export table schemas from database to SQL files."""
    cur = conn.cursor()
    
    if specific_name:
        tables = [(specific_name,)]
    else:
        cur.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """)
        tables = cur.fetchall()
    
    if not tables:
        print("No tables found to export.")
        return
    
    for (table_name,) in tables:
        # Get column definitions
        cur.execute("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = cur.fetchall()
        
        # Get primary key
        cur.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass
            AND i.indisprimary
        """, (table_name,))
        pk_columns = [row[0] for row in cur.fetchall()]
        
        # Get foreign keys
        cur.execute("""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = %s
        """, (table_name,))
        foreign_keys = cur.fetchall()
        
        # Build CREATE TABLE statement
        filepath = TABLES_DIR / f"{table_name}.sql"
        content = get_header("Table", table_name)
        content += f"DROP TABLE IF EXISTS {table_name} CASCADE;\n\n"
        content += f"CREATE TABLE {table_name} (\n"
        
        col_defs = []
        for col_name, data_type, max_length, nullable, default in columns:
            col_def = f"    {col_name} "
            
            if max_length:
                col_def += f"{data_type}({max_length})"
            else:
                col_def += data_type
            
            if col_name in pk_columns and 'serial' not in data_type.lower():
                if default and 'nextval' in str(default):
                    col_def = f"    {col_name} SERIAL"
            
            if nullable == 'NO' and col_name not in pk_columns:
                col_def += " NOT NULL"
            
            if default and 'nextval' not in str(default):
                col_def += f" DEFAULT {default}"
            
            col_defs.append(col_def)
        
        # Add primary key constraint
        if pk_columns:
            col_defs.append(f"    PRIMARY KEY ({', '.join(pk_columns)})")
        
        # Add foreign key constraints
        for fk_col, fk_table, fk_ref_col in foreign_keys:
            col_defs.append(f"    FOREIGN KEY ({fk_col}) REFERENCES {fk_table}({fk_ref_col})")
        
        content += ",\n".join(col_defs)
        content += "\n);\n"
        
        filepath.write_text(content)
        print(f"✅ Exported table: {filepath}")
    
    cur.close()


def export_procedures(conn, specific_name: str = None):
    """Export stored procedures from database to SQL files."""
    cur = conn.cursor()
    
    if specific_name:
        cur.execute("""
            SELECT proname, pg_get_functiondef(oid) as definition
            FROM pg_proc
            WHERE pronamespace = 'public'::regnamespace
            AND prokind = 'p'
            AND proname = %s
        """, (specific_name,))
    else:
        cur.execute("""
            SELECT proname, pg_get_functiondef(oid) as definition
            FROM pg_proc
            WHERE pronamespace = 'public'::regnamespace
            AND prokind = 'p'
        """)
    
    procedures = cur.fetchall()
    
    if not procedures:
        print("No procedures found to export.")
        return
    
    for proc_name, definition in procedures:
        filepath = PROCEDURES_DIR / f"{proc_name}.sql"
        content = get_header("Procedure", proc_name)
        content += f"DROP PROCEDURE IF EXISTS {proc_name} CASCADE;\n\n"
        content += definition + ";\n"
        
        filepath.write_text(content)
        print(f"✅ Exported procedure: {filepath}")
    
    cur.close()


def export_all(conn):
    """Export all database objects."""
    print("\n📦 Exporting all database objects...\n")
    print("=" * 50)
    print("FUNCTIONS:")
    print("=" * 50)
    export_functions(conn)
    
    print("\n" + "=" * 50)
    print("VIEWS:")
    print("=" * 50)
    export_views(conn)
    
    print("\n" + "=" * 50)
    print("TABLES:")
    print("=" * 50)
    export_tables(conn)
    
    print("\n" + "=" * 50)
    print("PROCEDURES:")
    print("=" * 50)
    export_procedures(conn)
    
    print("\n✅ Export complete! Files saved to sql/ folder.")
    print("📝 Don't forget to: git add . && git commit -m 'Export DB objects'")


def main():
    parser = argparse.ArgumentParser(description='Export database objects to SQL files')
    parser.add_argument('--all', action='store_true', help='Export all objects')
    parser.add_argument('--functions', action='store_true', help='Export all functions')
    parser.add_argument('--views', action='store_true', help='Export all views')
    parser.add_argument('--tables', action='store_true', help='Export all table schemas')
    parser.add_argument('--procedures', action='store_true', help='Export all procedures')
    parser.add_argument('--function', type=str, help='Export specific function by name')
    parser.add_argument('--view', type=str, help='Export specific view by name')
    parser.add_argument('--table', type=str, help='Export specific table by name')
    
    args = parser.parse_args()
    
    # Ensure directories exist
    ensure_dirs()
    
    # Connect to database
    try:
        conn = get_connection()
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        sys.exit(1)
    
    try:
        if args.all:
            export_all(conn)
        elif args.functions:
            export_functions(conn)
        elif args.views:
            export_views(conn)
        elif args.tables:
            export_tables(conn)
        elif args.procedures:
            export_procedures(conn)
        elif args.function:
            export_functions(conn, args.function)
        elif args.view:
            export_views(conn, args.view)
        elif args.table:
            export_tables(conn, args.table)
        else:
            parser.print_help()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
