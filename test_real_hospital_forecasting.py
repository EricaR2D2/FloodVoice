#!/usr/bin/env python3
"""
Test Real Hospital Forecasting
==============================
Test forecasting with actual real hospital data that has sufficient history.
"""

import requests
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def find_real_hospitals_with_sufficient_data():
    """Find real hospitals with enough data for forecasting."""
    print("🔍 Finding Real Hospitals with Sufficient Data for Forecasting")
    print("=" * 70)
    
    conn = sqlite3.connect('public_health_data.db')
    
    # Find hospitals with at least 15 data points for reliable forecasting
    query = """
        SELECT hospital_name, zip_code, COUNT(*) as records,
               MIN(date) as earliest_date, MAX(date) as latest_date
        FROM hospital_data 
        WHERE hospital_name NOT LIKE 'Test%'
        GROUP BY hospital_name, zip_code 
        HAVING COUNT(*) >= 15
        ORDER BY records DESC 
        LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    
    if len(df) == 0:
        print("❌ No real hospitals found with 15+ records")
        
        # Try with lower threshold
        query_lower = """
            SELECT hospital_name, zip_code, COUNT(*) as records,
                   MIN(date) as earliest_date, MAX(date) as latest_date
            FROM hospital_data 
            WHERE hospital_name NOT LIKE 'Test%'
            GROUP BY hospital_name, zip_code 
            HAVING COUNT(*) >= 7
            ORDER BY records DESC 
            LIMIT 10
        """
        
        df = pd.read_sql_query(query_lower, conn)
        
        if len(df) == 0:
            print("❌ No real hospitals found with even 7+ records")
            conn.close()
            return None
        else:
            print(f"⚠️  Found {len(df)} hospitals with 7+ records (minimum for forecasting):")
    else:
        print(f"✅ Found {len(df)} hospitals with 15+ records:")
    
    print("-" * 80)
    print(f"{'Hospital':<35} {'ZIP':<8} {'Records':<8} {'Date Range':<25}")
    print("-" * 80)
    
    for _, row in df.iterrows():
        date_range = f"{row['earliest_date']} to {row['latest_date']}"
        print(f"{row['hospital_name'][:34]:<35} {row['zip_code']:<8} {row['records']:<8} {date_range}")
    
    conn.close()
    return df

def find_real_patterns_with_sufficient_data():
    """Find real patterns that have corresponding hospital data for forecasting."""
    print(f"\n🎯 Finding Real Patterns with Sufficient Hospital Data")
    print("=" * 60)
    
    conn = sqlite3.connect('public_health_data.db')
    
    # Find patterns where the hospital has sufficient data
    query = """
        SELECT p.id, p.hospital_name, p.zip_code, p.pattern_type, 
               p.current_value, p.percentage_change, p.date,
               h.record_count
        FROM pattern_detections p
        JOIN (
            SELECT hospital_name, zip_code, COUNT(*) as record_count
            FROM hospital_data 
            WHERE hospital_name NOT LIKE 'Test%'
            GROUP BY hospital_name, zip_code
            HAVING COUNT(*) >= 7
        ) h ON p.hospital_name = h.hospital_name AND p.zip_code = h.zip_code
        WHERE p.hospital_name NOT LIKE 'Test%'
        ORDER BY h.record_count DESC, p.id DESC
        LIMIT 10
    """
    
    df = pd.read_sql_query(query, conn)
    
    if len(df) == 0:
        print("❌ No real patterns found with sufficient hospital data")
        conn.close()
        return None
    
    print(f"✅ Found {len(df)} real patterns with sufficient hospital data:")
    print("-" * 100)
    print(f"{'ID':<8} {'Hospital':<30} {'ZIP':<8} {'Type':<12} {'Value':<8} {'Change':<10} {'Records':<8} {'Date'}")
    print("-" * 100)
    
    for _, pattern in df.iterrows():
        print(f"{pattern['id']:<8} {pattern['hospital_name'][:29]:<30} {pattern['zip_code']:<8} {pattern['pattern_type']:<12} {pattern['current_value']:<8} {pattern['percentage_change']:+.1f}%{'':<4} {pattern['record_count']:<8} {pattern['date']}")
    
    conn.close()
    return df

def test_real_hospital_forecast(pattern_id, hospital_name, zip_code, base_url="http://localhost:5000"):
    """Test forecasting for a real hospital pattern."""
    print(f"\n🔬 Testing Real Hospital Forecast")
    print(f"   Pattern ID: {pattern_id}")
    print(f"   Hospital: {hospital_name}")
    print(f"   ZIP Code: {zip_code}")
    print("-" * 60)
    
    # Setup session
    session = requests.Session()
    
    # Login
    login_data = {'username': 'admin', 'password': 'admin123'}
    login_response = session.post(f"{base_url}/login", data=login_data)
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return False
    
    # Get forecast
    url = f"{base_url}/api/pattern/{pattern_id}/forecast"
    response = session.get(url, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ API call failed: HTTP {response.status_code}")
        return False
    
    forecast_data = response.json()
    
    print(f"📊 Forecast Status: {forecast_data.get('status')}")
    
    if forecast_data.get('status') == 'success':
        print(f"✅ Forecast generated successfully!")
        print(f"   Model Used: {forecast_data.get('model_used')}")
        print(f"   Historical Data Points: {forecast_data.get('historical_data_points')}")
        print(f"   Forecast Days: {len(forecast_data.get('dates', []))}")
        
        # Show sample forecast values
        dates = forecast_data.get('dates', [])
        values = forecast_data.get('values', [])
        lower_bounds = forecast_data.get('lower_bound', [])
        upper_bounds = forecast_data.get('upper_bound', [])
        
        if dates and values:
            print(f"\n   Sample Forecast (first 3 days):")
            for i in range(min(3, len(dates))):
                date = dates[i]
                value = values[i]
                if i < len(lower_bounds) and i < len(upper_bounds):
                    ci = f"[{lower_bounds[i]:.1f} - {upper_bounds[i]:.1f}]"
                else:
                    ci = "N/A"
                print(f"     {date}: {value:.1f} visits, 95% CI: {ci}")
        
        return True
    
    elif forecast_data.get('status') == 'error':
        error_msg = forecast_data.get('message', forecast_data.get('error_message', 'Unknown error'))
        print(f"❌ Forecast failed: {error_msg}")
        return False
    
    return False

def main():
    """Main function to test real hospital forecasting."""
    print("🏥 Testing Real Hospital Forecasting")
    print("Testing forecasting with actual hospital data from yesterday's ingestion")
    print("=" * 80)
    
    # Find hospitals with sufficient data
    hospitals_df = find_real_hospitals_with_sufficient_data()
    
    if hospitals_df is None or len(hospitals_df) == 0:
        print("\n❌ No real hospitals found with sufficient data for forecasting")
        print("💡 This explains why test data was needed for Gate 1 validation")
        return False
    
    # Find patterns with sufficient data
    patterns_df = find_real_patterns_with_sufficient_data()
    
    if patterns_df is None or len(patterns_df) == 0:
        print("\n❌ No real patterns found with sufficient hospital data")
        return False
    
    # Test forecasting with the top 3 real patterns
    print(f"\n🧪 Testing Forecasting with Top 3 Real Patterns")
    print("=" * 60)
    
    success_count = 0
    total_tests = min(3, len(patterns_df))
    
    for i in range(total_tests):
        pattern = patterns_df.iloc[i]
        success = test_real_hospital_forecast(
            pattern['id'], 
            pattern['hospital_name'], 
            pattern['zip_code']
        )
        if success:
            success_count += 1
    
    # Summary
    print(f"\n📊 Real Hospital Forecasting Test Results")
    print("=" * 50)
    print(f"Tests Passed: {success_count}/{total_tests}")
    print(f"Success Rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 All real hospital forecasting tests passed!")
        print("✅ The system works with actual hospital data")
    else:
        print("⚠️  Some real hospital forecasting tests failed")
        print("💡 This may be due to insufficient historical data")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()
