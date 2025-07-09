#!/usr/bin/env python3
"""
Fix SQLite database lock issues for NYC Public Health MVP
"""

import sqlite3
import os
import time

def fix_database_lock():
    """Fix database lock issues"""
    db_path = "public_health_data.db"
    
    print("🔧 FIXING DATABASE LOCK ISSUES")
    print("=" * 40)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return False
    
    print(f"📁 Database file: {db_path}")
    print(f"📊 File size: {os.path.getsize(db_path) / (1024*1024):.1f} MB")
    
    # Check for lock files
    lock_files = [
        f"{db_path}-wal",
        f"{db_path}-shm", 
        f"{db_path}-journal"
    ]
    
    print("\n🔍 Checking for lock files...")
    for lock_file in lock_files:
        if os.path.exists(lock_file):
            print(f"⚠️  Found lock file: {lock_file}")
            try:
                os.remove(lock_file)
                print(f"✅ Removed lock file: {lock_file}")
            except Exception as e:
                print(f"❌ Could not remove {lock_file}: {e}")
        else:
            print(f"✅ No lock file: {lock_file}")
    
    # Test database connection
    print("\n🧪 Testing database connection...")
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA cache_size=10000;")
        conn.execute("PRAGMA temp_store=memory;")
        
        # Quick test query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
        table_count = cursor.fetchone()[0]
        print(f"✅ Database connection successful!")
        print(f"📊 Found {table_count} tables")
        
        # Test a data query
        cursor.execute("SELECT COUNT(*) FROM nyc_covid_data LIMIT 1;")
        covid_count = cursor.fetchone()[0]
        print(f"📊 COVID data records: {covid_count:,}")
        
        conn.close()
        print("✅ Database connection closed properly")
        
    except sqlite3.OperationalError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    print("\n🎉 Database is ready for use!")
    return True

def optimize_database():
    """Optimize database for better performance"""
    print("\n⚡ OPTIMIZING DATABASE...")
    
    try:
        conn = sqlite3.connect("public_health_data.db", timeout=30.0)
        
        # Set optimal pragmas
        optimizations = [
            "PRAGMA journal_mode=WAL;",
            "PRAGMA synchronous=NORMAL;", 
            "PRAGMA cache_size=10000;",
            "PRAGMA temp_store=memory;",
            "PRAGMA mmap_size=268435456;",  # 256MB
            "PRAGMA optimize;"
        ]
        
        for pragma in optimizations:
            conn.execute(pragma)
            print(f"✅ Applied: {pragma}")
        
        conn.close()
        print("✅ Database optimization complete!")
        
    except Exception as e:
        print(f"❌ Optimization failed: {e}")

if __name__ == "__main__":
    if fix_database_lock():
        optimize_database()
        print("\n🚀 Ready to start Flask app!")
        print("Run: python app.py")
    else:
        print("\n❌ Database issues need manual intervention")
