#!/usr/bin/env python3
"""
Ingest NYC Foodborne Illness Data from NYC Open Data
DOHMH New York City Restaurant Inspection Results
"""

import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import requests
import json

def fetch_restaurant_inspection_data():
    """Fetch restaurant inspection data from NYC Open Data"""
    
    print("🍽️ Fetching NYC Restaurant Inspection Data...")
    
    # NYC Open Data API endpoint for Restaurant Inspections
    api_url = "https://data.cityofnewyork.us/resource/43nn-pn8j.json"
    
    try:
        print("Fetching restaurant inspection data from NYC Open Data...")
        
        # Fetch recent restaurant inspection data
        params = {
            "$limit": 100000,  # Get substantial amount of data
            "$order": "inspection_date DESC",  # Most recent first
            "$where": "inspection_date >= '2022-01-01T00:00:00.000'"  # Recent data only
        }
        
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"Retrieved {len(data)} restaurant inspection records from NYC Open Data")
        
        if not data:
            print("No restaurant inspection data returned from API")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Print available columns to understand the data structure
        print("Available restaurant inspection columns:", df.columns.tolist())
        if len(df) > 0:
            print("Sample restaurant inspection record:", df.iloc[0].to_dict())
        
        return df
        
    except Exception as e:
        print(f"Error fetching restaurant inspection data: {e}")
        return pd.DataFrame()

def process_restaurant_inspection_data(df):
    """Process and clean restaurant inspection data for foodborne illness analysis"""
    
    if df.empty:
        print("No restaurant inspection data to process")
        return pd.DataFrame()
    
    print(f"Processing {len(df)} restaurant inspection records...")
    
    processed_data = []
    
    # Focus on violations that could indicate foodborne illness risk
    high_risk_violations = [
        'food temperature', 'cross contamination', 'hand washing', 'food source',
        'food protection', 'food contact surface', 'personal hygiene', 'vermin',
        'sewage', 'toxic', 'food handling', 'refrigeration', 'hot holding'
    ]
    
    for _, row in df.iterrows():
        try:
            # Extract key fields
            camis = row.get('camis', '')
            dba = row.get('dba', '')
            boro = row.get('boro', '')
            zipcode = row.get('zipcode', '')
            inspection_date = row.get('inspection_date', '')
            action = row.get('action', '')
            violation_code = row.get('violation_code', '')
            violation_description = row.get('violation_description', '')
            critical_flag = row.get('critical_flag', '')
            score = row.get('score', '')
            grade = row.get('grade', '')
            
            # Clean and validate data
            if inspection_date and zipcode and dba:
                # Convert to proper date format
                date_clean = pd.to_datetime(inspection_date).strftime('%Y-%m-%d') if inspection_date else None
                
                # Determine if violation is high-risk for foodborne illness
                is_high_risk = False
                if violation_description and isinstance(violation_description, str):
                    violation_lower = violation_description.lower()
                    is_high_risk = any(risk_term in violation_lower for risk_term in high_risk_violations)
                
                # Convert score to numeric
                numeric_score = 0
                try:
                    numeric_score = int(score) if score else 0
                except:
                    numeric_score = 0
                
                # Determine risk level based on score and violations
                risk_level = determine_foodborne_risk_level(numeric_score, critical_flag, is_high_risk)
                
                processed_data.append({
                    "date": date_clean,
                    "restaurant_id": camis,
                    "restaurant_name": dba[:100] if dba else "Unknown",  # Limit length
                    "borough": boro,
                    "zip_code": zipcode,
                    "inspection_action": action,
                    "violation_code": violation_code,
                    "violation_description": violation_description[:200] if violation_description else "",  # Limit length
                    "is_critical": critical_flag == 'Critical',
                    "is_high_risk_foodborne": is_high_risk,
                    "inspection_score": numeric_score,
                    "grade": grade,
                    "foodborne_risk_level": risk_level,
                    "data_source": "NYC Open Data - Restaurant Inspections",
                    "illness_type": "Foodborne Illness Risk",
                    "created_at": datetime.now().isoformat()
                })
        
        except Exception as e:
            print(f"Error processing restaurant inspection record: {e}")
            continue
    
    if processed_data:
        processed_df = pd.DataFrame(processed_data)
        print(f"Successfully processed {len(processed_df)} restaurant inspection records")
        return processed_df
    else:
        print("No valid restaurant inspection records processed")
        return pd.DataFrame()

def determine_foodborne_risk_level(score, critical_flag, is_high_risk):
    """Determine foodborne illness risk level based on inspection data"""
    
    # High risk: High score + critical violations + high-risk violation types
    if score > 28 or (critical_flag == 'Critical' and is_high_risk):
        return 'HIGH'
    elif score > 14 or critical_flag == 'Critical':
        return 'MEDIUM'
    elif is_high_risk:
        return 'MEDIUM'
    else:
        return 'LOW'

def create_foodborne_illness_summary(df):
    """Create summary data for foodborne illness risk by area"""
    
    if df.empty:
        return pd.DataFrame()
    
    print("Creating foodborne illness risk summary by ZIP code...")
    
    # Group by ZIP code and calculate risk metrics
    summary_data = []
    
    for zip_code in df['zip_code'].unique():
        zip_data = df[df['zip_code'] == zip_code]
        
        if len(zip_data) > 0:
            # Calculate risk metrics
            total_inspections = len(zip_data)
            high_risk_inspections = len(zip_data[zip_data['foodborne_risk_level'] == 'HIGH'])
            critical_violations = len(zip_data[zip_data['is_critical'] == True])
            avg_score = zip_data['inspection_score'].mean()
            
            # Get most recent data
            latest_date = zip_data['date'].max()
            borough = zip_data['borough'].iloc[0]
            
            # Calculate overall risk score (0-100)
            risk_score = min(100, (high_risk_inspections / total_inspections * 50) + 
                           (critical_violations / total_inspections * 30) + 
                           (min(avg_score, 40) / 40 * 20))
            
            summary_data.append({
                "zip_code": zip_code,
                "borough": borough,
                "total_inspections": total_inspections,
                "high_risk_inspections": high_risk_inspections,
                "critical_violations": critical_violations,
                "avg_inspection_score": round(avg_score, 2),
                "foodborne_risk_score": round(risk_score, 2),
                "risk_level": 'HIGH' if risk_score > 70 else 'MEDIUM' if risk_score > 40 else 'LOW',
                "latest_inspection": latest_date,
                "data_source": "NYC Restaurant Inspections Analysis",
                "created_at": datetime.now().isoformat()
            })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        print(f"Created foodborne illness risk summary for {len(summary_df)} ZIP codes")
        return summary_df
    else:
        return pd.DataFrame()

def save_foodborne_illness_data(inspection_df, summary_df):
    """Save foodborne illness data to database"""
    
    try:
        conn = sqlite3.connect('public_health_data.db')
        
        # Save inspection data
        if not inspection_df.empty:
            inspection_df.to_sql('restaurant_inspection_data', conn, if_exists='replace', index=False)
            print(f"✅ Successfully saved {len(inspection_df)} restaurant inspection records")
        
        # Save summary data
        if not summary_df.empty:
            summary_df.to_sql('foodborne_illness_risk_summary', conn, if_exists='replace', index=False)
            print(f"✅ Successfully saved {len(summary_df)} foodborne risk summaries")
        
        # Show summary
        if not inspection_df.empty:
            print("\n📊 Restaurant Inspection Data Summary:")
            print(f"   Total records: {len(inspection_df)}")
            print(f"   Date range: {inspection_df['date'].min()} to {inspection_df['date'].max()}")
            print(f"   ZIP codes: {inspection_df['zip_code'].nunique()}")
            print(f"   Restaurants: {inspection_df['restaurant_id'].nunique()}")
            print(f"   High-risk inspections: {len(inspection_df[inspection_df['foodborne_risk_level'] == 'HIGH'])}")
        
        if not summary_df.empty:
            print("\n📋 High-risk ZIP codes for foodborne illness:")
            high_risk_areas = summary_df[summary_df['risk_level'] == 'HIGH'].head(10)
            if not high_risk_areas.empty:
                print(high_risk_areas[['zip_code', 'borough', 'foodborne_risk_score', 'high_risk_inspections']].to_string(index=False))
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error saving foodborne illness data: {e}")
        return False

def main():
    """Main function to ingest foodborne illness data"""
    
    print("=" * 60)
    print("🍽️ NYC FOODBORNE ILLNESS DATA INGESTION")
    print("=" * 60)
    
    # Fetch data
    inspection_df = fetch_restaurant_inspection_data()
    
    if not inspection_df.empty:
        # Process data
        processed_df = process_restaurant_inspection_data(inspection_df)
        
        if not processed_df.empty:
            # Create summary
            summary_df = create_foodborne_illness_summary(processed_df)
            
            # Save to database
            success = save_foodborne_illness_data(processed_df, summary_df)
            
            if success:
                print("\n✅ Foodborne illness data ingestion completed successfully!")
                return len(processed_df)
            else:
                print("\n❌ Failed to save foodborne illness data")
                return 0
        else:
            print("\n❌ No valid foodborne illness data processed")
            return 0
    else:
        print("\n❌ No restaurant inspection data retrieved")
        return 0

if __name__ == "__main__":
    records_ingested = main()
    print(f"\n🎯 Final result: {records_ingested} foodborne illness records ingested")
