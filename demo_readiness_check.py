#!/usr/bin/env python3
"""
Comprehensive demo readiness check for Public Health MVP
"""

import requests
import json

def demo_readiness_check():
    """Check if the dashboard is demo-ready."""
    
    base_url = "http://localhost:5000"
    
    print("🎯 PUBLIC HEALTH MVP - DEMO READINESS CHECK")
    print("=" * 60)
    
    issues = []
    successes = []
    
    try:
        # Create a session for login
        session = requests.Session()
        
        # Test 1: Login System
        print("\n1️⃣ TESTING LOGIN SYSTEM")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        if login_response.status_code == 302:
            print("   ✅ Login system working")
            successes.append("Login system functional")
        else:
            print("   ❌ Login system failed")
            issues.append("Login system not working")
        
        # Test 2: Main Dashboard
        print("\n2️⃣ TESTING MAIN DASHBOARD")
        dashboard_response = session.get(f"{base_url}/")
        if dashboard_response.status_code == 200:
            print("   ✅ Main dashboard loads")
            successes.append("Main dashboard accessible")
        else:
            print("   ❌ Main dashboard failed")
            issues.append("Main dashboard not loading")
        
        # Test 3: Dashboard Summary API
        print("\n3️⃣ TESTING DASHBOARD SUMMARY API")
        summary_response = session.get(f"{base_url}/api/summary")
        if summary_response.status_code == 200:
            data = summary_response.json()
            print("   ✅ Summary API working")
            
            # Check key data points
            if 'total_hospital_records' in data and data['total_hospital_records'] > 0:
                print(f"   ✅ Hospital records: {data['total_hospital_records']:,}")
                successes.append(f"Hospital data available ({data['total_hospital_records']:,} records)")
            else:
                print("   ❌ No hospital records")
                issues.append("No hospital data available")
            
            if 'total_patterns_detected' in data and data['total_patterns_detected'] > 0:
                print(f"   ✅ Pattern detections: {data['total_patterns_detected']:,}")
                successes.append(f"Pattern detection working ({data['total_patterns_detected']:,} patterns)")
            else:
                print("   ❌ No pattern detections")
                issues.append("No pattern detections available")
            
            if 'recent_patterns' in data and len(data['recent_patterns']) > 0:
                print(f"   ✅ Recent patterns for chart: {len(data['recent_patterns'])} types")
                successes.append("Pattern chart has data")
            else:
                print("   ❌ No recent patterns for chart")
                issues.append("Pattern chart will be blank")
                
        else:
            print("   ❌ Summary API failed")
            issues.append("Dashboard summary API not working")
        
        # Test 4: Pattern List API
        print("\n4️⃣ TESTING PATTERN LIST API")
        patterns_response = session.get(f"{base_url}/api/patterns?limit=5")
        if patterns_response.status_code == 200:
            patterns = patterns_response.json()
            if len(patterns) > 0:
                print(f"   ✅ Pattern list: {len(patterns)} patterns available")
                successes.append("Pattern list functional")
                
                # Check if patterns have AI explanations
                if patterns[0].get('ai_explanation'):
                    print("   ✅ AI explanations available")
                    successes.append("AI explanations working")
                else:
                    print("   ❌ No AI explanations")
                    issues.append("AI explanations missing")
            else:
                print("   ❌ No patterns in list")
                issues.append("Pattern list empty")
        else:
            print("   ❌ Pattern list API failed")
            issues.append("Pattern list API not working")
        
        # Test 5: Hospital Data API
        print("\n5️⃣ TESTING HOSPITAL DATA API")
        hospital_response = session.get(f"{base_url}/api/hospital-data?days=30")
        if hospital_response.status_code == 200:
            hospital_data = hospital_response.json()
            daily_totals = hospital_data.get('daily_totals', [])
            if hospital_data and len(daily_totals) > 0:
                print(f"   ✅ Hospital chart data: {len(daily_totals)} data points")
                successes.append("Hospital chart has data")
            else:
                print("   ❌ No hospital chart data")
                issues.append("Hospital chart will be blank")
        else:
            print("   ❌ Hospital data API failed")
            issues.append("Hospital data API not working")
        
        # Test 6: Map Data API
        print("\n6️⃣ TESTING MAP DATA API")
        map_response = session.post(f"{base_url}/api/map-data", json={})
        if map_response.status_code == 200:
            print("   ✅ Map data API working")
            successes.append("Map functionality available")
        else:
            print("   ❌ Map data API failed")
            issues.append("Map functionality not working")
        
    except Exception as e:
        print(f"   ❌ Test error: {e}")
        issues.append(f"Test execution error: {e}")
    
    # Summary
    print(f"\n📊 DEMO READINESS SUMMARY")
    print("=" * 40)
    
    print(f"\n✅ WORKING FEATURES ({len(successes)}):")
    for success in successes:
        print(f"   • {success}")
    
    if issues:
        print(f"\n❌ ISSUES FOUND ({len(issues)}):")
        for issue in issues:
            print(f"   • {issue}")
    
    # Overall assessment
    total_tests = len(successes) + len(issues)
    success_rate = (len(successes) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n🎯 OVERALL DEMO READINESS:")
    print(f"   Success Rate: {success_rate:.1f}% ({len(successes)}/{total_tests} features working)")
    
    if success_rate >= 90:
        print(f"   🎉 DEMO READY! System is fully functional")
    elif success_rate >= 75:
        print(f"   ⚠️ MOSTLY READY - Minor issues to address")
    else:
        print(f"   ❌ NOT DEMO READY - Major issues need fixing")
    
    print(f"\n🚀 Dashboard URL: {base_url}")
    print(f"🔐 Login: admin / admin123")

if __name__ == "__main__":
    demo_readiness_check()
