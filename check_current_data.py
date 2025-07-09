#!/usr/bin/env python3
import sqlite3
import pandas as pd

def check_current_data():
    """Check current data sources and ZIP code coverage."""
    
    conn = sqlite3.connect('public_health_data.db')
    
    print('=== CURRENT DATA SOURCES ===')
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
    for table in tables['name']:
        count = pd.read_sql_query(f'SELECT COUNT(*) as count FROM {table}', conn).iloc[0]['count']
        print(f'{table}: {count} records')
    
    print('\n=== ZIP CODES IN HOSPITAL DATA ===')
    zip_codes = pd.read_sql_query('SELECT DISTINCT zip_code, COUNT(*) as count FROM real_hospital_data GROUP BY zip_code ORDER BY count DESC LIMIT 10', conn)
    print(zip_codes)
    
    print('\n=== ZIP CODES IN FLU DATA ===')
    flu_zips = pd.read_sql_query('SELECT DISTINCT zip_code, COUNT(*) as count FROM flu_surveillance_data GROUP BY zip_code ORDER BY count DESC LIMIT 10', conn)
    print(flu_zips)
    
    print('\n=== RESTAURANT DATA ===')
    restaurant_zips = pd.read_sql_query('SELECT DISTINCT zip_code, COUNT(*) as count FROM restaurant_inspection_data GROUP BY zip_code ORDER BY count DESC LIMIT 10', conn)
    print(restaurant_zips)
    
    conn.close()

if __name__ == "__main__":
    check_current_data()
