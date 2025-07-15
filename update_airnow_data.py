#!/usr/bin/env python3
"""
EPA AirNow API Integration for NYC Public Health MVP
Updates air quality data with current EPA AirNow real-time data
"""

import requests
import pandas as pd
import sqlite3
import json
from datetime import datetime, timedelta
import time

# EPA AirNow API configuration
# Get a free API key at: https://docs.airnowapi.org/
AIRNOW_API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key
AIRNOW_BASE_URL = "http://www.airnowapi.org/aq"

def fetch_current_air_quality():
    """
    Fetch current air quality data from EPA AirNow API for NYC area
    """
    print("🌬️ Fetching current air quality data from EPA AirNow...")
    
    # NYC area coordinates and monitoring locations
    nyc_locations = [
        {"name": "Manhattan", "lat": 40.7831, "lon": -73.9712, "zip": "10001", "borough": "Manhattan"},
        {"name": "Brooklyn", "lat": 40.6782, "lon": -73.9442, "zip": "11201", "borough": "Brooklyn"},
        {"name": "Queens", "lat": 40.7282, "lon": -73.7949, "zip": "11101", "borough": "Queens"},
        {"name": "Bronx", "lat": 40.8448, "lon": -73.8648, "zip": "10451", "borough": "Bronx"},
        {"name": "Staten Island", "lat": 40.5795, "lon": -74.1502, "zip": "10301", "borough": "Staten Island"}
    ]
    
    all_data = []
    
    for location in nyc_locations:
        try:
            # Get current observations by lat/lon
            params = {
                "format": "application/json",
                "latitude": location["lat"],
                "longitude": location["lon"],
                "distance": 25,  # 25 miles radius
                "API_KEY": AIRNOW_API_KEY
            }
            
            url = f"{AIRNOW_BASE_URL}/observation/latLong/current/"
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                for record in data:
                    record['location_name'] = location['name']
                    record['zip_code'] = location['zip']
                    record['borough'] = location['borough']
                all_data.extend(data)
                print(f"✅ Retrieved {len(data)} records for {location['name']}")
            else:
                print(f"⚠️ Error fetching data for {location['name']}: HTTP {response.status_code}")
            
            # Rate limiting - be respectful to the API
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error fetching AirNow data for {location['name']}: {e}")
            continue
    
    if all_data:
        df = pd.DataFrame(all_data)
        print(f"📊 Total AirNow records retrieved: {len(df)}")
        return df
    else:
        print("❌ No AirNow data retrieved")
        return pd.DataFrame()

def process_air_quality_data(df):
    """
    Process EPA AirNow data to match our database schema
    """
    if df.empty:
        print("No air quality data to process")
        return pd.DataFrame()
    
    print(f"🔄 Processing {len(df)} air quality records...")
    
    processed_data = []
    
    for _, row in df.iterrows():
        try:
            # Extract key fields
            date_observed = row.get('DateObserved', '')
            hour_observed = row.get('HourObserved', 0)
            parameter_name = row.get('ParameterName', '')
            aqi_value = row.get('AQI', 0)
            category_info = row.get('Category', {})
            category_name = category_info.get('Name', 'Unknown') if isinstance(category_info, dict) else str(category_info)
            location_name = row.get('location_name', 'Unknown')
            zip_code = row.get('zip_code', '00000')
            borough = row.get('borough', 'Unknown')
            
            # Parse date
            try:
                if date_observed:
                    date_clean = datetime.strptime(date_observed, '%Y-%m-%d').strftime('%Y-%m-%d')
                else:
                    date_clean = datetime.now().strftime('%Y-%m-%d')
            except ValueError:
                date_clean = datetime.now().strftime('%Y-%m-%d')
            
            # Determine health risk level based on AQI
            def get_health_risk_level(aqi):
                if aqi <= 50:
                    return 'LOW'
                elif aqi <= 100:
                    return 'MEDIUM'
                elif aqi <= 150:
                    return 'HIGH'
                else:
                    return 'HAZARDOUS'
            
            # Convert AQI to numeric
            try:
                aqi_numeric = int(aqi_value) if aqi_value else 0
            except (ValueError, TypeError):
                aqi_numeric = 0
            
            processed_record = {
                "date": date_clean,
                "zip_code": zip_code,
                "borough": borough,
                "geo_type": "ZIP_CODE",
                "geo_id": zip_code,
                "location_name": location_name,
                "pollutant_type": "Air Quality Index",
                "pollutant_name": parameter_name,
                "measure_type": "AQI",
                "measure_info": f"Measured at hour {hour_observed}",
                "pollutant_value": float(aqi_numeric),
                "health_risk_level": get_health_risk_level(aqi_numeric),
                "time_period": f"{date_clean} {hour_observed:02d}:00",
                "data_source": "EPA AirNow API - Current Observations",
                "illness_type": "Air Quality Related",
                "created_at": datetime.now().isoformat()
            }
            
            processed_data.append(processed_record)
            
        except Exception as e:
            print(f"❌ Error processing air quality record: {e}")
            continue
    
    if processed_data:
        processed_df = pd.DataFrame(processed_data)
        print(f"✅ Successfully processed {len(processed_df)} air quality records")
        return processed_df
    else:
        print("❌ No valid air quality records processed")
        return pd.DataFrame()

def create_air_quality_summary(df):
    """
    Create air quality summary data for dashboard display
    """
    if df.empty:
        return pd.DataFrame()
    
    print("📋 Creating air quality summary...")
    
    summary_data = []
    
    # Group by location and calculate summary statistics
    for (location, borough), group in df.groupby(['location_name', 'borough']):
        try:
            # Calculate average AQI
            avg_aqi = group['pollutant_value'].mean()
            max_aqi = group['pollutant_value'].max()
            latest_date = group['date'].max()

            # Count unhealthy days (AQI > 100)
            unhealthy_count = len(group[group['pollutant_value'] > 100])
            total_measurements = len(group)
            unhealthy_percentage = (unhealthy_count / total_measurements * 100) if total_measurements > 0 else 0
            
            # Determine overall risk level
            if avg_aqi <= 50:
                risk_level = 'LOW'
                air_quality_score = avg_aqi
            elif avg_aqi <= 100:
                risk_level = 'MEDIUM'
                air_quality_score = avg_aqi
            else:
                risk_level = 'HIGH'
                air_quality_score = avg_aqi
            
            # Get representative ZIP code
            zip_code = group['zip_code'].iloc[0]
            
            summary_record = {
                "location_name": location,
                "zip_code": zip_code,
                "borough": borough,
                "avg_pm25": round(avg_aqi, 2),  # Using AQI as PM2.5 equivalent for now
                "avg_ozone": round(avg_aqi * 0.8, 2),  # Estimated ozone based on AQI
                "total_measurements": total_measurements,
                "unhealthy_days": unhealthy_count,
                "unhealthy_percentage": round(unhealthy_percentage, 2),
                "air_quality_score": round(air_quality_score, 2),
                "risk_level": risk_level,
                "latest_measurement": latest_date,
                "data_source": "EPA AirNow Current Data",
                "created_at": datetime.now().isoformat()
            }
            
            summary_data.append(summary_record)
            
        except Exception as e:
            print(f"❌ Error creating summary for {location}: {e}")
            continue
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        print(f"✅ Created air quality summary for {len(summary_df)} locations")
        return summary_df
    else:
        return pd.DataFrame()

def save_air_quality_data(air_quality_df, summary_df, db_path='public_health_data.db'):
    """
    Save processed air quality data to database
    """
    if air_quality_df.empty and summary_df.empty:
        print("❌ No air quality data to save")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Clear existing air quality data and replace with current EPA data
        print("🔄 Updating air quality data...")
        
        if not air_quality_df.empty:
            # Clear and replace enhanced_air_quality_data table
            conn.execute("DELETE FROM enhanced_air_quality_data")
            air_quality_df.to_sql('enhanced_air_quality_data', conn, if_exists='append', index=False)
            print(f"✅ Updated enhanced_air_quality_data with {len(air_quality_df)} records")
        
        if not summary_df.empty:
            # Clear and replace air_quality_summary table
            conn.execute("DELETE FROM air_quality_summary")
            summary_df.to_sql('air_quality_summary', conn, if_exists='append', index=False)
            print(f"✅ Updated air_quality_summary with {len(summary_df)} records")
        
        conn.commit()
        conn.close()
        
        print("✅ Successfully updated air quality data in database")
        return True
        
    except Exception as e:
        print(f"❌ Error saving air quality data: {e}")
        return False

def main():
    """Main function to update air quality data with EPA AirNow"""
    
    print("=" * 60)
    print("🌬️ EPA AIRNOW AIR QUALITY DATA UPDATE")
    print("=" * 60)
    
    if AIRNOW_API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️ Please set your EPA AirNow API key in the script")
        print("📝 Get a free API key at: https://docs.airnowapi.org/")
        print("💡 Or run without API key to use mock current data")
        
        # Create mock current data for demo purposes
        print("\n🔄 Creating mock current air quality data for demo...")
        mock_data = create_mock_current_data()
        if not mock_data.empty:
            summary_data = create_air_quality_summary(mock_data)
            success = save_air_quality_data(mock_data, summary_data)
            if success:
                print("✅ Mock current air quality data created successfully!")
                return len(mock_data)
        return 0
    
    # Fetch current air quality data
    air_quality_df = fetch_current_air_quality()
    
    if not air_quality_df.empty:
        # Process data
        processed_df = process_air_quality_data(air_quality_df)
        
        if not processed_df.empty:
            # Create summary
            summary_df = create_air_quality_summary(processed_df)
            
            # Save to database
            success = save_air_quality_data(processed_df, summary_df)
            
            if success:
                print("\n✅ EPA AirNow air quality data update completed successfully!")
                print(f"📊 Updated {len(processed_df)} air quality records")
                print("🔄 Air quality data is now current!")
                return len(processed_df)
            else:
                print("\n❌ Failed to save air quality data")
                return 0
        else:
            print("\n❌ No valid air quality data processed")
            return 0
    else:
        print("\n❌ No air quality data retrieved from EPA AirNow")
        return 0

def create_mock_current_data():
    """Create mock current air quality data for demo purposes"""
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    mock_data = [
        {"date": current_date, "zip_code": "10001", "borough": "Manhattan", "geo_type": "ZIP_CODE", "geo_id": "10001",
         "location_name": "Manhattan", "pollutant_type": "Air Quality Index", "pollutant_name": "PM2.5",
         "measure_type": "AQI", "measure_info": "Measured at hour 12", "pollutant_value": 45.0,
         "health_risk_level": "LOW", "time_period": f"{current_date} 12:00", "data_source": "EPA AirNow (Demo)",
         "illness_type": "Air Quality Related", "created_at": datetime.now().isoformat()},

        {"date": current_date, "zip_code": "11201", "borough": "Brooklyn", "geo_type": "ZIP_CODE", "geo_id": "11201",
         "location_name": "Brooklyn", "pollutant_type": "Air Quality Index", "pollutant_name": "PM2.5",
         "measure_type": "AQI", "measure_info": "Measured at hour 12", "pollutant_value": 52.0,
         "health_risk_level": "MEDIUM", "time_period": f"{current_date} 12:00", "data_source": "EPA AirNow (Demo)",
         "illness_type": "Air Quality Related", "created_at": datetime.now().isoformat()},

        {"date": current_date, "zip_code": "11101", "borough": "Queens", "geo_type": "ZIP_CODE", "geo_id": "11101",
         "location_name": "Queens", "pollutant_type": "Air Quality Index", "pollutant_name": "PM2.5",
         "measure_type": "AQI", "measure_info": "Measured at hour 12", "pollutant_value": 38.0,
         "health_risk_level": "LOW", "time_period": f"{current_date} 12:00", "data_source": "EPA AirNow (Demo)",
         "illness_type": "Air Quality Related", "created_at": datetime.now().isoformat()},

        {"date": current_date, "zip_code": "10451", "borough": "Bronx", "geo_type": "ZIP_CODE", "geo_id": "10451",
         "location_name": "Bronx", "pollutant_type": "Air Quality Index", "pollutant_name": "PM2.5",
         "measure_type": "AQI", "measure_info": "Measured at hour 12", "pollutant_value": 48.0,
         "health_risk_level": "LOW", "time_period": f"{current_date} 12:00", "data_source": "EPA AirNow (Demo)",
         "illness_type": "Air Quality Related", "created_at": datetime.now().isoformat()},

        {"date": current_date, "zip_code": "10301", "borough": "Staten Island", "geo_type": "ZIP_CODE", "geo_id": "10301",
         "location_name": "Staten Island", "pollutant_type": "Air Quality Index", "pollutant_name": "PM2.5",
         "measure_type": "AQI", "measure_info": "Measured at hour 12", "pollutant_value": 41.0,
         "health_risk_level": "LOW", "time_period": f"{current_date} 12:00", "data_source": "EPA AirNow (Demo)",
         "illness_type": "Air Quality Related", "created_at": datetime.now().isoformat()}
    ]
    
    return pd.DataFrame(mock_data)

if __name__ == "__main__":
    main()
