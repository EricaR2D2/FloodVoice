#!/usr/bin/env python3
import sqlite3
import pandas as pd

def check_database_structure():
    """Check the structure and data quality of the database."""
    try:
        conn = sqlite3.connect('public_health_data.db')
        cursor = conn.cursor()
        
        print("=== DATABASE STRUCTURE ANALYSIS ===\n")
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("📋 Available Tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "="*50)
        
        # Check each table
        for table in tables:
            table_name = table[0]
            print(f"\n🔍 TABLE: {table_name}")
            print("-" * 30)
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Total records: {count}")
            
            # Get sample data if table has records
            if count > 0:
                try:
                    sample_df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 3", conn)
                    print("Sample data:")
                    print(sample_df.to_string(index=False))
                except Exception as e:
                    print(f"Error reading sample data: {e}")
            
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database_structure()
