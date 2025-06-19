#!/usr/bin/env python3
"""
Ingest NYC Flu Surveillance Data from NYC Open Data
Emergency Department Visits and Admissions for Influenza-like Illness and/or Pneumonia
"""

import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import requests
import json

def fetch_flu_surveillance_data():
    """Fetch real flu surveillance data from NYC Open Data"""
    
    print("🦠 Fetching NYC Flu Surveillance Data...")
    
    # NYC Open Data API endpoint for Emergency Department Visits - Influenza-like Illness
    api_url = "https://data.cityofnewyork.us/resource/2nwg-uqyg.json"
    
    try:
        print("Fetching flu surveillance data from NYC Open Data...")
        
        # Fetch recent flu surveillance data
        params = {
            "$limit": 50000,  # Get substantial amount of data
            "$order": "date DESC"  # Most recent first
        }
        
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"Retrieved {len(data)} flu surveillance records from NYC Open Data")
        
        if not data:
            print("No flu surveillance data returned from API")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Print available columns to understand the data structure
        print("Available flu surveillance columns:", df.columns.tolist())
        if len(df) > 0:
            print("Sample flu surveillance record:", df.iloc[0].to_dict())
        
        return df
        
    except Exception as e:
        print(f"Error fetching flu surveillance data: {e}")
        return pd.DataFrame()

def process_flu_surveillance_data(df):
    """Process and clean flu surveillance data"""
    
    if df.empty:
        print("No flu surveillance data to process")
        return pd.DataFrame()
    
    print(f"Processing {len(df)} flu surveillance records...")
    
    processed_data = []
    
    for _, row in df.iterrows():
        try:
            # Extract key fields
            date = row.get('date', '')
            extract_date = row.get('extract_date', '')
            mod_zcta = row.get('mod_zcta', '')
            total_ed_visits = row.get('total_ed_visits', 0)
            ili_pne_visits = row.get('ili_pne_visits', 0)
            ili_pne_admissions = row.get('ili_pne_admissions', 0)
            
            # Clean and validate data
            if date and mod_zcta:
                # Convert to proper date format
                date_clean = pd.to_datetime(date).strftime('%Y-%m-%d') if date else None
                
                # Convert numeric fields
                total_visits = int(total_ed_visits) if total_ed_visits else 0
                flu_visits = int(ili_pne_visits) if ili_pne_visits else 0
                flu_admissions = int(ili_pne_admissions) if ili_pne_admissions else 0
                
                # Calculate flu percentage
                flu_percentage = round((flu_visits / total_visits) * 100, 2) if total_visits > 0 else 0
                
                # Map ZIP code to borough (simplified mapping)
                borough = map_zip_to_borough(mod_zcta)
                
                processed_data.append({
                    "date": date_clean,
                    "zip_code": mod_zcta,
                    "borough": borough,
                    "total_ed_visits": total_visits,
                    "flu_like_visits": flu_visits,
                    "flu_admissions": flu_admissions,
                    "flu_percentage": flu_percentage,
                    "extract_date": extract_date,
                    "data_source": "NYC Open Data - Flu Surveillance",
                    "illness_type": "Influenza-like Illness",
                    "created_at": datetime.now().isoformat()
                })
        
        except Exception as e:
            print(f"Error processing flu record: {e}")
            continue
    
    if processed_data:
        processed_df = pd.DataFrame(processed_data)
        print(f"Successfully processed {len(processed_df)} flu surveillance records")
        return processed_df
    else:
        print("No valid flu surveillance records processed")
        return pd.DataFrame()

def map_zip_to_borough(zip_code):
    """Map ZIP code to NYC borough (simplified mapping)"""
    zip_code = str(zip_code)
    
    # Simplified ZIP code to borough mapping
    if zip_code.startswith('100') or zip_code.startswith('101'):
        return 'Manhattan'
    elif zip_code.startswith('102') or zip_code.startswith('103') or zip_code.startswith('104'):
        return 'Bronx'
    elif zip_code.startswith('112') or zip_code.startswith('113') or zip_code.startswith('114'):
        return 'Queens'
    elif zip_code.startswith('110') or zip_code.startswith('111'):
        return 'Brooklyn'
    elif zip_code.startswith('103'):
        return 'Staten Island'
    else:
        return 'Unknown'

def save_flu_surveillance_data(df):
    """Save flu surveillance data to database"""
    
    if df.empty:
        print("No flu surveillance data to save")
        return False
    
    try:
        conn = sqlite3.connect('public_health_data.db')
        
        # Save to database
        df.to_sql('flu_surveillance_data', conn, if_exists='replace', index=False)
        
        print(f"✅ Successfully saved {len(df)} flu surveillance records to database")
        
        # Show summary
        print("\n📊 Flu Surveillance Data Summary:")
        print(f"   Total records: {len(df)}")
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"   ZIP codes: {df['zip_code'].nunique()}")
        print(f"   Boroughs: {df['borough'].nunique()}")
        
        # Show recent data sample
        print("\n📋 Recent flu surveillance data:")
        recent_data = df.head(10)[['date', 'zip_code', 'borough', 'total_ed_visits', 'flu_like_visits', 'flu_percentage']]
        print(recent_data.to_string(index=False))
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error saving flu surveillance data: {e}")
        return False

def main():
    """Main function to ingest flu surveillance data"""
    
    print("=" * 60)
    print("🦠 NYC FLU SURVEILLANCE DATA INGESTION")
    print("=" * 60)
    
    # Fetch data
    flu_df = fetch_flu_surveillance_data()
    
    if not flu_df.empty:
        # Process data
        processed_df = process_flu_surveillance_data(flu_df)
        
        if not processed_df.empty:
            # Save to database
            success = save_flu_surveillance_data(processed_df)
            
            if success:
                print("\n✅ Flu surveillance data ingestion completed successfully!")
                return len(processed_df)
            else:
                print("\n❌ Failed to save flu surveillance data")
                return 0
        else:
            print("\n❌ No valid flu surveillance data processed")
            return 0
    else:
        print("\n❌ No flu surveillance data retrieved")
        return 0

if __name__ == "__main__":
    records_ingested = main()
    print(f"\n🎯 Final result: {records_ingested} flu surveillance records ingested")
