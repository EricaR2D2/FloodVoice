import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import requests
import json

def fetch_emergency_department_data():
    """Fetch real emergency department visit data from NYC Open Data"""
    
    # NYC Open Data API endpoint for Emergency Department Visits
    # Emergency Department Visits and Admissions for Influenza-like Illness and/or Pneumonia
    api_url = "https://data.cityofnewyork.us/resource/2nwg-uqyg.json"
    
    try:
        print("Fetching real Emergency Department data from NYC Open Data...")
        
        # Fetch data with limit to get recent records
        params = {
            "$limit": 10000,  # Get substantial amount of data
            "$order": "date DESC"  # Most recent first
        }
        
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"Retrieved {len(data)} records from NYC Open Data")
        
        if not data:
            print("No data returned from API")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Print available columns to understand the data structure
        print("Available columns:", df.columns.tolist())
        print("Sample record:", df.iloc[0].to_dict() if len(df) > 0 else "No records")
        
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from NYC Open Data: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error processing emergency department data: {e}")
        return pd.DataFrame()

def process_emergency_department_data(df):
    """Process the raw emergency department data into our format"""
    
    if df.empty:
        print("No data to process")
        return pd.DataFrame()
    
    try:
        # Map NYC hospitals with approximate coordinates for major medical centers
        hospital_locations = {
            "Bronx": {"lat": 40.8448, "lon": -73.8648, "zip_code": "10451"},
            "Brooklyn": {"lat": 40.6782, "lon": -73.9442, "zip_code": "11201"}, 
            "Manhattan": {"lat": 40.7831, "lon": -73.9712, "zip_code": "10019"},
            "Queens": {"lat": 40.7282, "lon": -73.7949, "zip_code": "11368"},
            "Staten Island": {"lat": 40.5795, "lon": -74.1502, "zip_code": "10305"}
        }
        
        processed_data = []
        
        for _, row in df.iterrows():
            # Extract date and borough information
            date_str = row.get('date', '')
            
            # Process each borough if data is borough-level
            for borough, location in hospital_locations.items():
                # Look for borough-specific columns or total visits
                total_visits_col = f"{borough.lower()}_total_ed_visits" if f"{borough.lower()}_total_ed_visits" in df.columns else "total_ed_visits"
                ili_visits_col = f"{borough.lower()}_ili_pne_visits" if f"{borough.lower()}_ili_pne_visits" in df.columns else "ili_pne_visits"
                
                total_visits = row.get(total_visits_col, 0)
                respiratory_visits = row.get(ili_visits_col, 0)
                
                # Convert to numeric, handle missing values
                try:
                    total_visits = float(total_visits) if total_visits else 0
                    respiratory_visits = float(respiratory_visits) if respiratory_visits else 0
                except (ValueError, TypeError):
                    continue
                
                if total_visits > 0:  # Only include records with actual visit data
                    respiratory_percentage = (respiratory_visits / total_visits) * 100 if total_visits > 0 else 0
                    
                    processed_data.append({
                        "date": date_str,
                        "hospital_name": f"{borough} Medical Center",
                        "borough": borough,
                        "zip_code": location["zip_code"],
                        "latitude": location["lat"],
                        "longitude": location["lon"],
                        "total_visits": int(total_visits),
                        "respiratory_visits": int(respiratory_visits),
                        "respiratory_percentage": round(respiratory_percentage, 2),
                        "data_source": "NYC Open Data - Emergency Department Visits"
                    })
        
        result_df = pd.DataFrame(processed_data)
        print(f"Processed {len(result_df)} hospital records")
        
        return result_df
        
    except Exception as e:
        print(f"Error processing emergency department data: {e}")
        return pd.DataFrame()

def save_emergency_data_to_db(df, db_path='public_health_data.db'):
    """Save emergency department data to SQLite database"""
    
    if df.empty:
        print("No emergency department data to save")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        
        # Drop existing table and create new one
        conn.execute("DROP TABLE IF EXISTS real_hospital_data")
        
        # Create table with proper schema
        create_table_sql = """
        CREATE TABLE real_hospital_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            hospital_name TEXT NOT NULL,
            borough TEXT NOT NULL,
            zip_code TEXT,
            latitude REAL,
            longitude REAL,
            total_visits INTEGER,
            respiratory_visits INTEGER,
            respiratory_percentage REAL,
            data_source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        conn.execute(create_table_sql)
        
        # Insert data
        df.to_sql('real_hospital_data', conn, if_exists='append', index=False)
        
        conn.commit()
        conn.close()
        
        print(f"Successfully saved {len(df)} emergency department records to database")
        return True
        
    except Exception as e:
        print(f"Error saving emergency department data to database: {e}")
        return False

def main():
    """Main function to fetch and process emergency department data"""
    
    print("=== REAL EMERGENCY DEPARTMENT DATA INGESTION ===")
    
    # Fetch data from NYC Open Data
    raw_df = fetch_emergency_department_data()
    
    if raw_df.empty:
        print("Failed to fetch emergency department data")
        return
    
    # Process the data
    processed_df = process_emergency_department_data(raw_df)
    
    if processed_df.empty:
        print("Failed to process emergency department data")
        return
    
    # Save to database
    success = save_emergency_data_to_db(processed_df)
    
    if success:
        print("✅ Real emergency department data ingestion completed successfully!")
        print(f"📊 Total records: {len(processed_df)}")
        print(f"🏥 Hospitals: {processed_df['hospital_name'].nunique()}")
        print(f"📅 Date range: {processed_df['date'].min()} to {processed_df['date'].max()}")
    else:
        print("❌ Failed to complete emergency department data ingestion")

if __name__ == "__main__":
    main()
