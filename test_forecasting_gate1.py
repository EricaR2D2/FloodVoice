#!/usr/bin/env python3
"""
Testing & Validation Gate 1: Forecasting Functionality Test
===========================================================

Test Criteria:
1. Each alert detail view reliably shows a 3-7 day forecast
2. Confidence intervals (95%) are displayed numerically alongside point forecasts
3. If charted, confidence bands are visible and correctly plotted
4. Forecasts appear reasonable given recent historical data
5. Clear error messages for insufficient data cases

This script tests the forecasting API endpoints and validates the responses.
"""

import requests
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import time

class ForecastingGate1Validator:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def setup_test_session(self):
        """Setup authenticated session for testing."""
        print("🔐 Setting up test session...")
        
        # Try to access the main page to check if authentication is required
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200 and "login" not in response.url.lower():
                print("✅ No authentication required")
                return True
            else:
                print("🔑 Authentication required - attempting login...")
                # Try default test credentials
                login_data = {
                    'username': 'admin',
                    'password': 'admin123'
                }
                login_response = self.session.post(f"{self.base_url}/login", data=login_data)
                if login_response.status_code == 200:
                    print("✅ Successfully logged in")
                    return True
                else:
                    print("❌ Login failed")
                    return False
        except Exception as e:
            print(f"❌ Error setting up session: {e}")
            return False
    
    def get_test_patterns(self):
        """Get patterns from database for testing."""
        print("📊 Fetching test patterns from database...")
        
        try:
            conn = sqlite3.connect('public_health_data.db')
            # First try to get NYC COVID real patterns with sufficient data
            query = """
                SELECT id, date, zip_code, hospital_name, pattern_type,
                       current_value, percentage_change
                FROM pattern_detections
                WHERE hospital_name IN ('Bronx Medical Center', 'Brooklyn Health Center',
                                       'Manhattan Hospital', 'Queens Medical Center', 'Staten Island Hospital')
                ORDER BY id DESC
                LIMIT 10
            """
            df = pd.read_sql_query(query, conn)

            # If no NYC patterns, fall back to test patterns
            if len(df) == 0:
                query = """
                    SELECT id, date, zip_code, hospital_name, pattern_type,
                           current_value, percentage_change
                    FROM pattern_detections
                    WHERE hospital_name LIKE 'Test Forecasting%'
                    ORDER BY id DESC
                    LIMIT 10
                """
                df = pd.read_sql_query(query, conn)
            conn.close()
            
            if len(df) == 0:
                print("❌ No patterns found in database")
                return []
            
            patterns = df.to_dict('records')
            print(f"✅ Found {len(patterns)} patterns for testing")
            
            # Group by pattern type for comprehensive testing
            pattern_types = {}
            for pattern in patterns:
                ptype = pattern['pattern_type']
                if ptype not in pattern_types:
                    pattern_types[ptype] = []
                pattern_types[ptype].append(pattern)
            
            print(f"📈 Pattern types available: {list(pattern_types.keys())}")
            return patterns
            
        except Exception as e:
            print(f"❌ Error fetching patterns: {e}")
            return []
    
    def test_forecast_api_endpoint(self, pattern_id):
        """Test the forecast API endpoint for a specific pattern."""
        print(f"\n🔬 Testing forecast API for pattern ID: {pattern_id}")
        
        try:
            url = f"{self.base_url}/api/pattern/{pattern_id}/forecast"
            response = self.session.get(url, timeout=30)
            
            test_result = {
                'pattern_id': pattern_id,
                'api_status_code': response.status_code,
                'response_time': response.elapsed.total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
            
            if response.status_code != 200:
                test_result['error'] = f"HTTP {response.status_code}"
                test_result['passed'] = False
                print(f"❌ API call failed: HTTP {response.status_code}")
                return test_result
            
            # Parse JSON response
            try:
                forecast_data = response.json()
                test_result['forecast_data'] = forecast_data
            except json.JSONDecodeError as e:
                test_result['error'] = f"Invalid JSON response: {e}"
                test_result['passed'] = False
                print(f"❌ Invalid JSON response: {e}")
                return test_result
            
            # Validate forecast structure and content
            validation_result = self.validate_forecast_response(forecast_data)
            test_result.update(validation_result)
            
            return test_result
            
        except requests.exceptions.Timeout:
            test_result['error'] = "Request timeout"
            test_result['passed'] = False
            print(f"❌ Request timeout")
            return test_result
        except Exception as e:
            test_result['error'] = str(e)
            test_result['passed'] = False
            print(f"❌ Unexpected error: {e}")
            return test_result
    
    def validate_forecast_response(self, forecast_data):
        """Validate forecast response against Gate 1 criteria."""
        print("🔍 Validating forecast response...")
        
        validation = {
            'has_forecast': False,
            'has_confidence_intervals': False,
            'forecast_length_valid': False,
            'values_reasonable': False,
            'error_handling_appropriate': False,
            'passed': False
        }
        
        # Check if this is an error response
        if forecast_data.get('status') == 'error':
            error_msg = forecast_data.get('message', forecast_data.get('error_message', ''))
            print(f"📝 Error response: {error_msg}")
            
            # Validate error message quality
            if any(keyword in error_msg.lower() for keyword in 
                   ['insufficient', 'limited', 'data', 'forecast', 'available']):
                validation['error_handling_appropriate'] = True
                validation['passed'] = True
                print("✅ Appropriate error message for insufficient data")
            else:
                print("❌ Error message not descriptive enough")
            
            return validation
        
        # Check for successful forecast
        if forecast_data.get('status') == 'success':
            validation['has_forecast'] = True
            print("✅ Forecast generated successfully")
            
            # Validate forecast dates and values
            dates = forecast_data.get('dates', [])
            values = forecast_data.get('values', [])
            lower_bounds = forecast_data.get('lower_bound', [])
            upper_bounds = forecast_data.get('upper_bound', [])
            
            # Check forecast length (3-7 days)
            if 3 <= len(dates) <= 7 and len(dates) == len(values):
                validation['forecast_length_valid'] = True
                print(f"✅ Forecast length valid: {len(dates)} days")
            else:
                print(f"❌ Invalid forecast length: {len(dates)} days")
            
            # Check confidence intervals
            if (len(lower_bounds) == len(dates) and len(upper_bounds) == len(dates) and
                all(isinstance(x, (int, float)) for x in lower_bounds + upper_bounds)):
                validation['has_confidence_intervals'] = True
                print("✅ Confidence intervals present and valid")
                
                # Validate CI structure (lower < value < upper)
                ci_valid = all(
                    lower_bounds[i] <= values[i] <= upper_bounds[i]
                    for i in range(len(values))
                )
                if ci_valid:
                    print("✅ Confidence interval bounds are logical")
                else:
                    print("❌ Some confidence intervals have invalid bounds")
            else:
                print("❌ Missing or invalid confidence intervals")
            
            # Check if values are reasonable (positive, not extreme)
            if all(isinstance(v, (int, float)) and v >= 0 and v < 1000 for v in values):
                validation['values_reasonable'] = True
                print("✅ Forecast values appear reasonable")
            else:
                print("❌ Some forecast values appear unreasonable")
            
            # Overall validation
            validation['passed'] = (
                validation['has_forecast'] and
                validation['has_confidence_intervals'] and
                validation['forecast_length_valid'] and
                validation['values_reasonable']
            )
            
        return validation

    def test_alert_detail_page(self, pattern_id):
        """Test the alert detail page to ensure forecast is displayed."""
        print(f"\n🌐 Testing alert detail page for pattern ID: {pattern_id}")

        try:
            url = f"{self.base_url}/alert/{pattern_id}"
            response = self.session.get(url, timeout=30)

            if response.status_code != 200:
                print(f"❌ Alert detail page failed: HTTP {response.status_code}")
                return False

            html_content = response.text

            # Check for forecast section presence
            forecast_indicators = [
                'enhancedForecastChart',
                'enhancedForecastTable',
                'Forecast with Confidence Intervals',
                'Daily Forecast Values',
                'Confidence Interval'
            ]

            found_indicators = [indicator for indicator in forecast_indicators
                              if indicator in html_content]

            if len(found_indicators) >= 3:
                print(f"✅ Alert detail page contains forecast elements: {found_indicators}")
                return True
            else:
                print(f"❌ Alert detail page missing forecast elements. Found: {found_indicators}")
                return False

        except Exception as e:
            print(f"❌ Error testing alert detail page: {e}")
            return False

    def run_comprehensive_test(self):
        """Run comprehensive Gate 1 validation tests."""
        print("🚀 Starting Gate 1 Forecasting Validation Tests")
        print("=" * 60)

        # Setup session
        if not self.setup_test_session():
            print("❌ Failed to setup test session")
            return False

        # Get test patterns
        patterns = self.get_test_patterns()
        if not patterns:
            print("❌ No patterns available for testing")
            return False

        # Test different pattern types
        test_patterns = []
        pattern_types_tested = set()

        for pattern in patterns:
            ptype = pattern['pattern_type']
            if ptype not in pattern_types_tested or len(test_patterns) < 5:
                test_patterns.append(pattern)
                pattern_types_tested.add(ptype)
            if len(test_patterns) >= 8:  # Test up to 8 patterns
                break

        print(f"\n📋 Testing {len(test_patterns)} patterns across {len(pattern_types_tested)} types")

        # Run tests
        passed_tests = 0
        total_tests = 0

        for pattern in test_patterns:
            pattern_id = pattern['id']
            pattern_type = pattern['pattern_type']
            hospital = pattern['hospital_name']
            zip_code = pattern['zip_code']

            print(f"\n{'='*60}")
            print(f"🏥 Testing Pattern: {pattern_type.upper()}")
            print(f"   Hospital: {hospital}")
            print(f"   ZIP Code: {zip_code}")
            print(f"   Pattern ID: {pattern_id}")
            print(f"{'='*60}")

            # Test API endpoint
            api_result = self.test_forecast_api_endpoint(pattern_id)
            self.test_results.append(api_result)

            # Test alert detail page
            page_result = self.test_alert_detail_page(pattern_id)

            # Evaluate overall test result
            test_passed = api_result.get('passed', False) and page_result
            if test_passed:
                passed_tests += 1
                print("✅ OVERALL TEST RESULT: PASSED")
            else:
                print("❌ OVERALL TEST RESULT: FAILED")

            total_tests += 1

            # Add delay between tests
            time.sleep(1)

        # Generate summary report
        self.generate_test_report(passed_tests, total_tests)

        return passed_tests == total_tests

    def generate_test_report(self, passed_tests, total_tests):
        """Generate comprehensive test report."""
        print(f"\n{'='*60}")
        print("📊 GATE 1 FORECASTING VALIDATION REPORT")
        print(f"{'='*60}")

        print(f"🎯 Overall Results: {passed_tests}/{total_tests} tests passed")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Gate 1 criteria met!")
        else:
            print("⚠️  Some tests failed - review issues below")

        # Detailed breakdown
        print(f"\n📋 Detailed Test Results:")

        criteria_summary = {
            'has_forecast': 0,
            'has_confidence_intervals': 0,
            'forecast_length_valid': 0,
            'values_reasonable': 0,
            'error_handling_appropriate': 0
        }

        for result in self.test_results:
            for criterion in criteria_summary:
                if result.get(criterion, False):
                    criteria_summary[criterion] += 1

        print(f"   ✅ Reliable 3-7 day forecasts: {criteria_summary['forecast_length_valid']}/{total_tests}")
        print(f"   ✅ Confidence intervals displayed: {criteria_summary['has_confidence_intervals']}/{total_tests}")
        print(f"   ✅ Reasonable forecast values: {criteria_summary['values_reasonable']}/{total_tests}")
        print(f"   ✅ Appropriate error handling: {criteria_summary['error_handling_appropriate']}/{total_tests}")

        # Performance metrics
        response_times = [r.get('response_time', 0) for r in self.test_results if 'response_time' in r]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            print(f"\n⚡ Performance Metrics:")
            print(f"   Average API response time: {avg_response_time:.2f} seconds")
            print(f"   Fastest response: {min(response_times):.2f} seconds")
            print(f"   Slowest response: {max(response_times):.2f} seconds")

        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"gate1_validation_report_{timestamp}.json"

        report_data = {
            'test_summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': (passed_tests/total_tests)*100,
                'timestamp': datetime.now().isoformat()
            },
            'criteria_summary': criteria_summary,
            'detailed_results': self.test_results
        }

        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n💾 Detailed report saved to: {report_file}")

def main():
    """Main test execution function."""
    print("🧪 Gate 1 Forecasting Validation Test Suite")
    print("Testing forecasting functionality against Gate 1 criteria")
    print("=" * 60)

    validator = ForecastingGate1Validator()
    success = validator.run_comprehensive_test()

    if success:
        print("\n🎉 Gate 1 validation PASSED! Forecasting functionality meets all criteria.")
        exit(0)
    else:
        print("\n❌ Gate 1 validation FAILED. Please review the issues and fix them.")
        exit(1)

if __name__ == "__main__":
    main()
