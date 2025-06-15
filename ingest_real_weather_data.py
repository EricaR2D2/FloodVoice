import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import requests
import json

def fetch_nyc_temperature_data():
    """Fetch real temperature data from NYC Open Data - Hyperlocal Temperature Monitoring"""
    
    # NYC Open Data API endpoint for Hyperlocal Temperature Monitoring
    api_url = "https://data.cityofnewyork.us/resource/qdq3-9eqn.json"
    
    try:
        print("Fetching real NYC temperature data from NYC Open Data...")
        
        # Fetch recent temperature data
        params = {
            "$limit": 5000,  # Get substantial amount of data
            "$order": "datetime DESC"  # Most recent first
        }
        
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"Retrieved {len(data)} temperature records from NYC Open Data")
        
        if not data:
            print("No temperature data returned from API")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Print available columns to understand the data structure
        print("Available temperature columns:", df.columns.tolist())
        print("Sample temperature record:", df.iloc[0].to_dict() if len(df) > 0 else "No records")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching temperature data from NYC Open Data: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing temperature data: {e}")
        return pd.DataFrame()

def fetch_noaa_weather_data():
    """Fetch real weather data from NOAA API for NYC area"""
    
    # NOAA API endpoint for NYC Central Park weather station
    # Station ID: KNYC (Central Park)
    base_url = "https://api.weather.gov"
    
    try:
        print("Fetching real weather data from NOAA API...")
        
        # Get current conditions for NYC Central Park
        station_url = f"{base_url}/stations/KNYC/observations/latest"
        
        response = requests.get(station_url)
        response.raise_for_status()
        
        data = response.json()
        print("Retrieved current weather data from NOAA")
        
        # Extract weather properties
        properties = data.get('properties', {})
        
        weather_data = {
            'timestamp': properties.get('timestamp'),
            'temperature_c': properties.get('temperature', {}).get('value'),
            'humidity': properties.get('relativeHumidity', {}).get('value'),
            'wind_speed': properties.get('windSpeed', {}).get('value'),
            'wind_direction': properties.get('windDirection', {}).get('value'),
            'barometric_pressure': properties.get('barometricPressure', {}).get('value'),
            'visibility': properties.get('visibility', {}).get('value'),
            'description': properties.get('textDescription')
        }
        
        print("Sample NOAA weather data:", weather_data)
        
        return pd.DataFrame([weather_data])
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data from NOAA: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing NOAA weather data: {e}")
        return pd.DataFrame()

def process_weather_data(temp_df, noaa_df):
    """Process and combine weather data from multiple sources"""
    
    processed_data = []
    
    try:
        # Process NYC temperature monitoring data
        if not temp_df.empty:
            print("Processing NYC temperature monitoring data...")
            
            # Group by location and get recent readings
            for _, row in temp_df.head(50).iterrows():  # Process recent 50 records
                
                # Extract location and temperature info
                location = row.get('location', 'NYC Location')
                temp_f = row.get('temperature_f', 0)
                datetime_str = row.get('datetime', '')
                
                # Convert temperature to Celsius if needed
                try:
                    temp_f = float(temp_f) if temp_f else 0
                    temp_c = (temp_f - 32) * 5/9 if temp_f > 0 else 0
                except (ValueError, TypeError):
                    temp_c = 0
                
                # Calculate tick risk score based on temperature
                # Ticks are most active in temperatures 45-85°F (7-29°C)
                if 7 <= temp_c <= 29:
                    tick_risk_score = min(100, max(0, (temp_c - 7) * 4.5))  # Scale 0-100
                else:
                    tick_risk_score = 0
                
                processed_data.append({
                    "date": datetime_str[:10] if datetime_str else datetime.now().strftime("%Y-%m-%d"),
                    "station_name": f"NYC Temperature Monitor - {location}",
                    "borough": "Manhattan",  # Default to Manhattan for NYC monitors
                    "zip_code": "10019",
                    "latitude": 40.7831,  # Central NYC coordinates
                    "longitude": -73.9712,
                    "temp_avg_f": temp_f,
                    "temp_avg_c": round(temp_c, 2),
                    "humidity_avg": 50,  # Default humidity
                    "tick_risk_score": round(tick_risk_score, 2),
                    "data_source": "NYC Open Data - Temperature Monitoring"
                })
        
        # Process NOAA weather data
        if not noaa_df.empty:
            print("Processing NOAA weather data...")
            
            for _, row in noaa_df.iterrows():
                
                # Extract weather info
                temp_c = row.get('temperature_c', 0)
                humidity = row.get('humidity', 0)
                timestamp = row.get('timestamp', '')
                
                # Convert temperature to Fahrenheit
                try:
                    temp_c = float(temp_c) if temp_c else 0
                    temp_f = (temp_c * 9/5) + 32 if temp_c != 0 else 0
                    humidity = float(humidity) if humidity else 50
                except (ValueError, TypeError):
                    temp_f = 0
                    humidity = 50
                
                # Calculate tick risk score (temperature + humidity factors)
                temp_risk = min(100, max(0, (temp_c - 7) * 4.5)) if 7 <= temp_c <= 29 else 0
                humidity_risk = min(100, max(0, (humidity - 30) * 1.4)) if humidity >= 30 else 0
                tick_risk_score = (temp_risk + humidity_risk) / 2
                
                processed_data.append({
                    "date": timestamp[:10] if timestamp else datetime.now().strftime("%Y-%m-%d"),
                    "station_name": "NOAA Central Park Weather Station",
                    "borough": "Manhattan",
                    "zip_code": "10024",
                    "latitude": 40.7829,
                    "longitude": -73.9654,
                    "temp_avg_f": round(temp_f, 2),
                    "temp_avg_c": round(temp_c, 2),
                    "humidity_avg": round(humidity, 2),
                    "tick_risk_score": round(tick_risk_score, 2),
                    "data_source": "NOAA Weather API"
                })
        
        result_df = pd.DataFrame(processed_data)
        print(f"Processed {len(result_df)} weather records")
        
        return result_df
        
    except Exception as e:
        print(f"Error processing weather data: {e}")
        return pd.DataFrame()

def save_weather_data_to_db(df, db_path='public_health_data.db'):
    """Save weather data to SQLite database"""
    
    if df.empty:
        print("No weather data to save")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Drop existing table and create new one
        conn.execute("DROP TABLE IF EXISTS real_weather_data")
        
        # Create table with proper schema
        create_table_sql = """
        CREATE TABLE real_weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            station_name TEXT NOT NULL,
            borough TEXT NOT NULL,
            zip_code TEXT,
            latitude REAL,
            longitude REAL,
            temp_avg_f REAL,
            temp_avg_c REAL,
            humidity_avg REAL,
            tick_risk_score REAL,
            data_source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        conn.execute(create_table_sql)
        
        # Insert data
        df.to_sql('real_weather_data', conn, if_exists='append', index=False)
        
        conn.commit()
        conn.close()
        
        print(f"Successfully saved {len(df)} weather records to database")
        return True
        
    except Exception as e:
        print(f"Error saving weather data to database: {e}")
        return False

def main():
    """Main function to fetch and process weather data"""
    
    print("=== REAL WEATHER DATA INGESTION ===")
    
    # Fetch temperature data from NYC Open Data
    temp_df = fetch_nyc_temperature_data()
    
    # Fetch weather data from NOAA
    noaa_df = fetch_noaa_weather_data()
    
    if temp_df.empty and noaa_df.empty:
        print("Failed to fetch any weather data")
        return
    
    # Process the data
    processed_df = process_weather_data(temp_df, noaa_df)
    
    if processed_df.empty:
        print("Failed to process weather data")
        return
    
    # Save to database
    success = save_weather_data_to_db(processed_df)
    
    if success:
        print("✅ Real weather data ingestion completed successfully!")
        print(f"📊 Total records: {len(processed_df)}")
        print(f"🌡️ Weather stations: {processed_df['station_name'].nunique()}")
        print(f"📅 Date range: {processed_df['date'].min()} to {processed_df['date'].max()}")
    else:
        print("❌ Failed to complete weather data ingestion")

if __name__ == "__main__":
    main()
