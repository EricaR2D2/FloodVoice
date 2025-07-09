#!/usr/bin/env python3
"""
Class Assignment: Live API Calls Script
Based on NYC Public Health MVP code structure and API patterns

This script demonstrates live API calls using the same patterns and 
authentication methods as the existing codebase.
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Load environment variables (following existing pattern from phase2_pattern_detection.py)
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')

def make_openrouter_api_call():
    """
    Make a live API call to OpenRouter (AI service used in pattern detection)
    Following the exact pattern from phase2_pattern_detection.py
    """
    print("🤖 OPENROUTER AI API CALL")
    print("=" * 50)
    
    # Endpoint and parameters (from existing codebase)
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
    
    # API key handling method: Environment variable (secure pattern from codebase)
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        print("💡 Set it using: export OPENROUTER_API_KEY='your_key_here'")
        return None
    
    # Parameters (following existing AI explanation pattern)
    params = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system", 
                "content": "You are a public health data analyst. Provide brief, factual responses."
            },
            {
                "role": "user", 
                "content": "What are the key indicators of a disease outbreak in emergency department data?"
            }
        ],
        "max_tokens": 150,
        "temperature": 0.3
    }
    
    # Headers (following existing pattern)
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/EricaR2D2/PublicHealthMVP",
        "X-Title": "NYC Public Health MVP"
    }
    
    try:
        print(f"📡 Making API call to: {endpoint}")
        print(f"🔑 API key handling: Environment variable (secure)")
        print(f"📋 Parameters: {json.dumps(params, indent=2)}")
        
        response = requests.post(endpoint, json=params, headers=headers, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS - Raw JSON Response:")
            print("=" * 50)
            raw_json = response.json()
            print(json.dumps(raw_json, indent=2))
            return raw_json
        else:
            print(f"\n❌ API call failed with status {response.status_code}")
            print(f"Error response: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ Exception during API call: {e}")
        return None

def make_nyc_open_data_api_call():
    """
    Make a live API call to NYC Open Data (used throughout the codebase)
    Following patterns from ingest_flu_surveillance_data.py and other data ingestion scripts
    """
    print("\n🏙️ NYC OPEN DATA API CALL")
    print("=" * 50)
    
    # Endpoint and parameters (from existing flu surveillance code)
    endpoint = "https://data.cityofnewyork.us/resource/2nwg-uqyg.json"
    
    # API key handling method: No key required (public API)
    print("🔑 API key handling: No authentication required (public API)")
    
    # Parameters (following existing data ingestion patterns)
    params = {
        "$limit": 10,
        "$order": "extract_date DESC",
        "$select": "extract_date,mod_zcta,ili_pne_visits,total_ed_visits"
    }
    
    try:
        print(f"📡 Making API call to: {endpoint}")
        print(f"📋 Parameters: {json.dumps(params, indent=2)}")
        
        response = requests.get(endpoint, params=params, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS - Raw JSON Response:")
            print("=" * 50)
            raw_json = response.json()
            print(json.dumps(raw_json, indent=2))
            return raw_json
        else:
            print(f"\n❌ API call failed with status {response.status_code}")
            print(f"Error response: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ Exception during API call: {e}")
        return None

def make_restaurant_inspection_api_call():
    """
    Make a live API call to NYC Restaurant Inspection Data
    Following patterns from ingest_foodborne_illness_data.py
    """
    print("\n🍽️ NYC RESTAURANT INSPECTION API CALL")
    print("=" * 50)
    
    # Endpoint and parameters (from existing restaurant data code)
    endpoint = "https://data.cityofnewyork.us/resource/43nn-pn8j.json"
    
    # API key handling method: No key required (public API)
    print("🔑 API key handling: No authentication required (public API)")
    
    # Parameters (following existing restaurant inspection patterns)
    params = {
        "$limit": 5,
        "$order": "inspection_date DESC",
        "$select": "inspection_date,dba,boro,zipcode,action,violation_code,grade",
        "$where": "inspection_date >= '2025-06-01'"
    }
    
    try:
        print(f"📡 Making API call to: {endpoint}")
        print(f"📋 Parameters: {json.dumps(params, indent=2)}")
        
        response = requests.get(endpoint, params=params, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\n✅ SUCCESS - Raw JSON Response:")
            print("=" * 50)
            raw_json = response.json()
            print(json.dumps(raw_json, indent=2))
            return raw_json
        else:
            print(f"\n❌ API call failed with status {response.status_code}")
            print(f"Error response: {response.text}")
            return None
            
    except Exception as e:
        print(f"\n❌ Exception during API call: {e}")
        return None

def main():
    """
    Main function demonstrating multiple API calling patterns from the codebase
    """
    print("🚀 CLASS ASSIGNMENT: LIVE API CALLS DEMONSTRATION")
    print("Based on NYC Public Health MVP codebase patterns")
    print("=" * 70)
    
    # Track results
    results = {}
    
    # 1. OpenRouter AI API (requires API key)
    print("\n1️⃣ TESTING AI API WITH AUTHENTICATION")
    ai_result = make_openrouter_api_call()
    results['openrouter_ai'] = ai_result is not None
    
    # 2. NYC Open Data - Flu Surveillance (public API)
    print("\n2️⃣ TESTING NYC OPEN DATA - FLU SURVEILLANCE")
    flu_result = make_nyc_open_data_api_call()
    results['nyc_flu_data'] = flu_result is not None
    
    # 3. NYC Open Data - Restaurant Inspections (public API)
    print("\n3️⃣ TESTING NYC OPEN DATA - RESTAURANT INSPECTIONS")
    restaurant_result = make_restaurant_inspection_api_call()
    results['nyc_restaurant_data'] = restaurant_result is not None
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 API CALL SUMMARY")
    print("=" * 70)
    
    for api_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{api_name}: {status}")
    
    successful_calls = sum(results.values())
    total_calls = len(results)
    
    print(f"\n🎯 Overall Success Rate: {successful_calls}/{total_calls} ({(successful_calls/total_calls)*100:.1f}%)")
    
    if successful_calls > 0:
        print("\n✅ Assignment completed successfully!")
        print("💡 Raw JSON responses printed above for each successful API call")
    else:
        print("\n⚠️ No API calls succeeded. Check your environment setup.")
        print("💡 For OpenRouter API: Set OPENROUTER_API_KEY environment variable")
        print("💡 For NYC APIs: Check internet connection")

if __name__ == "__main__":
    main()
