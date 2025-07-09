#!/usr/bin/env python3
"""
Update NYC Flu Surveillance Data to Current Sources
Fetches the latest flu surveillance data from NYC Open Data
"""

import requests
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json

def fetch_current_nyc_flu_data():
    """Fetch current NYC flu surveillance data from Open Data API."""
    
    print("🦠 Fetching Current NYC Flu Surveillance Data...")
    print("-" * 50)
    
    # NYC Open Data API endpoint for flu surveillance
    base_url = "https://data.cityofnewyork.us/resource/2nwg-uqyg.json"
    
    try:
        # Get recent data (last 2 years to ensure we have current data)
        cutoff_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        
        params = {
            "$limit": 50000,
            "$where": f"extract_date >= '{cutoff_date}'",
            "$order": "extract_date DESC"
        }
        
        print(f"Requesting data from: {base_url}")
        print(f"Parameters: {params}")
        
        response = requests.get(base_url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully fetched {len(data)} records")
            
            if data:
                # Convert to DataFrame for easier processing
                df = pd.DataFrame(data)
                print(f"📊 Data columns: {list(df.columns)}")
                
                # Show sample of latest data
                if len(df) > 0:
                    latest_date = df['extract_date'].max() if 'extract_date' in df.columns else 'Unknown'
                    print(f"📅 Latest data date: {latest_date}")
                    
                    # Show sample records
                    print("\n📋 Sample records:")
                    sample_cols = ['extract_date', 'mod_zcta', 'ili_pne_visits', 'ili_pne_admissions'] if all(col in df.columns for col in ['extract_date', 'mod_zcta', 'ili_pne_visits', 'ili_pne_admissions']) else df.columns[:4]
                    print(df[sample_cols].head(3).to_string(index=False))
                
                return df
            else:
                print("⚠️ No data returned from API")
                return pd.DataFrame()
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ Error fetching flu data: {e}")
        return pd.DataFrame()

def process_flu_data(df):
    """Process and clean the flu surveillance data."""
    
    if df.empty:
        print("⚠️ No data to process")
        return pd.DataFrame()
    
    print("\n🔄 Processing flu surveillance data...")
    
    processed_records = []
    
    for _, row in df.iterrows():
        try:
            # Extract key fields (adjust based on actual API response structure)
            extract_date = row.get('extract_date', '')
            mod_zcta = row.get('mod_zcta', '')  # Modified ZIP code
            ili_pne_visits = row.get('ili_pne_visits', 0)
            ili_pne_admissions = row.get('ili_pne_admissions', 0)
            total_ed_visits = row.get('total_ed_visits', 0)
            
            # Clean and validate data
            if extract_date and mod_zcta:
                # Convert date format
                try:
                    date_clean = pd.to_datetime(extract_date).strftime('%Y-%m-%d')
                except:
                    date_clean = extract_date[:10] if len(extract_date) >= 10 else extract_date
                
                # Clean ZIP code (remove any prefixes/suffixes)
                zip_code = str(mod_zcta).strip()
                if len(zip_code) > 5:
                    zip_code = zip_code[:5]
                
                # Convert numeric fields
                try:
                    flu_visits = int(float(ili_pne_visits)) if ili_pne_visits else 0
                    flu_admissions = int(float(ili_pne_admissions)) if ili_pne_admissions else 0
                    total_visits = int(float(total_ed_visits)) if total_ed_visits else max(flu_visits, 1)
                except:
                    flu_visits = 0
                    flu_admissions = 0
                    total_visits = 1
                
                # Calculate flu percentage
                flu_percentage = (flu_visits / total_visits * 100) if total_visits > 0 else 0
                
                # Map ZIP to borough (simplified mapping)
                borough = map_zip_to_borough(zip_code)
                
                processed_record = {
                    'date': date_clean,
                    'zip_code': zip_code,
                    'borough': borough,
                    'total_ed_visits': total_visits,
                    'flu_like_visits': flu_visits,
                    'flu_admissions': flu_admissions,
                    'flu_percentage': round(flu_percentage, 2),
                    'extract_date': extract_date,
                    'data_source': 'NYC Open Data - Current Flu Surveillance',
                    'illness_type': 'Influenza-like Illness',
                    'created_at': datetime.now().isoformat()
                }
                
                processed_records.append(processed_record)
                
        except Exception as e:
            print(f"Error processing record: {e}")
            continue
    
    if processed_records:
        result_df = pd.DataFrame(processed_records)
        print(f"✅ Processed {len(result_df)} records")
        return result_df
    else:
        print("⚠️ No records could be processed")
        return pd.DataFrame()

def map_zip_to_borough(zip_code):
    """Map ZIP code to NYC borough."""
    
    # Simplified ZIP to borough mapping
    zip_borough_map = {
        # Bronx: 104xx, 105xx
        '104': 'Bronx', '105': 'Bronx',
        # Brooklyn: 112xx, 113xx
        '112': 'Brooklyn', '113': 'Brooklyn',
        # Manhattan: 100xx, 101xx, 102xx
        '100': 'Manhattan', '101': 'Manhattan', '102': 'Manhattan',
        # Queens: 110xx, 111xx, 113xx, 114xx, 116xx
        '110': 'Queens', '111': 'Queens', '114': 'Queens', '116': 'Queens',
        # Staten Island: 103xx
        '103': 'Staten Island'
    }
    
    if len(zip_code) >= 3:
        prefix = zip_code[:3]
        return zip_borough_map.get(prefix, 'Unknown')
    
    return 'Unknown'

def update_flu_surveillance_database(df):
    """Update the database with current flu surveillance data."""
    
    if df.empty:
        print("⚠️ No data to update in database")
        return
    
    print(f"\n💾 Updating database with {len(df)} flu surveillance records...")
    
    conn = sqlite3.connect('public_health_data.db')
    cursor = conn.cursor()
    
    try:
        # Clear old flu surveillance data
        cursor.execute("DELETE FROM flu_surveillance_data WHERE data_source LIKE '%Flu Surveillance%'")
        old_count = cursor.rowcount
        print(f"🗑️ Removed {old_count} old flu surveillance records")
        
        # Insert new data
        df.to_sql('flu_surveillance_data', conn, if_exists='append', index=False)
        print(f"✅ Inserted {len(df)} new flu surveillance records")
        
        # Verify the update
        cursor.execute("""
            SELECT COUNT(*) as count, MIN(date) as earliest, MAX(date) as latest
            FROM flu_surveillance_data
            WHERE data_source = 'NYC Open Data - Current Flu Surveillance'
        """)
        
        result = cursor.fetchone()
        print(f"📊 Verification: {result[0]} records from {result[1]} to {result[2]}")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Database update error: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Main function to update flu surveillance data."""
    
    print("🔄 NYC FLU SURVEILLANCE DATA UPDATE")
    print("=" * 60)
    
    # Step 1: Fetch current data
    flu_df = fetch_current_nyc_flu_data()
    
    if not flu_df.empty:
        # Step 2: Process the data
        processed_df = process_flu_data(flu_df)
        
        if not processed_df.empty:
            # Step 3: Update database
            update_flu_surveillance_database(processed_df)
            
            print("\n✅ Flu surveillance data update complete!")
            print(f"📊 Updated with {len(processed_df)} current records")
        else:
            print("❌ No processed data to update")
    else:
        print("❌ No flu data fetched - update failed")

if __name__ == "__main__":
    main()
