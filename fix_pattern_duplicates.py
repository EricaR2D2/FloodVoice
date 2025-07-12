#!/usr/bin/env python3
"""
Fix pattern detection duplicates causing 500 errors
"""

import sqlite3
import pandas as pd

def fix_pattern_duplicates():
    """Clear duplicate patterns and fix the database."""
    
    conn = sqlite3.connect('public_health_data.db')
    cursor = conn.cursor()
    
    print("🔧 FIXING PATTERN DETECTION DUPLICATES")
    print("=" * 50)
    
    # Check current pattern count
    pattern_count = pd.read_sql_query("SELECT COUNT(*) as count FROM pattern_detections", conn).iloc[0]['count']
    print(f"Current pattern count: {pattern_count}")
    
    # Check for duplicates
    duplicates = pd.read_sql_query("""
        SELECT zip_code, date, pattern_type, COUNT(*) as count 
        FROM pattern_detections 
        GROUP BY zip_code, date, pattern_type 
        HAVING COUNT(*) > 1
        ORDER BY count DESC
        LIMIT 10
    """, conn)
    
    print(f"\nDuplicate patterns found: {len(duplicates)}")
    if not duplicates.empty:
        print("Sample duplicates:")
        print(duplicates)
    
    # Clear all patterns to start fresh
    print("\n🗑️ Clearing all pattern detections...")
    cursor.execute("DELETE FROM pattern_detections")
    
    # Reset the auto-increment counter
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='pattern_detections'")
    
    conn.commit()
    
    # Verify cleanup
    new_count = pd.read_sql_query("SELECT COUNT(*) as count FROM pattern_detections", conn).iloc[0]['count']
    print(f"✅ Pattern count after cleanup: {new_count}")
    
    conn.close()
    
    print("\n✅ Pattern duplicates fixed!")
    print("The dashboard should now load without 500 errors.")
    print("Pattern detection will run fresh when the app starts.")

if __name__ == "__main__":
    fix_pattern_duplicates()
