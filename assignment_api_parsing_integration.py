#!/usr/bin/env python3
"""
Class Assignment: Parse Live API Response and Integrate Data into MVP Functionality
Based on NYC Public Health MVP existing patterns for data extraction and storage

This script demonstrates parsing API responses and integrating data using the same
patterns as the existing MVP codebase.
"""

import requests
import json
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional

# Sample raw JSON responses (simulating live API responses)
SAMPLE_NYC_FLU_RESPONSE = [
    {
        "extract_date": "2025-06-20T00:00:00.000",
        "mod_zcta": "10001",
        "ili_pne_visits": "45",
        "total_ed_visits": "892",
        "ili_pne_admissions": "12"
    },
    {
        "extract_date": "2025-06-20T00:00:00.000", 
        "mod_zcta": "10451",
        "ili_pne_visits": "67",
        "total_ed_visits": "1205",
        "ili_pne_admissions": "18"
    }
]

SAMPLE_RESTAURANT_RESPONSE = [
    {
        "inspection_date": "2025-06-18T00:00:00.000",
        "dba": "Joe's Pizza",
        "boro": "MANHATTAN",
        "zipcode": "10001",
        "action": "Violations were cited in the following area(s).",
        "violation_code": "04L",
        "violation_description": "Evidence of mice or live mice present in facility's food and/or non-food areas.",
        "critical_flag": "Critical",
        "grade": "B",
        "score": "18"
    }
]

SAMPLE_OPENROUTER_AI_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": "Key indicators of disease outbreak in emergency department data include: 1) Sudden spike in visits (>30% above baseline), 2) Clustering by geographic area, 3) Similar symptom patterns, 4) Unusual demographic distribution, 5) Temporal clustering within short periods."
            }
        }
    ],
    "usage": {
        "prompt_tokens": 45,
        "completion_tokens": 52,
        "total_tokens": 97
    }
}

def parse_flu_surveillance_response(raw_json_response: List[Dict]) -> List[Dict]:
    """
    Parse NYC Flu Surveillance API response and extract specific data fields
    Following the pattern from ingest_flu_surveillance_data.py
    """
    print("🦠 PARSING FLU SURVEILLANCE API RESPONSE")
    print("=" * 50)
    
    print("Raw JSON Response:")
    print(json.dumps(raw_json_response, indent=2))
    
    processed_data = []
    
    for record in raw_json_response:
        try:
            # Extract specific data fields (following existing MVP pattern)
            extract_date = record.get('extract_date', '')
            mod_zcta = record.get('mod_zcta', '')
            ili_pne_visits = record.get('ili_pne_visits', '0')
            total_ed_visits = record.get('total_ed_visits', '0')
            ili_pne_admissions = record.get('ili_pne_admissions', '0')
            
            # Clean and validate data (following existing pattern)
            if extract_date and mod_zcta:
                # Convert to proper date format
                date_clean = pd.to_datetime(extract_date).strftime('%Y-%m-%d')
                
                # Convert numeric fields
                total_visits = int(total_ed_visits) if total_ed_visits else 0
                flu_visits = int(ili_pne_visits) if ili_pne_visits else 0
                flu_admissions = int(ili_pne_admissions) if ili_pne_admissions else 0
                
                # Calculate flu percentage
                flu_percentage = round((flu_visits / total_visits) * 100, 2) if total_visits > 0 else 0
                
                # Map ZIP code to borough (simplified mapping from existing code)
                borough_mapping = {
                    '10001': 'MANHATTAN', '10451': 'BRONX', '11101': 'QUEENS',
                    '11201': 'BROOKLYN', '10301': 'STATEN ISLAND'
                }
                borough = borough_mapping.get(mod_zcta, 'UNKNOWN')
                
                # Create processed record (following existing MVP structure)
                processed_record = {
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
                }
                
                processed_data.append(processed_record)
                
        except Exception as e:
            print(f"Error processing flu record: {e}")
            continue
    
    print(f"\n✅ Extracted and processed {len(processed_data)} flu surveillance records")
    print("Processed data structure:")
    if processed_data:
        print(json.dumps(processed_data[0], indent=2))
    
    return processed_data

def parse_restaurant_inspection_response(raw_json_response: List[Dict]) -> List[Dict]:
    """
    Parse NYC Restaurant Inspection API response and extract specific data fields
    Following the pattern from ingest_foodborne_illness_data.py
    """
    print("\n🍽️ PARSING RESTAURANT INSPECTION API RESPONSE")
    print("=" * 50)
    
    print("Raw JSON Response:")
    print(json.dumps(raw_json_response, indent=2))
    
    processed_data = []
    
    for record in raw_json_response:
        try:
            # Extract specific data fields (following existing MVP pattern)
            inspection_date = record.get('inspection_date', '')
            dba = record.get('dba', '')
            boro = record.get('boro', '')
            zipcode = record.get('zipcode', '')
            action = record.get('action', '')
            violation_code = record.get('violation_code', '')
            violation_description = record.get('violation_description', '')
            critical_flag = record.get('critical_flag', '')
            grade = record.get('grade', '')
            score = record.get('score', '0')
            
            # Clean and validate data (following existing pattern)
            if inspection_date and dba and boro:
                # Convert to proper date format
                date_clean = pd.to_datetime(inspection_date).strftime('%Y-%m-%d')
                
                # Convert numeric score
                try:
                    numeric_score = int(score) if score else 0
                except:
                    numeric_score = 0
                
                # Determine risk level (following existing logic)
                is_high_risk = 'mice' in violation_description.lower() or 'roach' in violation_description.lower()
                risk_level = "HIGH" if numeric_score > 20 or is_high_risk else "MEDIUM" if numeric_score > 10 else "LOW"
                
                # Create processed record (following existing MVP structure)
                processed_record = {
                    "date": date_clean,
                    "restaurant_id": f"REST_{zipcode}_{hash(dba) % 10000}",  # Generate ID
                    "restaurant_name": dba[:100] if dba else "Unknown",
                    "borough": boro,
                    "zip_code": zipcode,
                    "inspection_action": action,
                    "violation_code": violation_code,
                    "violation_description": violation_description[:200] if violation_description else "",
                    "is_critical": critical_flag == 'Critical',
                    "is_high_risk_foodborne": is_high_risk,
                    "inspection_score": numeric_score,
                    "grade": grade,
                    "foodborne_risk_level": risk_level,
                    "data_source": "NYC Open Data - Restaurant Inspections",
                    "illness_type": "Foodborne Illness Risk",
                    "created_at": datetime.now().isoformat()
                }
                
                processed_data.append(processed_record)
                
        except Exception as e:
            print(f"Error processing restaurant record: {e}")
            continue
    
    print(f"\n✅ Extracted and processed {len(processed_data)} restaurant inspection records")
    print("Processed data structure:")
    if processed_data:
        print(json.dumps(processed_data[0], indent=2))
    
    return processed_data

def parse_ai_explanation_response(raw_json_response: Dict) -> str:
    """
    Parse OpenRouter AI API response and extract explanation text
    Following the pattern from phase2_pattern_detection.py
    """
    print("\n🤖 PARSING AI EXPLANATION API RESPONSE")
    print("=" * 50)
    
    print("Raw JSON Response:")
    print(json.dumps(raw_json_response, indent=2))
    
    try:
        # Extract AI explanation text (following existing MVP pattern)
        if 'choices' in raw_json_response and len(raw_json_response['choices']) > 0:
            explanation = raw_json_response['choices'][0]['message']['content']
            
            # Clean and validate explanation
            explanation = explanation.strip()
            if len(explanation) > 500:
                explanation = explanation[:500] + "..."
            
            print(f"\n✅ Extracted AI explanation: {len(explanation)} characters")
            print(f"Explanation: {explanation}")
            
            return explanation
        else:
            print("❌ No explanation found in AI response")
            return "No explanation available"
            
    except Exception as e:
        print(f"❌ Error parsing AI response: {e}")
        return "Error parsing explanation"

def store_flu_data_in_database(processed_data: List[Dict]) -> bool:
    """
    Store processed flu data in database following existing MVP patterns
    Based on the pattern from ingest_flu_surveillance_data.py
    """
    print("\n💾 STORING FLU DATA IN DATABASE")
    print("=" * 50)
    
    try:
        # Connect to database (following existing pattern)
        conn = sqlite3.connect('public_health_data.db')
        
        # Convert to DataFrame for easy database insertion
        df = pd.DataFrame(processed_data)
        
        # Store in database (following existing pattern)
        df.to_sql('flu_surveillance_data', conn, if_exists='append', index=False)
        
        print(f"✅ Successfully stored {len(processed_data)} flu surveillance records")
        
        # Show summary (following existing pattern)
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"   ZIP codes: {df['zip_code'].nunique()}")
        print(f"   Boroughs: {df['borough'].nunique()}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing flu data: {e}")
        return False

def store_restaurant_data_in_database(processed_data: List[Dict]) -> bool:
    """
    Store processed restaurant data in database following existing MVP patterns
    Based on the pattern from ingest_foodborne_illness_data.py
    """
    print("\n💾 STORING RESTAURANT DATA IN DATABASE")
    print("=" * 50)
    
    try:
        # Connect to database (following existing pattern)
        conn = sqlite3.connect('public_health_data.db')
        
        # Convert to DataFrame for easy database insertion
        df = pd.DataFrame(processed_data)
        
        # Store in database (following existing pattern)
        df.to_sql('restaurant_inspection_data', conn, if_exists='append', index=False)
        
        print(f"✅ Successfully stored {len(processed_data)} restaurant inspection records")
        
        # Show summary (following existing pattern)
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"   Restaurants: {df['restaurant_name'].nunique()}")
        print(f"   High risk: {df['is_high_risk_foodborne'].sum()}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error storing restaurant data: {e}")
        return False

def main():
    """
    Main function demonstrating API response parsing and data integration
    Following existing MVP patterns for data processing and storage
    """
    print("🚀 CLASS ASSIGNMENT: API RESPONSE PARSING & DATA INTEGRATION")
    print("Based on NYC Public Health MVP existing patterns")
    print("=" * 70)
    
    # 1. Parse Flu Surveillance API Response
    print("\n1️⃣ PARSING FLU SURVEILLANCE DATA")
    flu_data = parse_flu_surveillance_response(SAMPLE_NYC_FLU_RESPONSE)
    
    if flu_data:
        # Store flu data in database
        flu_stored = store_flu_data_in_database(flu_data)
    
    # 2. Parse Restaurant Inspection API Response  
    print("\n2️⃣ PARSING RESTAURANT INSPECTION DATA")
    restaurant_data = parse_restaurant_inspection_response(SAMPLE_RESTAURANT_RESPONSE)
    
    if restaurant_data:
        # Store restaurant data in database
        restaurant_stored = store_restaurant_data_in_database(restaurant_data)
    
    # 3. Parse AI Explanation API Response
    print("\n3️⃣ PARSING AI EXPLANATION DATA")
    ai_explanation = parse_ai_explanation_response(SAMPLE_OPENROUTER_AI_RESPONSE)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DATA INTEGRATION SUMMARY")
    print("=" * 70)
    
    print(f"✅ Flu surveillance records processed: {len(flu_data) if flu_data else 0}")
    print(f"✅ Restaurant inspection records processed: {len(restaurant_data) if restaurant_data else 0}")
    print(f"✅ AI explanation extracted: {'Yes' if ai_explanation else 'No'}")
    
    print("\n🎯 Assignment completed successfully!")
    print("💡 Data extracted from raw JSON responses and integrated into MVP database structure")

if __name__ == "__main__":
    main()
