#!/usr/bin/env python3
"""
Debug the hospital chart data issue
"""

import requests
import json

def debug_hospital_chart():
    """Debug why the hospital chart is blank."""
    
    base_url = "http://localhost:5000"
    
    print("🐛 DEBUGGING HOSPITAL CHART DATA")
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
            # Test the hospital data API
            print("\n📊 Testing /api/hospital-data response:")
            hospital_response = session.get(f"{base_url}/api/hospital-data?days=30")
            
            if hospital_response.status_code == 200:
                data = hospital_response.json()
                print(f"✅ Hospital API working")
                print(f"📋 Response keys: {list(data.keys())}")
                
                # Check daily_totals
                if 'daily_totals' in data:
                    daily_totals = data['daily_totals']
                    print(f"\n📈 daily_totals found:")
                    print(f"   Type: {type(daily_totals)}")
                    print(f"   Length: {len(daily_totals) if hasattr(daily_totals, '__len__') else 'N/A'}")
                    
                    if len(daily_totals) > 0:
                        print(f"   First item keys: {list(daily_totals[0].keys())}")
                        print(f"   First item: {daily_totals[0]}")
                        print(f"   Last item: {daily_totals[-1]}")
                        
                        # Check if the expected fields exist
                        first_item = daily_totals[0]
                        if 'date' in first_item and 'er_visits_respiratory' in first_item:
                            print(f"   ✅ Chart data format is correct")
                            print(f"   📊 Chart should display {len(daily_totals)} data points")
                        else:
                            print(f"   ❌ Missing expected fields")
                            print(f"   Expected: 'date', 'er_visits_respiratory'")
                            print(f"   Found: {list(first_item.keys())}")
                    else:
                        print(f"   ❌ daily_totals is empty")
                else:
                    print(f"\n❌ 'daily_totals' key NOT FOUND in response")
                    print(f"   Available keys: {list(data.keys())}")
                
                # Check zip_breakdown
                if 'zip_breakdown' in data:
                    zip_breakdown = data['zip_breakdown']
                    print(f"\n📍 zip_breakdown found: {len(zip_breakdown)} items")
                
            else:
                print(f"❌ Hospital API failed: HTTP {hospital_response.status_code}")
                print(f"Response: {hospital_response.text[:200]}...")
        else:
            print(f"❌ Login failed")
    
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    # Also check the database directly
    print(f"\n🗄️ Checking database directly:")
    try:
        import sqlite3
        import pandas as pd
        
        conn = sqlite3.connect('public_health_data.db')
        
        # Check hospital data
        hospital_count = pd.read_sql_query("SELECT COUNT(*) as count FROM real_hospital_data", conn)
        print(f"   Total hospital records: {hospital_count.iloc[0]['count']}")
        
        # Check recent hospital data (last 30 days)
        recent_hospital = pd.read_sql_query("""
            SELECT date, COUNT(*) as records, SUM(respiratory_visits) as total_visits
            FROM real_hospital_data
            WHERE date >= date('now', '-30 days')
            GROUP BY date
            ORDER BY date
        """, conn)
        print(f"   Recent hospital data (last 30 days): {len(recent_hospital)} days")
        
        if len(recent_hospital) > 0:
            print(f"   Date range: {recent_hospital.iloc[0]['date']} to {recent_hospital.iloc[-1]['date']}")
            print(f"   Sample data: {recent_hospital.head(3).to_dict('records')}")
        else:
            print(f"   ❌ No recent hospital data found")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Database check error: {e}")

if __name__ == "__main__":
    debug_hospital_chart()
