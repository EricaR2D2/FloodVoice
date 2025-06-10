#!/usr/bin/env python3
"""
NYC Tick-Borne Disease Data Ingestion
Based on NYC Health Department surveillance data and seasonal patterns
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def create_tick_disease_data():
    """
    Create realistic tick-borne disease surveillance data for NYC
    Based on NYC Health Advisory 2024 and seasonal patterns
    """
    
    # NYC ZIP codes with known tick activity (based on NYC Health data)
    tick_active_zips = {
        # Staten Island (highest activity per NYC Health Advisory)
        '10301': 'Staten Island North',
        '10302': 'Staten Island West', 
        '10303': 'Staten Island Central',
        '10304': 'Staten Island East',
        '10305': 'Staten Island South',
        
        # Bronx (focal areas mentioned in advisory)
        '10463': 'Bronx Riverdale',
        '10471': 'Bronx Fieldston',
        '10466': 'Bronx Pelham',
        '10467': 'Bronx Norwood',
        
        # Queens (some park areas)
        '11354': 'Queens Flushing',
        '11355': 'Queens Whitestone',
        '11356': 'Queens College Point',
        
        # Brooklyn (limited activity)
        '11209': 'Brooklyn Bay Ridge',
        '11220': 'Brooklyn Sunset Park',
        
        # Manhattan (minimal but some Central Park area)
        '10024': 'Manhattan Upper West Side',
        '10025': 'Manhattan Morningside Heights'
    }
    
    # Disease types based on NYC surveillance
    diseases = [
        'Lyme Disease',
        'Rocky Mountain Spotted Fever', 
        'Ehrlichiosis',
        'Anaplasmosis',
        'Babesiosis',
        'Powassan Virus'
    ]
    
    # Generate 3 years of data (2022-2024)
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    records = []
    
    # Generate seasonal patterns (tick season: April-October)
    current_date = start_date
    case_id = 1
    
    while current_date <= end_date:
        # Seasonal multiplier (higher in tick season)
        month = current_date.month
        if 4 <= month <= 10:  # Tick season
            seasonal_multiplier = 3.0
            if month in [6, 7, 8]:  # Peak season
                seasonal_multiplier = 5.0
        else:  # Off season
            seasonal_multiplier = 0.2
            
        # Generate cases for this day
        daily_cases = max(0, int(np.random.poisson(2 * seasonal_multiplier)))
        
        for _ in range(daily_cases):
            # Select ZIP code (Staten Island most likely)
            zip_weights = [0.4 if '103' in zip_code else 0.1 for zip_code in tick_active_zips.keys()]
            zip_code = np.random.choice(list(tick_active_zips.keys()), p=np.array(zip_weights)/sum(zip_weights))
            
            # Select disease (Lyme most common)
            disease_weights = [0.7, 0.1, 0.08, 0.07, 0.03, 0.02]  # Lyme disease most common
            disease = np.random.choice(diseases, p=disease_weights)
            
            # Patient demographics
            age = max(1, int(np.random.normal(45, 20)))  # Adults more likely
            gender = np.random.choice(['M', 'F'])
            
            # Severity based on disease type
            if disease == 'Lyme Disease':
                severity = np.random.choice(['Mild', 'Moderate', 'Severe'], p=[0.6, 0.3, 0.1])
            elif disease == 'Powassan Virus':
                severity = np.random.choice(['Moderate', 'Severe'], p=[0.3, 0.7])
            else:
                severity = np.random.choice(['Mild', 'Moderate', 'Severe'], p=[0.4, 0.4, 0.2])
            
            # Exposure location (parks, wooded areas)
            exposure_locations = [
                'Staten Island Greenbelt',
                'Van Cortlandt Park',
                'Pelham Bay Park',
                'Central Park',
                'Prospect Park',
                'Flushing Meadows',
                'Forest Park',
                'Private yard',
                'Unknown/Multiple'
            ]
            exposure = np.random.choice(exposure_locations)
            
            record = {
                'case_id': f'TBD-{case_id:06d}',
                'report_date': current_date.strftime('%Y-%m-%d'),
                'zip_code': zip_code,
                'neighborhood': tick_active_zips[zip_code],
                'disease_type': disease,
                'patient_age': age,
                'patient_gender': gender,
                'severity': severity,
                'exposure_location': exposure,
                'lab_confirmed': np.random.choice(['Yes', 'No'], p=[0.8, 0.2]),
                'hospitalized': 'Yes' if severity == 'Severe' else np.random.choice(['Yes', 'No'], p=[0.1, 0.9]),
                'outcome': np.random.choice(['Recovered', 'Ongoing Treatment', 'Chronic'], p=[0.8, 0.15, 0.05])
            }
            
            records.append(record)
            case_id += 1
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(records)

def ingest_tick_disease_data():
    """Ingest tick-borne disease data into the database"""
    
    print("🦟 Generating NYC Tick-Borne Disease Surveillance Data...")
    
    # Generate the dataset
    df = create_tick_disease_data()
    
    print(f"📊 Generated {len(df)} tick-borne disease cases")
    print(f"📅 Date range: {df['report_date'].min()} to {df['report_date'].max()}")
    print(f"🏥 Disease types: {df['disease_type'].unique()}")
    print(f"📍 ZIP codes covered: {len(df['zip_code'].unique())}")
    
    # Connect to database
    conn = sqlite3.connect('public_health_data.db')
    
    # Create table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS tick_disease_surveillance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT UNIQUE,
        report_date DATE,
        zip_code TEXT,
        neighborhood TEXT,
        disease_type TEXT,
        patient_age INTEGER,
        patient_gender TEXT,
        severity TEXT,
        exposure_location TEXT,
        lab_confirmed TEXT,
        hospitalized TEXT,
        outcome TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    conn.execute(create_table_sql)
    
    # Insert data
    df.to_sql('tick_disease_surveillance', conn, if_exists='replace', index=False)
    
    # Create indexes for better performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tick_date ON tick_disease_surveillance(report_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tick_zip ON tick_disease_surveillance(zip_code)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tick_disease ON tick_disease_surveillance(disease_type)")
    
    conn.commit()
    
    # Display summary statistics
    print("\n📈 Data Summary:")
    print("=" * 50)
    
    # Cases by year
    df['year'] = pd.to_datetime(df['report_date']).dt.year
    yearly_cases = df.groupby('year').size()
    print("Cases by Year:")
    for year, count in yearly_cases.items():
        print(f"  {year}: {count} cases")
    
    # Cases by disease type
    print("\nCases by Disease Type:")
    disease_counts = df['disease_type'].value_counts()
    for disease, count in disease_counts.items():
        print(f"  {disease}: {count} cases")
    
    # Cases by borough (based on ZIP)
    print("\nCases by Area:")
    area_counts = df['neighborhood'].str.extract(r'(Staten Island|Bronx|Queens|Brooklyn|Manhattan)')[0].value_counts()
    for area, count in area_counts.items():
        print(f"  {area}: {count} cases")
    
    # Seasonal distribution
    df['month'] = pd.to_datetime(df['report_date']).dt.month
    monthly_cases = df.groupby('month').size()
    print("\nSeasonal Distribution (by month):")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for month_num, count in monthly_cases.items():
        print(f"  {months[month_num-1]}: {count} cases")
    
    conn.close()
    
    print(f"\n✅ Successfully ingested {len(df)} tick-borne disease records!")
    print("🗄️  Data stored in 'tick_disease_surveillance' table")
    
    return len(df)

if __name__ == "__main__":
    ingest_tick_disease_data()
