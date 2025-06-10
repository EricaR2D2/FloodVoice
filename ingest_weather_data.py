#!/usr/bin/env python3
"""
NYC Weather Data Ingestion
Historical weather data for correlation with tick-borne disease patterns
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json

def create_historical_weather_data():
    """
    Create realistic NYC weather data for correlation analysis
    Based on NYC climate patterns and seasonal variations
    """
    
    # NYC weather stations (approximate locations)
    weather_stations = {
        'NYC_CENTRAL_PARK': {'lat': 40.7829, 'lon': -73.9654, 'name': 'Central Park'},
        'NYC_LAGUARDIA': {'lat': 40.7769, 'lon': -73.8740, 'name': 'LaGuardia Airport'},
        'NYC_JFK': {'lat': 40.6413, 'lon': -73.7781, 'name': 'JFK Airport'},
        'NYC_BROOKLYN': {'lat': 40.6501, 'lon': -73.9496, 'name': 'Brooklyn'},
        'NYC_STATEN_ISLAND': {'lat': 40.5795, 'lon': -74.1502, 'name': 'Staten Island'}
    }
    
    # Generate 3 years of daily weather data (2022-2024)
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    records = []
    
    current_date = start_date
    while current_date <= end_date:
        day_of_year = current_date.timetuple().tm_yday
        
        # Seasonal temperature patterns for NYC
        # Winter: 20-45°F, Spring: 45-70°F, Summer: 65-85°F, Fall: 45-70°F
        base_temp = 55 + 25 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
        
        for station_id, station_info in weather_stations.items():
            # Add some station-specific variation
            station_temp_offset = np.random.normal(0, 2)
            
            # Daily temperature with realistic variation
            temp_high = base_temp + np.random.normal(5, 8) + station_temp_offset
            temp_low = temp_high - np.random.normal(15, 5)
            temp_avg = (temp_high + temp_low) / 2
            
            # Ensure realistic bounds
            temp_high = max(-5, min(100, temp_high))
            temp_low = max(-15, min(temp_high - 5, temp_low))
            temp_avg = (temp_high + temp_low) / 2
            
            # Precipitation (more in spring/summer, less in winter)
            precip_base_prob = 0.3 + 0.2 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
            has_precip = np.random.random() < precip_base_prob
            
            if has_precip:
                # Precipitation amount (inches)
                precip_amount = np.random.exponential(0.3)
                precip_amount = min(3.0, precip_amount)  # Cap at 3 inches
            else:
                precip_amount = 0.0
            
            # Humidity (higher in summer, lower in winter)
            base_humidity = 60 + 20 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
            humidity = max(20, min(95, base_humidity + np.random.normal(0, 10)))
            
            # Wind speed
            wind_speed = max(0, np.random.gamma(2, 3))  # mph
            
            # Weather conditions
            if precip_amount > 0.5:
                condition = 'Rain'
            elif precip_amount > 0:
                condition = 'Light Rain'
            elif humidity > 80:
                condition = 'Cloudy'
            elif np.random.random() < 0.3:
                condition = 'Partly Cloudy'
            else:
                condition = 'Clear'
            
            # Tick activity risk calculation
            # Ticks active when temp > 45°F and humidity > 50%
            tick_risk_score = 0
            if temp_avg > 45:  # Above freezing threshold
                tick_risk_score += 30
            if temp_avg > 60:  # Optimal temperature
                tick_risk_score += 40
            if humidity > 50:  # Sufficient humidity
                tick_risk_score += 20
            if humidity > 70:  # High humidity
                tick_risk_score += 10
            
            # Seasonal bonus (peak tick season)
            month = current_date.month
            if 5 <= month <= 9:  # May-September
                tick_risk_score += 20
            elif month in [4, 10]:  # April, October
                tick_risk_score += 10
            
            tick_risk_score = min(100, tick_risk_score)
            
            record = {
                'date': current_date.strftime('%Y-%m-%d'),
                'station_id': station_id,
                'station_name': station_info['name'],
                'latitude': station_info['lat'],
                'longitude': station_info['lon'],
                'temp_high_f': round(temp_high, 1),
                'temp_low_f': round(temp_low, 1),
                'temp_avg_f': round(temp_avg, 1),
                'precipitation_in': round(precip_amount, 2),
                'humidity_percent': round(humidity, 1),
                'wind_speed_mph': round(wind_speed, 1),
                'weather_condition': condition,
                'tick_risk_score': tick_risk_score
            }
            
            records.append(record)
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(records)

def ingest_weather_data():
    """Ingest weather data into the database"""
    
    print("🌡️ Generating NYC Weather Data for Tick-Disease Correlation...")
    
    # Generate the dataset
    df = create_historical_weather_data()
    
    print(f"📊 Generated {len(df)} weather observations")
    print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"🏢 Weather stations: {df['station_name'].unique()}")
    print(f"🌡️ Temperature range: {df['temp_avg_f'].min():.1f}°F to {df['temp_avg_f'].max():.1f}°F")
    
    # Connect to database
    conn = sqlite3.connect('public_health_data.db')
    
    # Create table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        station_id TEXT,
        station_name TEXT,
        latitude REAL,
        longitude REAL,
        temp_high_f REAL,
        temp_low_f REAL,
        temp_avg_f REAL,
        precipitation_in REAL,
        humidity_percent REAL,
        wind_speed_mph REAL,
        weather_condition TEXT,
        tick_risk_score INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    conn.execute(create_table_sql)
    
    # Insert data
    df.to_sql('weather_data', conn, if_exists='replace', index=False)
    
    # Create indexes for better performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_weather_date ON weather_data(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_weather_station ON weather_data(station_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_weather_temp ON weather_data(temp_avg_f)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_weather_risk ON weather_data(tick_risk_score)")
    
    conn.commit()
    
    # Display summary statistics
    print("\n📈 Weather Data Summary:")
    print("=" * 50)
    
    # Average conditions by season
    df['date_parsed'] = pd.to_datetime(df['date'])
    df['month'] = df['date_parsed'].dt.month
    df['season'] = df['month'].map({
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    })
    
    seasonal_stats = df.groupby('season').agg({
        'temp_avg_f': 'mean',
        'precipitation_in': 'mean',
        'humidity_percent': 'mean',
        'tick_risk_score': 'mean'
    }).round(1)
    
    print("Seasonal Averages:")
    for season in ['Spring', 'Summer', 'Fall', 'Winter']:
        if season in seasonal_stats.index:
            stats = seasonal_stats.loc[season]
            print(f"  {season}:")
            print(f"    Temperature: {stats['temp_avg_f']}°F")
            print(f"    Precipitation: {stats['precipitation_in']} inches")
            print(f"    Humidity: {stats['humidity_percent']}%")
            print(f"    Tick Risk Score: {stats['tick_risk_score']}")
    
    # High tick risk days
    high_risk_days = len(df[df['tick_risk_score'] >= 70])
    total_days = len(df['date'].unique())
    print(f"\nTick Activity Analysis:")
    print(f"  High risk days (score ≥70): {high_risk_days} ({high_risk_days/total_days*100:.1f}%)")
    print(f"  Peak risk months: {df[df['tick_risk_score'] >= 80]['month'].value_counts().head(3).to_dict()}")
    
    conn.close()
    
    print(f"\n✅ Successfully ingested {len(df)} weather records!")
    print("🗄️  Data stored in 'weather_data' table")
    
    return len(df)

if __name__ == "__main__":
    ingest_weather_data()
