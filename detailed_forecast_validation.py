#!/usr/bin/env python3
"""
Detailed Forecast Validation for Gate 1
=======================================

This script performs detailed validation of forecast responses to ensure
they meet all Gate 1 criteria with specific numerical checks.
"""

import requests
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def test_specific_forecast(pattern_id, base_url="http://localhost:5000"):
    """Test a specific forecast and display detailed results."""
    print(f"🔬 Detailed Forecast Test for Pattern ID: {pattern_id}")
    print("=" * 60)
    
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
    
    print("📊 FORECAST RESPONSE ANALYSIS")
    print("-" * 40)
    
    # Basic info
    print(f"Status: {forecast_data.get('status')}")
    print(f"Hospital: {forecast_data.get('hospital_name')}")
    print(f"ZIP Code: {forecast_data.get('zip_code')}")
    print(f"Historical Data Points: {forecast_data.get('historical_data_points')}")
    print(f"Model Used: {forecast_data.get('model_used')}")
    print(f"Confidence Level: {forecast_data.get('confidence_level')}")
    
    if forecast_data.get('status') != 'success':
        print(f"❌ Forecast failed: {forecast_data.get('message', 'Unknown error')}")
        return False
    
    # Forecast details
    dates = forecast_data.get('dates', [])
    values = forecast_data.get('values', [])
    lower_bounds = forecast_data.get('lower_bound', [])
    upper_bounds = forecast_data.get('upper_bound', [])
    
    print(f"\n📅 FORECAST DETAILS")
    print("-" * 40)
    print(f"Forecast Length: {len(dates)} days")
    print(f"Date Range: {dates[0] if dates else 'N/A'} to {dates[-1] if dates else 'N/A'}")
    
    # Validate Gate 1 criteria
    print(f"\n✅ GATE 1 CRITERIA VALIDATION")
    print("-" * 40)
    
    # Criterion 1: 3-7 day forecast
    forecast_length_valid = 3 <= len(dates) <= 7
    print(f"1. Forecast Length (3-7 days): {'✅ PASS' if forecast_length_valid else '❌ FAIL'} ({len(dates)} days)")
    
    # Criterion 2: Confidence intervals present
    ci_present = (len(lower_bounds) == len(dates) and len(upper_bounds) == len(dates) and
                  all(isinstance(x, (int, float)) for x in lower_bounds + upper_bounds))
    print(f"2. Confidence Intervals Present: {'✅ PASS' if ci_present else '❌ FAIL'}")
    
    # Criterion 3: CI bounds logical
    ci_logical = all(lower_bounds[i] <= values[i] <= upper_bounds[i] for i in range(len(values))) if ci_present else False
    print(f"3. CI Bounds Logical (lower ≤ value ≤ upper): {'✅ PASS' if ci_logical else '❌ FAIL'}")
    
    # Criterion 4: Values reasonable
    values_reasonable = all(isinstance(v, (int, float)) and v >= 0 and v < 1000 for v in values)
    print(f"4. Forecast Values Reasonable: {'✅ PASS' if values_reasonable else '❌ FAIL'}")
    
    # Display daily forecast table
    if dates and values:
        print(f"\n📋 DAILY FORECAST TABLE")
        print("-" * 80)
        print(f"{'Date':<12} {'Day':<4} {'Predicted':<10} {'Lower CI':<10} {'Upper CI':<10} {'CI Width':<10}")
        print("-" * 80)
        
        for i in range(len(dates)):
            date = datetime.strptime(dates[i], '%Y-%m-%d')
            day_name = date.strftime('%a')
            date_str = date.strftime('%m/%d')
            
            predicted = values[i]
            lower = lower_bounds[i] if i < len(lower_bounds) else 'N/A'
            upper = upper_bounds[i] if i < len(upper_bounds) else 'N/A'
            
            if isinstance(lower, (int, float)) and isinstance(upper, (int, float)):
                ci_width = upper - lower
                print(f"{date_str:<12} {day_name:<4} {predicted:<10.1f} {lower:<10.1f} {upper:<10.1f} {ci_width:<10.1f}")
            else:
                print(f"{date_str:<12} {day_name:<4} {predicted:<10.1f} {'N/A':<10} {'N/A':<10} {'N/A':<10}")
    
    # Interpretation analysis
    interpretation = forecast_data.get('interpretation', {})
    if interpretation:
        print(f"\n🧠 AI INTERPRETATION")
        print("-" * 40)
        print(f"Summary: {interpretation.get('summary', 'N/A')}")
        print(f"Trend: {interpretation.get('trend_analysis', 'N/A')}")
        print(f"Confidence: {interpretation.get('confidence_interpretation', 'N/A')}")
    
    # Overall assessment
    all_criteria_met = forecast_length_valid and ci_present and ci_logical and values_reasonable
    
    print(f"\n🎯 OVERALL GATE 1 ASSESSMENT")
    print("-" * 40)
    if all_criteria_met:
        print("🎉 ALL GATE 1 CRITERIA MET!")
        print("✅ This forecast meets all requirements for Gate 1 validation")
    else:
        print("❌ SOME GATE 1 CRITERIA NOT MET")
        print("⚠️  Review the failed criteria above")
    
    return all_criteria_met

def test_all_forecasting_patterns():
    """Test all available forecasting patterns."""
    print("🧪 Testing All Forecasting Patterns")
    print("=" * 60)
    
    # Get test patterns
    conn = sqlite3.connect('public_health_data.db')
    query = """
        SELECT id, hospital_name, zip_code, pattern_type, current_value, percentage_change
        FROM pattern_detections 
        WHERE hospital_name LIKE 'Test Forecasting%'
        ORDER BY id DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) == 0:
        print("❌ No test forecasting patterns found")
        return False
    
    print(f"Found {len(df)} test patterns:")
    for _, pattern in df.iterrows():
        print(f"  ID {pattern['id']}: {pattern['hospital_name']} ({pattern['pattern_type']})")
    
    # Test each pattern
    all_passed = True
    for _, pattern in df.iterrows():
        print(f"\n{'='*80}")
        result = test_specific_forecast(pattern['id'])
        if not result:
            all_passed = False
        print(f"{'='*80}")
    
    # Final summary
    print(f"\n🎯 FINAL SUMMARY")
    print("=" * 60)
    if all_passed:
        print("🎉 ALL FORECASTING PATTERNS PASSED GATE 1 VALIDATION!")
    else:
        print("❌ Some forecasting patterns failed validation")
    
    return all_passed

def main():
    """Main function."""
    print("🔬 Detailed Forecast Validation for Gate 1")
    print("Testing specific forecast responses against all criteria")
    print("=" * 80)
    
    success = test_all_forecasting_patterns()
    
    if success:
        print("\n✅ Gate 1 validation completed successfully!")
        print("🚀 Ready for production deployment")
    else:
        print("\n❌ Gate 1 validation failed")
        print("🔧 Please fix the issues before proceeding")

if __name__ == "__main__":
    main()
