#!/usr/bin/env python3
"""
Research suggested NYC Open Data sources for compatibility with MVP
"""

import requests
import pandas as pd
import json

def test_api_endpoint(endpoint_url, dataset_name):
    """Test an API endpoint and return sample data structure."""
    print(f"\n=== {dataset_name} ===")
    print(f"URL: {endpoint_url}")
    
    try:
        # Get first 5 records to analyze structure
        response = requests.get(f"{endpoint_url}?$limit=5", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {len(data)} sample records")
            
            if data:
                print("Sample record structure:")
                sample = data[0]
                for key, value in sample.items():
                    print(f"  {key}: {value} ({type(value).__name__})")
                
                # Check for key fields we need
                key_fields = ['date', 'zip_code', 'zipcode', 'borough', 'boro']
                found_fields = []
                for field in key_fields:
                    if field.lower() in [k.lower() for k in sample.keys()]:
                        found_fields.append(field)
                
                print(f"Key fields found: {found_fields}")
                return True, data
            else:
                print("⚠️ No data returned")
                return False, None
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def main():
    """Research the suggested datasets."""
    
    # Suggested datasets with their likely API endpoints
    datasets = {
        "Restaurant Inspections": "https://data.cityofnewyork.us/resource/43nn-pn8j.json",
        "COVID-19 Daily Counts": "https://data.cityofnewyork.us/resource/rc75-m7u3.json", 
        "COVID-19 Testing Cohorts": "https://data.cityofnewyork.us/resource/cwmx-mvra.json"
    }
    
    print("🔍 RESEARCHING SUGGESTED NYC OPEN DATA SOURCES")
    print("=" * 60)
    
    compatible_datasets = []
    
    for name, url in datasets.items():
        success, data = test_api_endpoint(url, name)
        if success:
            compatible_datasets.append((name, url, data))
    
    print(f"\n📊 COMPATIBILITY SUMMARY")
    print("=" * 30)
    print(f"Compatible datasets: {len(compatible_datasets)}")
    
    for name, url, data in compatible_datasets:
        print(f"✅ {name}")
    
    return compatible_datasets

if __name__ == "__main__":
    main()
