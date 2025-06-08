#!/usr/bin/env python3
"""
Create Test Data for Forecasting Validation
==========================================

This script creates sufficient historical hospital data to enable proper
forecasting testing for Gate 1 validation.
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def create_test_hospital_data():
    """Create test hospital data with sufficient history for forecasting."""
    print("🏥 Creating test hospital data for forecasting validation...")
    
    conn = sqlite3.connect('public_health_data.db')
    
    # Create test hospitals with different patterns
    test_hospitals = [
        {
            'hospital_name': 'Test Forecasting Hospital A',
            'zip_code': '10001',
            'pattern_type': 'spike',
            'base_visits': 25
        },
        {
            'hospital_name': 'Test Forecasting Hospital B', 
            'zip_code': '10002',
            'pattern_type': 'drop',
            'base_visits': 30
        },
        {
            'hospital_name': 'Test Forecasting Hospital C',
            'zip_code': '10003', 
            'pattern_type': 'consistently_high',
            'base_visits': 20
        },
        {
            'hospital_name': 'Test Forecasting Hospital D',
            'zip_code': '10004',
            'pattern_type': 'normal',
            'base_visits': 35
        }
    ]
    
    # Generate 45 days of historical data for each hospital
    all_data = []
    base_date = datetime.now() - timedelta(days=45)
    
    for hospital in test_hospitals:
        print(f"   Creating data for {hospital['hospital_name']} ({hospital['pattern_type']})")
        
        for day in range(45):
            date = base_date + timedelta(days=day)
            base_visits = hospital['base_visits']
            
            # Add realistic variation
            daily_variation = np.random.normal(0, 3)
            visits = max(1, int(base_visits + daily_variation))
            
            # Add pattern-specific behavior in recent days
            if day >= 35:  # Last 10 days
                if hospital['pattern_type'] == 'spike':
                    if day >= 42:  # Last 3 days - spike
                        visits = int(visits * 1.6)  # 60% increase
                elif hospital['pattern_type'] == 'drop':
                    if day >= 42:  # Last 3 days - drop
                        visits = int(visits * 0.5)  # 50% decrease
                elif hospital['pattern_type'] == 'consistently_high':
                    if day >= 38:  # Last 7 days - consistently high
                        visits = int(visits * 1.3)  # 30% increase
            
            all_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'hospital_name': hospital['hospital_name'],
                'zip_code': hospital['zip_code'],
                'er_visits_respiratory': visits
            })
    
    # Insert data into database
    df = pd.DataFrame(all_data)
    df.to_sql('hospital_data', conn, if_exists='append', index=False)
    
    print(f"✅ Created {len(all_data)} hospital data records")
    
    # Create corresponding pattern detections
    create_test_patterns(conn, test_hospitals)
    
    conn.close()

def create_test_patterns(conn, test_hospitals):
    """Create pattern detections for the test hospitals."""
    print("🔍 Creating test pattern detections...")
    
    cursor = conn.cursor()
    detection_timestamp = datetime.now().isoformat()
    pattern_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    patterns = []
    
    for hospital in test_hospitals:
        if hospital['pattern_type'] != 'normal':
            
            # Calculate realistic pattern values
            base_visits = hospital['base_visits']
            
            if hospital['pattern_type'] == 'spike':
                current_value = int(base_visits * 1.6)
                percentage_change = 60.0
            elif hospital['pattern_type'] == 'drop':
                current_value = int(base_visits * 0.5)
                percentage_change = -50.0
            elif hospital['pattern_type'] == 'consistently_high':
                current_value = int(base_visits * 1.3)
                percentage_change = 30.0
            
            # Create AI explanation
            ai_explanation = f"Detected {hospital['pattern_type']} pattern in {hospital['hospital_name']} (ZIP {hospital['zip_code']}). Current ER respiratory visits: {current_value}, representing a {percentage_change:+.1f}% change from the 7-day average."
            
            # Insert pattern
            cursor.execute("""
                INSERT INTO pattern_detections
                (detection_timestamp, date, zip_code, hospital_name, pattern_type,
                 current_value, rolling_mean, percentage_change, confidence_score,
                 confidence_level, context_data, ai_explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                detection_timestamp,
                pattern_date,
                hospital['zip_code'],
                hospital['hospital_name'],
                hospital['pattern_type'],
                current_value,
                base_visits,
                percentage_change,
                0.85,
                'HIGH',
                json.dumps({}),
                ai_explanation
            ))
            
            patterns.append({
                'hospital': hospital['hospital_name'],
                'zip_code': hospital['zip_code'],
                'pattern_type': hospital['pattern_type']
            })
    
    conn.commit()
    print(f"✅ Created {len(patterns)} test pattern detections")
    
    # Display created patterns
    cursor.execute("""
        SELECT id, hospital_name, zip_code, pattern_type, current_value, percentage_change
        FROM pattern_detections 
        WHERE hospital_name LIKE 'Test Forecasting%'
        ORDER BY id DESC
    """)
    
    new_patterns = cursor.fetchall()
    print("\n📋 Created test patterns:")
    for pattern in new_patterns:
        print(f"   ID: {pattern[0]}, {pattern[1]} (ZIP {pattern[2]}), {pattern[3]}, Value: {pattern[4]}, Change: {pattern[5]:+.1f}%")

def main():
    """Main function to create test data."""
    print("🧪 Creating Test Data for Forecasting Gate 1 Validation")
    print("=" * 60)
    
    create_test_hospital_data()
    
    print("\n✅ Test data creation completed!")
    print("🔬 You can now run the Gate 1 validation tests with sufficient data.")
    print("📊 Run: python test_forecasting_gate1.py")

if __name__ == "__main__":
    main()
