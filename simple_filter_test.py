#!/usr/bin/env python3
import sqlite3
import pandas as pd

def simple_filter_test():
    """Simple test of filter functionality."""
    
    conn = sqlite3.connect('public_health_data.db')
    
    print("🎯 SIMPLE FILTER TEST")
    print("=" * 30)
    
    # Test 1: Check if data exists for common filters
    print("\n1. Testing Borough Filter - Manhattan")
    manhattan_hospitals = pd.read_sql_query("""
        SELECT COUNT(*) as count, MIN(date) as earliest, MAX(date) as latest
        FROM real_hospital_data 
        WHERE borough = 'Manhattan'
    """, conn)
    
    print(f"   Manhattan hospitals: {manhattan_hospitals.iloc[0]['count']} records")
    print(f"   Date range: {manhattan_hospitals.iloc[0]['earliest']} to {manhattan_hospitals.iloc[0]['latest']}")
    
    # Test 2: Check ZIP code filter
    print("\n2. Testing ZIP Code Filter - 10001")
    zip_data = pd.read_sql_query("""
        SELECT COUNT(*) as hospital_count
        FROM real_hospital_data 
        WHERE zip_code = '10001'
    """, conn)
    
    flu_data = pd.read_sql_query("""
        SELECT COUNT(*) as flu_count
        FROM flu_surveillance_data 
        WHERE zip_code = '10001'
    """, conn)
    
    print(f"   ZIP 10001 - Hospital records: {zip_data.iloc[0]['hospital_count']}")
    print(f"   ZIP 10001 - Flu records: {flu_data.iloc[0]['flu_count']}")
    
    # Test 3: Check recent data availability
    print("\n3. Testing Date Filter - Last 30 days")
    recent_hospital = pd.read_sql_query("""
        SELECT COUNT(*) as count
        FROM real_hospital_data 
        WHERE date >= date('now', '-30 days')
    """, conn)
    
    recent_flu = pd.read_sql_query("""
        SELECT COUNT(*) as count
        FROM flu_surveillance_data 
        WHERE date >= date('now', '-30 days')
    """, conn)
    
    print(f"   Recent hospital data: {recent_hospital.iloc[0]['count']} records")
    print(f"   Recent flu data: {recent_flu.iloc[0]['count']} records")
    
    # Test 4: Check illness type filter
    print("\n4. Testing Illness Type Filter")
    illness_types = pd.read_sql_query("""
        SELECT illness_type, COUNT(*) as count
        FROM flu_surveillance_data 
        GROUP BY illness_type
    """, conn)
    
    for _, row in illness_types.iterrows():
        print(f"   {row['illness_type']}: {row['count']} records")
    
    # Test 5: Check pattern detection count (simplified)
    print("\n5. Pattern Detection Status")
    try:
        pattern_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM pattern_detections 
            LIMIT 1
        """, conn)
        print(f"   Pattern records: {pattern_count.iloc[0]['count']:,}")
        
        if pattern_count.iloc[0]['count'] > 100000:
            print("   ⚠️ WARNING: Excessive pattern records may cause performance issues")
        else:
            print("   ✅ Pattern count is reasonable")
            
    except Exception as e:
        print(f"   ❌ Error accessing patterns: {e}")
    
    conn.close()
    
    print("\n" + "=" * 30)
    print("✅ Simple filter test complete!")

if __name__ == "__main__":
    simple_filter_test()
