#!/usr/bin/env python3
"""
Debug the pattern chart data issue
"""

import requests
import json

def debug_pattern_chart():
    """Debug why the pattern chart is blank."""
    
    base_url = "http://localhost:5000"
    
    print("🐛 DEBUGGING PATTERN CHART DATA")
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
            # Test the summary API to see what data it returns
            print("\n📊 Testing /api/summary response:")
            summary_response = session.get(f"{base_url}/api/summary")
            
            if summary_response.status_code == 200:
                data = summary_response.json()
                print(f"✅ Summary API working")
                print(f"📋 Response keys: {list(data.keys())}")
                
                # Check if recent_patterns exists and what it contains
                if 'recent_patterns' in data:
                    recent_patterns = data['recent_patterns']
                    print(f"\n📈 recent_patterns found:")
                    print(f"   Type: {type(recent_patterns)}")
                    print(f"   Length: {len(recent_patterns) if hasattr(recent_patterns, '__len__') else 'N/A'}")
                    print(f"   Content: {recent_patterns}")
                else:
                    print(f"\n❌ 'recent_patterns' key NOT FOUND in response")
                    print(f"   Available keys: {list(data.keys())}")
                
            else:
                print(f"❌ Summary API failed: HTTP {summary_response.status_code}")
            
            # Test the patterns API separately
            print(f"\n📊 Testing /api/patterns response:")
            patterns_response = session.get(f"{base_url}/api/patterns?limit=10")
            
            if patterns_response.status_code == 200:
                patterns_data = patterns_response.json()
                print(f"✅ Patterns API working")
                print(f"📋 Response type: {type(patterns_data)}")
                print(f"📋 Response length: {len(patterns_data) if hasattr(patterns_data, '__len__') else 'N/A'}")
                
                if len(patterns_data) > 0:
                    print(f"📋 First pattern keys: {list(patterns_data[0].keys()) if patterns_data else 'No patterns'}")
                    print(f"📋 Sample pattern: {patterns_data[0] if patterns_data else 'No patterns'}")
                else:
                    print(f"⚠️ No patterns returned")
                    
            else:
                print(f"❌ Patterns API failed: HTTP {patterns_response.status_code}")
        
        else:
            print("❌ Login failed")
    
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
        
        # Check pattern_detections table
        pattern_count = pd.read_sql_query("SELECT COUNT(*) as count FROM pattern_detections", conn)
        print(f"   Total patterns in DB: {pattern_count.iloc[0]['count']}")
        
        # Check recent patterns (last 7 days)
        recent_patterns_db = pd.read_sql_query("""
            SELECT pattern_type, COUNT(*) as count
            FROM pattern_detections
            WHERE date >= date('now', '-7 days')
            GROUP BY pattern_type
        """, conn)
        print(f"   Recent patterns (last 7 days): {len(recent_patterns_db)} types")
        print(f"   Pattern types: {recent_patterns_db.to_dict('records') if len(recent_patterns_db) > 0 else 'None'}")
        
        # Check all patterns by type
        all_patterns_db = pd.read_sql_query("""
            SELECT pattern_type, COUNT(*) as count
            FROM pattern_detections
            GROUP BY pattern_type
        """, conn)
        print(f"   All patterns by type: {all_patterns_db.to_dict('records') if len(all_patterns_db) > 0 else 'None'}")
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Database check error: {e}")

if __name__ == "__main__":
    debug_pattern_chart()
