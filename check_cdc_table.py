#!/usr/bin/env python3
"""
Check CDC table structure to fix column reference error
"""

import sqlite3
import pandas as pd

def check_cdc_tables():
    """Check CDC table structure."""
    
    conn = sqlite3.connect('public_health_data.db')
    
    print('=== CDC TABLE STRUCTURE ===')
    try:
        # Get all tables with 'cdc' in the name
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%cdc%'", conn)
        print(f'CDC related tables: {list(tables["name"])}')
        
        if len(tables) == 0:
            print('No CDC tables found')
        else:
            for table_name in tables['name']:
                print(f'\n--- {table_name} ---')
                
                # Get table info
                table_info = pd.read_sql_query(f'PRAGMA table_info({table_name})', conn)
                print('Columns:')
                for _, row in table_info.iterrows():
                    print(f'  {row["name"]} ({row["type"]})')
                
                # Get sample data
                sample = pd.read_sql_query(f'SELECT * FROM {table_name} LIMIT 3', conn)
                print(f'Sample data ({len(sample)} rows):')
                if not sample.empty:
                    print(sample.to_string(index=False))
                else:
                    print('  No data')
        
        # Also check for flu-related tables
        print('\n=== FLU RELATED TABLES ===')
        flu_tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%flu%'", conn)
        print(f'Flu related tables: {list(flu_tables["name"])}')
        
        for table_name in flu_tables['name']:
            print(f'\n--- {table_name} ---')
            
            # Get table info
            table_info = pd.read_sql_query(f'PRAGMA table_info({table_name})', conn)
            print('Columns:')
            for _, row in table_info.iterrows():
                print(f'  {row["name"]} ({row["type"]})')
            
    except Exception as e:
        print(f'Error: {e}')
    
    conn.close()

if __name__ == "__main__":
    check_cdc_tables()
