#!/usr/bin/env python3
"""
Fix database schema to add confidence_level column
"""

import sqlite3

def fix_database():
    """Add confidence_level column to existing pattern_detections table."""
    conn = sqlite3.connect('public_health_data.db')
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(pattern_detections)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'confidence_level' not in columns:
            print("Adding confidence_level column...")
            cursor.execute('ALTER TABLE pattern_detections ADD COLUMN confidence_level TEXT DEFAULT "MEDIUM"')
            conn.commit()
            print("✅ Database updated successfully!")
        else:
            print("✅ confidence_level column already exists")
            
    except Exception as e:
        print(f"❌ Error updating database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()
