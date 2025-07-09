#!/usr/bin/env python3
import sqlite3
from datetime import datetime, timedelta

def emergency_pattern_cleanup():
    """Emergency cleanup of excessive pattern detections."""
    
    conn = sqlite3.connect('public_health_data.db')
    cursor = conn.cursor()
    
    print("🚨 EMERGENCY PATTERN CLEANUP")
    print("=" * 40)
    
    # Check current count
    cursor.execute("SELECT COUNT(*) FROM pattern_detections")
    current_count = cursor.fetchone()[0]
    print(f"Current patterns: {current_count:,}")
    
    if current_count > 1000000:  # More than 1 million
        print("⚠️ Excessive patterns detected. Performing emergency cleanup...")
        
        # Strategy 1: Keep only recent high-confidence patterns
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        print(f"Keeping only patterns after {cutoff_date} with HIGH confidence...")
        
        # Create backup table first
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_detections_backup AS 
            SELECT * FROM pattern_detections 
            WHERE date >= ? AND confidence_level = 'HIGH'
            LIMIT 10000
        """, (cutoff_date,))
        
        # Count backup
        cursor.execute("SELECT COUNT(*) FROM pattern_detections_backup")
        backup_count = cursor.fetchone()[0]
        print(f"Backed up {backup_count:,} recent high-confidence patterns")
        
        # Drop original table
        cursor.execute("DROP TABLE pattern_detections")
        
        # Rename backup to original
        cursor.execute("ALTER TABLE pattern_detections_backup RENAME TO pattern_detections")
        
        # Verify cleanup
        cursor.execute("SELECT COUNT(*) FROM pattern_detections")
        new_count = cursor.fetchone()[0]
        print(f"Cleaned up to {new_count:,} patterns")
        
        removed = current_count - new_count
        print(f"Removed {removed:,} excessive patterns")
        
    else:
        print("✅ Pattern count is reasonable")
    
    # Create index for better performance
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_date ON pattern_detections(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_zip ON pattern_detections(zip_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_hospital ON pattern_detections(hospital_name)")
        print("✅ Created performance indexes")
    except Exception as e:
        print(f"Index creation warning: {e}")
    
    conn.commit()
    conn.close()
    
    print("✅ Emergency cleanup complete!")

if __name__ == "__main__":
    emergency_pattern_cleanup()
