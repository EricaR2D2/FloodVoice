#!/usr/bin/env python3
"""
Check Real Hospital Data
========================
Check what real hospital data is available for forecasting.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def check_real_hospitals():
    """Check real hospital data availability."""
    print("🏥 Checking Real Hospital Data")
    print("=" * 50)
    
    conn = sqlite3.connect('public_health_data.db')
    
    # Get real hospitals (not test data)
    query = """
        SELECT DISTINCT hospital_name, zip_code, COUNT(*) as records,
               MIN(date) as earliest_date, MAX(date) as latest_date
        FROM hospital_data 
        WHERE hospital_name NOT LIKE 'Test%'
        GROUP BY hospital_name, zip_code 
        ORDER BY records DESC 
        LIMIT 15
    """
    
    df = pd.read_sql_query(query, conn)
    
    if len(df) == 0:
        print("❌ No real hospital data found!")
        return
    
    print(f"Found {len(df)} real hospitals with data:")
    print("-" * 80)
    print(f"{'Hospital':<35} {'ZIP':<8} {'Records':<8} {'Date Range':<20}")
    print("-" * 80)
    
    for _, row in df.iterrows():
        date_range = f"{row['earliest_date']} to {row['latest_date']}"
        print(f"{row['hospital_name'][:34]:<35} {row['zip_code']:<8} {row['records']:<8} {date_range}")
    
    # Check for recent patterns with real hospitals
    print(f"\n🔍 Checking Recent Patterns with Real Hospitals")
    print("-" * 50)
    
    pattern_query = """
        SELECT id, hospital_name, zip_code, pattern_type, current_value, percentage_change, date
        FROM pattern_detections 
        WHERE hospital_name NOT LIKE 'Test%'
        ORDER BY id DESC 
        LIMIT 10
    """
    
    patterns_df = pd.read_sql_query(pattern_query, conn)
    
    if len(patterns_df) == 0:
        print("❌ No real hospital patterns found!")
    else:
        print(f"Found {len(patterns_df)} recent patterns with real hospitals:")
        print("-" * 100)
        print(f"{'ID':<8} {'Hospital':<30} {'ZIP':<8} {'Type':<12} {'Value':<8} {'Change':<10} {'Date'}")
        print("-" * 100)
        
        for _, pattern in patterns_df.iterrows():
            print(f"{pattern['id']:<8} {pattern['hospital_name'][:29]:<30} {pattern['zip_code']:<8} {pattern['pattern_type']:<12} {pattern['current_value']:<8} {pattern['percentage_change']:+.1f}%{'':<4} {pattern['date']}")
    
    conn.close()
    
    return patterns_df if len(patterns_df) > 0 else None

def check_data_sufficiency():
    """Check if real hospitals have sufficient data for forecasting."""
    print(f"\n📊 Checking Data Sufficiency for Forecasting")
    print("-" * 50)
    
    conn = sqlite3.connect('public_health_data.db')
    
    # Check hospitals with at least 7 days of data (minimum for forecasting)
    query = """
        SELECT hospital_name, zip_code, COUNT(*) as records,
               MIN(date) as earliest_date, MAX(date) as latest_date
        FROM hospital_data 
        WHERE hospital_name NOT LIKE 'Test%'
        GROUP BY hospital_name, zip_code 
        HAVING COUNT(*) >= 7
        ORDER BY records DESC 
        LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    
    if len(df) == 0:
        print("❌ No real hospitals have sufficient data (7+ records) for forecasting!")
        print("💡 This is why the test was using 'Test Forecasting Hospital' data.")
    else:
        print(f"✅ Found {len(df)} real hospitals with sufficient data for forecasting:")
        print("-" * 80)
        print(f"{'Hospital':<35} {'ZIP':<8} {'Records':<8} {'Date Range':<20}")
        print("-" * 80)
        
        for _, row in df.iterrows():
            date_range = f"{row['earliest_date']} to {row['latest_date']}"
            print(f"{row['hospital_name'][:34]:<35} {row['zip_code']:<8} {row['records']:<8} {date_range}")
    
    conn.close()
    return df

if __name__ == "__main__":
    patterns = check_real_hospitals()
    sufficient_data = check_data_sufficiency()
    
    print(f"\n📋 Summary:")
    print("-" * 30)
    if sufficient_data is not None and len(sufficient_data) > 0:
        print("✅ Real hospital data is available for forecasting")
        print("🔧 We should update the test to use real hospitals instead of test data")
    else:
        print("❌ Real hospital data is insufficient for forecasting")
        print("💡 This explains why test data was created for validation")
