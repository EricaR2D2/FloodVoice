#!/usr/bin/env python3
"""
Debug the current TypeError and 500 error
"""

import requests
import json

def debug_current_error():
    """Debug the current dashboard errors."""
    
    base_url = "http://localhost:5000"
    
    print("🐛 DEBUGGING CURRENT DASHBOARD ERRORS")
    print("=" * 50)
    
    # Test the API summary endpoint that's failing
    print("\n🔍 Testing API Summary endpoint directly")
    
    try:
        # Create a session for login
        session = requests.Session()
        
        # Login first
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"   🔐 Login: HTTP {login_response.status_code}")
        
        if login_response.status_code == 302:
            # Test the summary API
            summary_response = session.get(f"{base_url}/api/summary")
            print(f"   📊 Summary API: HTTP {summary_response.status_code}")
            
            if summary_response.status_code == 500:
                print("   ❌ 500 Error Details:")
                try:
                    error_data = summary_response.json()
                    print(f"   📝 Error: {error_data}")
                except:
                    print(f"   📝 Raw response: {summary_response.text[:500]}...")
            elif summary_response.status_code == 200:
                print("   ✅ Success!")
                try:
                    data = summary_response.json()
                    print(f"   📋 Keys: {list(data.keys())}")
                except:
                    print("   ⚠️ Could not parse JSON response")
        else:
            print("   ❌ Login failed")
    
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test the main dashboard page
    print(f"\n🔍 Testing main dashboard page")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   📄 Main page: HTTP {response.status_code}")
        
        if response.status_code == 200:
            # Check if there are any JavaScript errors in the HTML
            html = response.text
            if 'error' in html.lower() or 'undefined' in html.lower():
                print("   ⚠️ Potential issues found in HTML")
            else:
                print("   ✅ HTML looks clean")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n🔍 Testing individual data freshness functions")
    
    # Test the data freshness function directly
    try:
        import sys
        sys.path.append('.')
        from app import DashboardManager
        
        manager = DashboardManager()
        
        # Test each data source individually
        data_sources = [
            ('hospital_data', 'real_hospital_data', 'date'),
            ('nyc_covid_data', 'nyc_covid_data', 'date_of_interest'),
            ('covid_daily_counts', 'covid_daily_counts', 'date_of_interest'),
            ('air_quality_data', 'enhanced_air_quality_data', 'date'),
            ('restaurant_data', 'restaurant_inspection_data', 'date'),
            ('cdc_ili_data', 'cdc_ili_data', 'week_ending_date')
        ]
        
        for name, table, column in data_sources:
            print(f"\n   Testing {name} ({table}.{column})")
            try:
                freshness = manager.get_data_freshness(table, column)
                print(f"   ✅ Success: {freshness}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
    except Exception as e:
        print(f"   ❌ Could not test data freshness: {e}")

if __name__ == "__main__":
    debug_current_error()
