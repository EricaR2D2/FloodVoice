#!/usr/bin/env python3
"""
Ingest Enhanced NYC Air Quality Data from NYC Open Data
NYCCAS Air Pollution Rasters and Air Quality Surveillance Data
"""

import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import requests
import json

def fetch_nyc_air_quality_data():
    """Fetch NYC air quality surveillance data from NYC Open Data"""
    
    print("🌬️ Fetching NYC Air Quality Surveillance Data...")
    
    # NYC Open Data API endpoint for Air Quality
    api_url = "https://data.cityofnewyork.us/resource/c3uy-2p5r.json"
    
    try:
        print("Fetching air quality surveillance data from NYC Open Data...")
        
        # Fetch air quality surveillance data
        params = {
            "$limit": 50000,  # Get substantial amount of data
            "$order": "start_date DESC"  # Most recent first
        }
        
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"Retrieved {len(data)} air quality surveillance records from NYC Open Data")
        
        if not data:
            print("No air quality surveillance data returned from API")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Print available columns to understand the data structure
        print("Available air quality surveillance columns:", df.columns.tolist())
        if len(df) > 0:
            print("Sample air quality surveillance record:", df.iloc[0].to_dict())
        
        return df
        
    except Exception as e:
        print(f"Error fetching air quality surveillance data: {e}")
        return pd.DataFrame()

def fetch_nyccas_pollution_data():
    """Fetch NYCCAS Air Pollution Rasters data"""
    
    print("🌫️ Fetching NYCCAS Air Pollution Rasters Data...")
    
    # NYC Open Data API endpoint for NYCCAS Air Pollution Rasters
    api_url = "https://data.cityofnewyork.us/resource/q68s-8qxv.json"
    
    try:
        print("Fetching NYCCAS pollution raster data from NYC Open Data...")
        
        # Fetch pollution raster data
        params = {
            "$limit": 50000,  # Get substantial amount of data
        }
        
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"Retrieved {len(data)} NYCCAS pollution records from NYC Open Data")
        
        if not data:
            print("No NYCCAS pollution data returned from API")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Print available columns to understand the data structure
        print("Available NYCCAS pollution columns:", df.columns.tolist())
        if len(df) > 0:
            print("Sample NYCCAS pollution record:", df.iloc[0].to_dict())
        
        return df
        
    except Exception as e:
        print(f"Error fetching NYCCAS pollution data: {e}")
        return pd.DataFrame()

def process_air_quality_data(surveillance_df, pollution_df):
    """Process and clean air quality data"""
    
    processed_data = []
    
    # Process surveillance data
    if not surveillance_df.empty:
        print(f"Processing {len(surveillance_df)} air quality surveillance records...")
        
        for _, row in surveillance_df.iterrows():
            try:
                # Extract key fields
                unique_id = row.get('unique_id', '')
                indicator_id = row.get('indicator_id', '')
                name = row.get('name', '')
                measure = row.get('measure', '')
                measure_info = row.get('measure_info', '')
                geo_type_name = row.get('geo_type_name', '')
                geo_join_id = row.get('geo_join_id', '')
                geo_place_name = row.get('geo_place_name', '')
                time_period = row.get('time_period', '')
                start_date = row.get('start_date', '')
                data_value = row.get('data_value', '')
                
                # Clean and validate data
                if start_date and geo_join_id and data_value:
                    # Convert to proper date format
                    date_clean = pd.to_datetime(start_date).strftime('%Y-%m-%d') if start_date else None
                    
                    # Convert data value to numeric
                    numeric_value = 0
                    try:
                        numeric_value = float(data_value) if data_value else 0
                    except:
                        numeric_value = 0
                    
                    # Determine pollutant type and health risk
                    pollutant_type = determine_pollutant_type(name, measure)
                    health_risk_level = determine_health_risk_level(pollutant_type, numeric_value)
                    
                    # Map geo_join_id to ZIP code if possible
                    zip_code = map_geo_to_zip(geo_join_id, geo_type_name)
                    borough = map_geo_to_borough(geo_place_name, geo_type_name)
                    
                    processed_data.append({
                        "date": date_clean,
                        "zip_code": zip_code,
                        "borough": borough,
                        "geo_type": geo_type_name,
                        "geo_id": geo_join_id,
                        "location_name": geo_place_name,
                        "pollutant_type": pollutant_type,
                        "pollutant_name": name,
                        "measure_type": measure,
                        "measure_info": measure_info[:200] if measure_info else "",
                        "pollutant_value": numeric_value,
                        "health_risk_level": health_risk_level,
                        "time_period": time_period,
                        "data_source": "NYC Air Quality Surveillance",
                        "illness_type": "Air Quality Related",
                        "created_at": datetime.now().isoformat()
                    })
            
            except Exception as e:
                print(f"Error processing air quality surveillance record: {e}")
                continue
    
    # Process NYCCAS pollution data
    if not pollution_df.empty:
        print(f"Processing {len(pollution_df)} NYCCAS pollution records...")
        
        for _, row in pollution_df.iterrows():
            try:
                # Extract key fields from NYCCAS data
                # Note: This will depend on the actual structure of the NYCCAS data
                # We'll add this processing once we see the data structure
                pass
            
            except Exception as e:
                print(f"Error processing NYCCAS pollution record: {e}")
                continue
    
    if processed_data:
        processed_df = pd.DataFrame(processed_data)
        print(f"Successfully processed {len(processed_df)} air quality records")
        return processed_df
    else:
        print("No valid air quality records processed")
        return pd.DataFrame()

def determine_pollutant_type(name, measure):
    """Determine pollutant type from name and measure"""
    
    name_lower = name.lower() if name else ""
    measure_lower = measure.lower() if measure else ""
    
    if "pm2.5" in name_lower or "fine particles" in name_lower:
        return "PM2.5"
    elif "pm10" in name_lower:
        return "PM10"
    elif "ozone" in name_lower or "o3" in name_lower:
        return "Ozone"
    elif "nitrogen" in name_lower or "no2" in name_lower:
        return "Nitrogen Dioxide"
    elif "sulfur" in name_lower or "so2" in name_lower:
        return "Sulfur Dioxide"
    elif "carbon monoxide" in name_lower or "co" in name_lower:
        return "Carbon Monoxide"
    elif "black carbon" in name_lower:
        return "Black Carbon"
    else:
        return "Other"

def determine_health_risk_level(pollutant_type, value):
    """Determine health risk level based on pollutant type and value"""
    
    # EPA AQI breakpoints (simplified)
    if pollutant_type == "PM2.5":
        if value <= 12.0:
            return "GOOD"
        elif value <= 35.4:
            return "MODERATE"
        elif value <= 55.4:
            return "UNHEALTHY_SENSITIVE"
        elif value <= 150.4:
            return "UNHEALTHY"
        else:
            return "HAZARDOUS"
    elif pollutant_type == "Ozone":
        if value <= 0.054:
            return "GOOD"
        elif value <= 0.070:
            return "MODERATE"
        elif value <= 0.085:
            return "UNHEALTHY_SENSITIVE"
        elif value <= 0.105:
            return "UNHEALTHY"
        else:
            return "HAZARDOUS"
    else:
        # Generic thresholds for other pollutants
        if value <= 50:
            return "GOOD"
        elif value <= 100:
            return "MODERATE"
        elif value <= 150:
            return "UNHEALTHY_SENSITIVE"
        else:
            return "UNHEALTHY"

def map_geo_to_zip(geo_id, geo_type):
    """Map geographic ID to ZIP code"""
    
    # If it's already a ZIP code format, return it
    if geo_type and "zip" in geo_type.lower():
        return geo_id
    
    # For other geo types, we'd need a mapping table
    # For now, return the geo_id as is
    return geo_id

def map_geo_to_borough(geo_place_name, geo_type):
    """Map geographic place name to borough"""
    
    if not geo_place_name:
        return "Unknown"
    
    place_lower = geo_place_name.lower()
    
    if "manhattan" in place_lower or "new york" in place_lower:
        return "Manhattan"
    elif "brooklyn" in place_lower or "kings" in place_lower:
        return "Brooklyn"
    elif "queens" in place_lower:
        return "Queens"
    elif "bronx" in place_lower:
        return "Bronx"
    elif "staten island" in place_lower or "richmond" in place_lower:
        return "Staten Island"
    else:
        return geo_place_name

def create_air_quality_summary(df):
    """Create summary data for air quality by area"""
    
    if df.empty:
        return pd.DataFrame()
    
    print("Creating air quality summary by location...")
    
    summary_data = []
    
    # Group by location and calculate air quality metrics
    for location in df['location_name'].unique():
        location_data = df[df['location_name'] == location]
        
        if len(location_data) > 0:
            # Calculate air quality metrics
            avg_pm25 = location_data[location_data['pollutant_type'] == 'PM2.5']['pollutant_value'].mean()
            avg_ozone = location_data[location_data['pollutant_type'] == 'Ozone']['pollutant_value'].mean()
            
            # Count unhealthy days
            unhealthy_days = len(location_data[location_data['health_risk_level'].isin(['UNHEALTHY', 'HAZARDOUS'])])
            total_measurements = len(location_data)
            
            # Get most recent data
            latest_date = location_data['date'].max()
            borough = location_data['borough'].iloc[0]
            zip_code = location_data['zip_code'].iloc[0]
            
            # Calculate overall air quality score (0-100, lower is better)
            pm25_score = min(100, avg_pm25 * 2) if pd.notna(avg_pm25) else 50
            ozone_score = min(100, avg_ozone * 1000) if pd.notna(avg_ozone) else 50
            overall_score = (pm25_score + ozone_score) / 2
            
            summary_data.append({
                "location_name": location,
                "zip_code": zip_code,
                "borough": borough,
                "avg_pm25": round(avg_pm25, 2) if pd.notna(avg_pm25) else None,
                "avg_ozone": round(avg_ozone, 4) if pd.notna(avg_ozone) else None,
                "total_measurements": total_measurements,
                "unhealthy_days": unhealthy_days,
                "unhealthy_percentage": round((unhealthy_days / total_measurements) * 100, 2),
                "air_quality_score": round(overall_score, 2),
                "risk_level": "HIGH" if overall_score > 75 else "MEDIUM" if overall_score > 50 else "LOW",
                "latest_measurement": latest_date,
                "data_source": "NYC Air Quality Analysis",
                "created_at": datetime.now().isoformat()
            })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        print(f"Created air quality summary for {len(summary_df)} locations")
        return summary_df
    else:
        return pd.DataFrame()

def save_air_quality_data(air_quality_df, summary_df):
    """Save air quality data to database"""
    
    try:
        conn = sqlite3.connect('public_health_data.db')
        
        # Save air quality data
        if not air_quality_df.empty:
            air_quality_df.to_sql('enhanced_air_quality_data', conn, if_exists='replace', index=False)
            print(f"✅ Successfully saved {len(air_quality_df)} air quality records")
        
        # Save summary data
        if not summary_df.empty:
            summary_df.to_sql('air_quality_summary', conn, if_exists='replace', index=False)
            print(f"✅ Successfully saved {len(summary_df)} air quality summaries")
        
        # Show summary
        if not air_quality_df.empty:
            print("\n📊 Air Quality Data Summary:")
            print(f"   Total records: {len(air_quality_df)}")
            print(f"   Date range: {air_quality_df['date'].min()} to {air_quality_df['date'].max()}")
            print(f"   Locations: {air_quality_df['location_name'].nunique()}")
            print(f"   Pollutant types: {air_quality_df['pollutant_type'].nunique()}")
            print(f"   Unhealthy measurements: {len(air_quality_df[air_quality_df['health_risk_level'].isin(['UNHEALTHY', 'HAZARDOUS'])])}")
        
        if not summary_df.empty:
            print("\n📋 High-risk locations for air quality:")
            high_risk_areas = summary_df[summary_df['risk_level'] == 'HIGH'].head(10)
            if not high_risk_areas.empty:
                print(high_risk_areas[['location_name', 'borough', 'air_quality_score', 'unhealthy_percentage']].to_string(index=False))
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error saving air quality data: {e}")
        return False

def main():
    """Main function to ingest enhanced air quality data"""
    
    print("=" * 60)
    print("🌬️ NYC ENHANCED AIR QUALITY DATA INGESTION")
    print("=" * 60)
    
    # Fetch surveillance data
    surveillance_df = fetch_nyc_air_quality_data()
    
    # Fetch NYCCAS pollution data
    pollution_df = fetch_nyccas_pollution_data()
    
    if not surveillance_df.empty or not pollution_df.empty:
        # Process data
        processed_df = process_air_quality_data(surveillance_df, pollution_df)
        
        if not processed_df.empty:
            # Create summary
            summary_df = create_air_quality_summary(processed_df)
            
            # Save to database
            success = save_air_quality_data(processed_df, summary_df)
            
            if success:
                print("\n✅ Enhanced air quality data ingestion completed successfully!")
                return len(processed_df)
            else:
                print("\n❌ Failed to save air quality data")
                return 0
        else:
            print("\n❌ No valid air quality data processed")
            return 0
    else:
        print("\n❌ No air quality data retrieved")
        return 0

if __name__ == "__main__":
    records_ingested = main()
    print(f"\n🎯 Final result: {records_ingested} air quality records ingested")
