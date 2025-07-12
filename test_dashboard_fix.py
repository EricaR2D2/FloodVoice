#!/usr/bin/env python3
"""
Test dashboard endpoints to verify 500 error is fixed
"""

import requests
import json

def test_dashboard_endpoints():
    """Test key dashboard endpoints."""
    
    base_url = "http://localhost:5000"
    
    print("🧪 TESTING DASHBOARD ENDPOINTS")
    print("=" * 40)
    
    # Test endpoints (note: most require authentication)
    endpoints = {
        "Main Dashboard": "/",
        "Login Page": "/login",
        "Map Data": "/api/map-data",  # This one doesn't require auth
    }

    # Endpoints that require authentication (will return 302 redirect to login)
    auth_endpoints = {
        "Dashboard Summary": "/api/summary",
        "Recent Patterns": "/api/patterns",
        "Hospital Data": "/api/hospital-data",
        "Settings": "/api/settings"
    }
    
    results = {}

    # Test public endpoints first
    for name, endpoint in endpoints.items():
        print(f"\n🔍 Testing {name}: {endpoint}")
        
        try:
            if endpoint == "/api/map-data":
                # POST endpoint requires JSON data
                response = requests.post(f"{base_url}{endpoint}",
                                       json={},
                                       timeout=10)
            else:
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ SUCCESS: HTTP {response.status_code}")
                
                # Try to parse JSON for API endpoints
                if endpoint.startswith('/api/'):
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            print(f"   📊 Response keys: {list(data.keys())}")
                        else:
                            print(f"   📊 Response type: {type(data)}")
                    except:
                        print(f"   📊 Response length: {len(response.text)} chars")
                else:
                    print(f"   📊 HTML response length: {len(response.text)} chars")
                
                results[name] = "SUCCESS"
                
            elif response.status_code == 500:
                print(f"   ❌ INTERNAL SERVER ERROR: HTTP {response.status_code}")
                print(f"   📝 Error details: {response.text[:200]}...")
                results[name] = "500 ERROR"

            elif response.status_code == 302:
                print(f"   🔐 REDIRECT (Authentication required): HTTP {response.status_code}")
                results[name] = "AUTH REQUIRED"

            else:
                print(f"   ⚠️ UNEXPECTED: HTTP {response.status_code}")
                results[name] = f"HTTP {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ CONNECTION ERROR: Server not running?")
            results[name] = "CONNECTION ERROR"
            
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT: Request took too long")
            results[name] = "TIMEOUT"
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results[name] = f"ERROR: {e}"

    # Test authenticated endpoints (expect 302 redirects)
    print(f"\n🔐 Testing authenticated endpoints (expect redirects):")
    for name, endpoint in auth_endpoints.items():
        print(f"\n🔍 Testing {name}: {endpoint}")

        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10, allow_redirects=False)

            if response.status_code == 302:
                print(f"   ✅ EXPECTED REDIRECT: HTTP {response.status_code}")
                results[name] = "AUTH REQUIRED (EXPECTED)"
            elif response.status_code == 500:
                print(f"   ❌ INTERNAL SERVER ERROR: HTTP {response.status_code}")
                results[name] = "500 ERROR"
            else:
                print(f"   ⚠️ UNEXPECTED: HTTP {response.status_code}")
                results[name] = f"HTTP {response.status_code}"

        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results[name] = f"ERROR: {e}"

    # Summary
    print(f"\n📊 TEST RESULTS SUMMARY")
    print("=" * 30)
    
    success_count = sum(1 for result in results.values() if result in ["SUCCESS", "AUTH REQUIRED (EXPECTED)"])
    error_500_count = sum(1 for result in results.values() if "500 ERROR" in result)
    total_count = len(results)

    for name, result in results.items():
        if result == "SUCCESS":
            status_icon = "✅"
        elif result == "AUTH REQUIRED (EXPECTED)" or result == "AUTH REQUIRED":
            status_icon = "🔐"
        elif "500 ERROR" in result:
            status_icon = "❌"
        else:
            status_icon = "⚠️"
        print(f"   {status_icon} {name}: {result}")

    print(f"\n🎯 Overall: {success_count}/{total_count} endpoints working correctly")
    print(f"🚨 500 Errors: {error_500_count}/{total_count} endpoints")

    if error_500_count == 0:
        print("🎉 SUCCESS! No 500 errors found - Dashboard issue is FIXED!")
    elif error_500_count < total_count:
        print("⚠️ PARTIAL FIX: Some 500 errors remain")
    else:
        print("❌ DASHBOARD STILL BROKEN: All endpoints have 500 errors")
    
    return results

if __name__ == "__main__":
    test_dashboard_endpoints()
