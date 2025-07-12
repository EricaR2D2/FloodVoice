#!/usr/bin/env python3
"""
Test that the pattern chart fix is working
"""

import requests
import json

def test_pattern_chart_fix():
    """Test that the pattern chart now has data."""
    
    base_url = "http://localhost:5000"
    
    print("🧪 TESTING PATTERN CHART FIX")
    print("=" * 40)
    
    try:
        # Create a session for login
        session = requests.Session()
        
        # Login first
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"🔐 Login: HTTP {login_response.status_code}")
        
        if login_response.status_code == 302:
            # Test the summary API
            summary_response = session.get(f"{base_url}/api/summary")
            
            if summary_response.status_code == 200:
                data = summary_response.json()
                recent_patterns = data.get('recent_patterns', [])
                
                print(f"📊 Pattern Chart Data Test:")
                print(f"   ✅ API Response: HTTP 200")
                print(f"   📈 Recent patterns found: {len(recent_patterns)}")
                
                if len(recent_patterns) > 0:
                    print(f"   🎯 CHART SHOULD NOW DISPLAY DATA!")
                    print(f"   📋 Pattern types:")
                    
                    total_patterns = 0
                    for pattern in recent_patterns:
                        pattern_type = pattern['pattern_type'].replace('_', ' ').upper()
                        count = pattern['count']
                        total_patterns += count
                        print(f"     • {pattern_type}: {count} patterns")
                    
                    print(f"   📊 Total patterns for chart: {total_patterns}")
                    
                    # Simulate what the JavaScript chart will do
                    labels = [p['pattern_type'].replace('_', ' ').upper() for p in recent_patterns]
                    values = [p['count'] for p in recent_patterns]
                    
                    print(f"   🏷️ Chart labels: {labels}")
                    print(f"   📊 Chart values: {values}")
                    
                    print(f"\n✅ PATTERN CHART FIX SUCCESSFUL!")
                    print(f"   The 'Recent Pattern Types' chart should now show:")
                    for i, (label, value) in enumerate(zip(labels, values)):
                        percentage = (value / total_patterns) * 100
                        print(f"   • {label}: {value} patterns ({percentage:.1f}%)")
                    
                else:
                    print(f"   ❌ STILL NO DATA: recent_patterns is empty")
                    print(f"   🔍 Need to investigate further...")
                    
            else:
                print(f"   ❌ API Error: HTTP {summary_response.status_code}")
        else:
            print(f"   ❌ Login failed")
    
    except Exception as e:
        print(f"   ❌ Test error: {e}")
    
    print(f"\n🎯 DEMO READINESS CHECK:")
    print(f"   Dashboard URL: {base_url}")
    print(f"   Expected result: Pattern chart shows data instead of blank box")
    print(f"   Status: {'✅ READY' if len(recent_patterns) > 0 else '❌ NOT READY'}")

if __name__ == "__main__":
    test_pattern_chart_fix()
