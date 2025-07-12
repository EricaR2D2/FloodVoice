#!/usr/bin/env python3
"""
Test the date parsing fix for dashboard summary
"""

import requests
import json

def test_date_parsing_fix():
    """Test that the date parsing error is fixed."""
    
    base_url = "http://localhost:5000"
    
    print("🧪 TESTING DATE PARSING FIX")
    print("=" * 40)
    
    # Test the dashboard summary endpoint that was failing
    print("\n🔍 Testing Dashboard Summary API (was failing with date parsing error)")
    
    try:
        # First, we need to login to access the API
        session = requests.Session()
        
        # Get login page to get any CSRF tokens if needed
        login_page = session.get(f"{base_url}/login")
        print(f"   📝 Login page: HTTP {login_page.status_code}")
        
        # Try to login (assuming default credentials exist)
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"   🔐 Login attempt: HTTP {login_response.status_code}")
        
        if login_response.status_code == 302:
            print("   ✅ Login successful (redirected)")
            
            # Now test the dashboard summary API
            summary_response = session.get(f"{base_url}/api/summary")
            print(f"   📊 Dashboard summary: HTTP {summary_response.status_code}")
            
            if summary_response.status_code == 200:
                print("   ✅ SUCCESS: Dashboard summary API working!")
                
                try:
                    data = summary_response.json()
                    print(f"   📋 Response keys: {list(data.keys())}")
                    
                    # Check for data freshness info
                    if 'data_freshness' in data:
                        print("   📅 Data freshness info found:")
                        for source, freshness in data['data_freshness'].items():
                            status = freshness.get('status', 'unknown')
                            latest = freshness.get('latest_date', 'unknown')
                            print(f"     {source}: {status} (latest: {latest})")
                    
                except Exception as e:
                    print(f"   ⚠️ Could not parse JSON: {e}")
                    
            elif summary_response.status_code == 500:
                print("   ❌ STILL FAILING: 500 Internal Server Error")
                print(f"   📝 Error details: {summary_response.text[:300]}...")
                
            else:
                print(f"   ⚠️ Unexpected response: HTTP {summary_response.status_code}")
                
        else:
            print("   ❌ Login failed - testing without authentication")
            
            # Test without authentication (should get redirect)
            summary_response = requests.get(f"{base_url}/api/summary", allow_redirects=False)
            print(f"   📊 Dashboard summary (no auth): HTTP {summary_response.status_code}")
            
            if summary_response.status_code == 302:
                print("   🔐 Expected redirect to login (authentication required)")
            elif summary_response.status_code == 500:
                print("   ❌ 500 error even without authentication - date parsing issue persists")
            
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    # Test other endpoints that might have date parsing issues
    print(f"\n🔍 Testing other endpoints for date parsing issues")
    
    endpoints_to_test = [
        "/api/hospital-data?days=30",
        "/api/patterns?limit=5"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n   Testing {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}", allow_redirects=False)
            print(f"   HTTP {response.status_code}")
            
            if response.status_code == 500:
                print("   ❌ 500 error detected")
            elif response.status_code == 302:
                print("   🔐 Redirect (auth required)")
            elif response.status_code == 200:
                print("   ✅ Working")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n📊 DATE PARSING FIX TEST COMPLETE")
    print("=" * 40)

if __name__ == "__main__":
    test_date_parsing_fix()
