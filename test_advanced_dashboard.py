#!/usr/bin/env python3
"""
Test script for Advanced Dashboard functionality
"""

import requests
import json

def test_advanced_dashboard():
    """Test the complete advanced dashboard flow"""
    
    print("🧪 Testing Advanced Dashboard Authentication & Functionality")
    print("=" * 60)
    
    # Create session for maintaining cookies
    session = requests.Session()
    
    # Test 1: Check if advanced dashboard requires authentication
    print("\n1. Testing Authentication Requirement...")
    try:
        response = session.get('http://localhost:5000/advanced-dashboard', allow_redirects=False)
        if response.status_code == 302:
            print("   ✅ Authentication required - redirects to login")
        else:
            print(f"   ❌ No authentication required (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Error testing authentication: {e}")
        return False
    
    # Test 2: Login with test user
    print("\n2. Testing Login...")
    try:
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        login_response = session.post('http://localhost:5000/login', data=login_data, allow_redirects=True)
        
        if login_response.status_code == 200 and ('dashboard' in login_response.url or login_response.url.endswith('/')):
            print("   ✅ Login successful")
        else:
            print(f"   ❌ Login failed (Status: {login_response.status_code}, URL: {login_response.url})")
            return False
    except Exception as e:
        print(f"   ❌ Error during login: {e}")
        return False
    
    # Test 3: Access advanced dashboard
    print("\n3. Testing Advanced Dashboard Access...")
    try:
        dashboard_response = session.get('http://localhost:5000/advanced-dashboard')
        if dashboard_response.status_code == 200:
            print(f"   ✅ Advanced dashboard accessible (Content: {len(dashboard_response.text)} chars)")
        else:
            print(f"   ❌ Advanced dashboard failed (Status: {dashboard_response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Error accessing advanced dashboard: {e}")
        return False
    
    # Test 4: Test API endpoints
    print("\n4. Testing API Endpoints...")
    
    # Test map data API
    try:
        api_data = {
            'illnessTypes': ['COVID-19'],
            'dateRange': '30',
            'borough': '',
            'zipCode': '',
            'riskLevels': ['LOW', 'MEDIUM', 'HIGH', 'HAZARDOUS']
        }
        
        api_response = session.post('http://localhost:5000/api/map-data', json=api_data)
        if api_response.status_code == 200:
            data = api_response.json()
            if data.get('success'):
                print(f"   ✅ Map Data API working (Alerts: {len(data.get('alerts', []))})")
            else:
                print(f"   ⚠️ Map Data API returned success=False: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ Map Data API failed (Status: {api_response.status_code})")
            print(f"      Response: {api_response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error testing Map Data API: {e}")
    
    # Test choropleth endpoint
    try:
        choropleth_response = session.get('http://localhost:5000/choropleth-map/COVID-19?date_range=30&borough=&zip_code=')
        if choropleth_response.status_code == 200:
            print(f"   ✅ Choropleth API working (Content: {len(choropleth_response.text)} chars)")
        else:
            print(f"   ❌ Choropleth API failed (Status: {choropleth_response.status_code})")
    except Exception as e:
        print(f"   ❌ Error testing Choropleth API: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Advanced Dashboard Test Complete!")
    return True

if __name__ == "__main__":
    test_advanced_dashboard()
