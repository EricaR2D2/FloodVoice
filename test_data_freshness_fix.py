#!/usr/bin/env python3
"""
Test the data freshness fix
"""

import requests
import json

def test_data_freshness_fix():
    """Test that the data freshness now shows a more recent date."""
    
    base_url = "http://localhost:5000"
    
    print("🧪 TESTING DATA FRESHNESS FIX")
    print("=" * 50)
    
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
            # Test the summary API to see the new latest_data_date
            print("\n📊 Testing /api/summary for latest_data_date:")
            summary_response = session.get(f"{base_url}/api/summary")
            
            if summary_response.status_code == 200:
                data = summary_response.json()
                print(f"✅ Summary API working")
                
                # Check the latest_data_date
                latest_data_date = data.get('latest_data_date')
                print(f"\n📅 LATEST DATA DATE:")
                print(f"   Current: {latest_data_date}")
                
                if latest_data_date:
                    from datetime import datetime
                    try:
                        # Parse the date
                        if ' ' in str(latest_data_date):
                            date_part = latest_data_date.split(' ')[0]
                        else:
                            date_part = latest_data_date
                        
                        latest_dt = datetime.strptime(date_part, '%Y-%m-%d')
                        days_old = (datetime.now() - latest_dt).days
                        
                        print(f"   Days old: {days_old}")
                        
                        if days_old <= 7:
                            print(f"   ✅ EXCELLENT: Data is current (≤7 days)")
                        elif days_old <= 14:
                            print(f"   ✅ GOOD: Data is recent (≤14 days)")
                        elif days_old <= 30:
                            print(f"   ⚠️ ACCEPTABLE: Data is somewhat recent (≤30 days)")
                        else:
                            print(f"   ❌ POOR: Data is outdated (>30 days)")
                        
                        # Check if it's better than June 9
                        june_9 = datetime.strptime('2025-06-09', '%Y-%m-%d')
                        if latest_dt > june_9:
                            improvement_days = (latest_dt - june_9).days
                            print(f"   🎯 IMPROVEMENT: {improvement_days} days newer than Jun 9")
                        else:
                            print(f"   ❌ NO IMPROVEMENT: Still showing old date")
                            
                    except Exception as e:
                        print(f"   ❌ Could not parse date: {e}")
                else:
                    print(f"   ❌ No latest_data_date found")
                
                # Also check data_freshness details
                if 'data_freshness' in data:
                    print(f"\n📊 DATA FRESHNESS BREAKDOWN:")
                    for source, freshness in data['data_freshness'].items():
                        status = freshness.get('status', 'unknown')
                        latest = freshness.get('latest_date', 'unknown')
                        days_old = freshness.get('days_old', 'unknown')
                        print(f"   {source}: {latest} ({days_old} days old, {status})")
                
            else:
                print(f"❌ Summary API failed: HTTP {summary_response.status_code}")
        else:
            print(f"❌ Login failed")
    
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_freshness_fix()
