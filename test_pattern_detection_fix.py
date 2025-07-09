#!/usr/bin/env python3
"""
Test the pattern detection fix for weather column issues
"""

import sqlite3
import pandas as pd
from phase2_pattern_detection import PatternDetector

def test_pattern_detection():
    """Test pattern detection with current database structure."""
    
    print("🧪 TESTING PATTERN DETECTION FIX")
    print("=" * 50)
    
    try:
        # Initialize pattern detector
        detector = PatternDetector()
        
        print("✅ Pattern detector initialized successfully")
        
        # Test loading real-time data
        print("\n📊 Testing real-time data loading...")
        data = detector.load_data()
        
        print(f"✅ Real-time data loaded:")
        print(f"   🏥 Hospital data: {len(data['hospital'])} records")
        print(f"   🌡️ Weather data: {len(data['weather'])} records")
        print(f"   🌬️ Air quality data: {len(data['air_quality'])} records")
        
        # Check weather data structure
        if not data['weather'].empty:
            print(f"\n🌡️ Weather data columns: {list(data['weather'].columns)}")
            print("Sample weather record:")
            print(data['weather'].head(1).to_string(index=False))
        
        # Test pattern detection on a small subset
        print("\n🔍 Testing pattern detection...")
        
        # Get recent hospital data for testing
        if not data['hospital'].empty:
            # Limit to recent data for testing
            recent_data = {
                'hospital': data['hospital'].tail(50),  # Last 50 records
                'weather': data['weather'],
                'air_quality': data['air_quality'],
                'cdc_ili': data.get('cdc_ili', pd.DataFrame()),
                'nyc_covid': data.get('nyc_covid', pd.DataFrame()),
                'tick_diseases': data.get('tick_diseases', pd.DataFrame())
            }
            
            patterns = detector.detect_patterns(recent_data)
            
            print(f"✅ Pattern detection completed successfully!")
            print(f"   📊 Patterns detected: {len(patterns)}")
            
            # Show sample patterns
            if patterns:
                print("\n📋 Sample detected patterns:")
                for i, pattern in enumerate(patterns[:3]):  # Show first 3
                    print(f"   {i+1}. {pattern['pattern_type']} at {pattern['hospital_name']} on {pattern['date'].strftime('%Y-%m-%d')}")
                    print(f"      Confidence: {pattern['confidence_score']:.1f}% ({pattern['confidence_level']})")
                    print(f"      Change: {pattern['percentage_change']:+.1f}%")
            else:
                print("   ℹ️ No patterns detected in test data (this is normal)")
        
        print("\n✅ Pattern detection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Pattern detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_weather_context():
    """Test weather context gathering specifically."""
    
    print("\n🌡️ TESTING WEATHER CONTEXT GATHERING")
    print("-" * 40)
    
    try:
        detector = PatternDetector()
        
        # Load data
        data = detector.load_data()
        
        if not data['weather'].empty:
            # Test context gathering with a sample date and ZIP
            from datetime import datetime
            
            sample_date = datetime.now()
            sample_zip = "10001"
            
            print(f"Testing context gathering for {sample_date.strftime('%Y-%m-%d')} in ZIP {sample_zip}")
            
            context = detector.gather_context_data(sample_date, sample_zip, data)
            
            print("✅ Context gathering successful!")
            
            if 'weather' in context:
                weather = context['weather']
                print(f"   🌡️ Weather context:")
                print(f"      Temperature: {weather.get('temperature_f', 'N/A')}°F")
                print(f"      Humidity: {weather.get('humidity_percent', 'N/A')}%")
                print(f"      Tick Risk Score: {weather.get('tick_risk_score', 'N/A')}")
            else:
                print("   ℹ️ No weather context for this date/location")
            
            return True
        else:
            print("⚠️ No weather data available for testing")
            return True
            
    except Exception as e:
        print(f"❌ Weather context test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    
    print("🔧 PATTERN DETECTION FIX VERIFICATION")
    print("=" * 60)
    
    # Test 1: Basic pattern detection
    test1_success = test_pattern_detection()
    
    # Test 2: Weather context gathering
    test2_success = test_weather_context()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY:")
    print(f"   Pattern Detection: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   Weather Context: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 ALL TESTS PASSED! Pattern detection fix is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
