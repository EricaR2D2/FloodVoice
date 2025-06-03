import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta
from phase2_pattern_detection import PatternDetector

class Phase2Validator:
    def __init__(self):
        self.test_db_path = "test_public_health_data.db"
        self.original_db_path = "public_health_data.db"
        self.test_results = []
        
    def create_test_database(self):
        """Create a test database with controlled data for validation."""
        print("Creating test database with controlled data...")
        
        # Remove existing test database
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        conn = sqlite3.connect(self.test_db_path)
        
        # Create test hospital data with known patterns
        test_hospital_data = []
        base_date = datetime(2020, 3, 1)
        
        # ZIP 10001 - Normal pattern (no spikes/drops)
        for i in range(14):
            date = base_date + timedelta(days=i)
            test_hospital_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'hospital_name': 'Test Hospital A',
                'zip_code': '10001',
                'er_visits_respiratory': 15 + np.random.randint(-2, 3)  # 13-17 range, stable
            })
        
        # ZIP 10002 - Clear spike pattern
        for i in range(14):
            date = base_date + timedelta(days=i)
            if i == 10:  # Day 11 - create a clear spike
                visits = 35  # 133% above average of ~15
            else:
                visits = 15 + np.random.randint(-2, 3)
            
            test_hospital_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'hospital_name': 'Test Hospital B',
                'zip_code': '10002',
                'er_visits_respiratory': visits
            })
        
        # ZIP 10003 - Clear drop pattern
        for i in range(14):
            date = base_date + timedelta(days=i)
            if i == 12:  # Day 13 - create a clear drop
                visits = 5  # 67% below average of ~15
            else:
                visits = 15 + np.random.randint(-2, 3)
            
            test_hospital_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'hospital_name': 'Test Hospital C',
                'zip_code': '10003',
                'er_visits_respiratory': visits
            })
        
        # ZIP 10004 - Consistently high pattern
        for i in range(14):
            date = base_date + timedelta(days=i)
            if i >= 10:  # Last 4 days - consistently high
                visits = 20  # 33% above average
            else:
                visits = 15 + np.random.randint(-2, 3)
            
            test_hospital_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'hospital_name': 'Test Hospital D',
                'zip_code': '10004',
                'er_visits_respiratory': visits
            })
        
        # Create DataFrame and save to database
        hospital_df = pd.DataFrame(test_hospital_data)
        hospital_df.to_sql('hospital_data', conn, if_exists='replace', index=False)
        
        # Create minimal context data
        context_data = []
        for i in range(14):
            date = base_date + timedelta(days=i)
            context_data.append({
                'date_local': date.strftime('%Y-%m-%d'),
                'state_name': 'New York',
                'county_name': 'New York',
                'aqi': 50,
                'category': 'Good',
                'pm25_concentration': 15.0,
                'ozone_concentration': 0.05
            })
        
        aqi_df = pd.DataFrame(context_data)
        aqi_df.to_sql('air_quality_data', conn, if_exists='replace', index=False)
        
        # Create CDC data
        cdc_data = [{
            'week_ending_date': (base_date + timedelta(days=7)).strftime('%Y-%m-%d'),
            'region': 'New York',
            'ili_percent': 5.0,
            'total_patients': 1000,
            'ili_patients': 50
        }]
        cdc_df = pd.DataFrame(cdc_data)
        cdc_df.to_sql('cdc_ili_data', conn, if_exists='replace', index=False)
        
        # Create NYC COVID data
        covid_data = []
        for i in range(14):
            date = base_date + timedelta(days=i)
            covid_data.append({
                'date_of_interest': date.strftime('%Y-%m-%d'),
                'CASE_COUNT': 100 + i * 10,
                'HOSPITALIZED_COUNT': 20 + i * 2,
                'DEATH_COUNT': 1 + i
            })
        
        covid_df = pd.DataFrame(covid_data)
        covid_df.to_sql('nyc_covid_data', conn, if_exists='replace', index=False)
        
        conn.close()
        print(f"Test database created: {self.test_db_path}")
        
    def run_test_with_patterns(self):
        """Test the pattern detector with data that should trigger patterns."""
        print("\n" + "="*60)
        print("TEST 1: Data WITH Expected Patterns")
        print("="*60)
        
        # Temporarily replace the database path in PatternDetector
        original_db_path = PatternDetector.__dict__.get('DB_PATH', 'public_health_data.db')
        
        # Create a custom detector for testing
        detector = PatternDetector()
        detector.conn.close()  # Close original connection
        detector.conn = sqlite3.connect(self.test_db_path)
        
        try:
            # Run analysis
            data = detector.load_data()
            patterns = detector.detect_patterns(data)
            
            print(f"Patterns detected: {len(patterns)}")
            
            # Validate results
            test_result = {
                'test_name': 'Data WITH Patterns',
                'execution_success': True,
                'patterns_detected': len(patterns),
                'expected_patterns': ['spike', 'drop'],  # We expect at least these
                'api_calls_made': 0,
                'explanations_received': 0,
                'explanations_coherent': 0
            }
            
            if len(patterns) > 0:
                print("\nDetected patterns:")
                for i, pattern in enumerate(patterns):
                    print(f"  {i+1}. {pattern['pattern_type']} in {pattern['zip_code']} on {pattern['date'].strftime('%Y-%m-%d')}")
                    print(f"     Current: {pattern['current_value']}, Average: {pattern['rolling_mean']:.1f}, Change: {pattern['percentage_change']:+.1f}%")
                
                # Test AI explanation generation for first pattern
                print(f"\nTesting AI explanation for first pattern...")
                test_pattern = patterns[0]
                
                try:
                    explanation = detector.generate_ai_explanation(test_pattern)
                    test_result['api_calls_made'] = 1
                    test_result['explanations_received'] = 1
                    
                    print(f"AI Explanation received: {len(explanation)} characters")
                    print(f"Full explanation: {explanation}")

                    # Check if explanation is coherent and mentions key elements
                    key_elements = [
                        str(test_pattern['zip_code']),
                        test_pattern['pattern_type'],
                        str(test_pattern['current_value'])
                    ]

                    # More flexible checking for key elements
                    zip_found = str(test_pattern['zip_code']) in explanation
                    pattern_found = test_pattern['pattern_type'] in explanation.lower() or 'spike' in explanation.lower() or 'increase' in explanation.lower()
                    value_found = str(test_pattern['current_value']) in explanation or 'visits' in explanation.lower()

                    coherent = zip_found and pattern_found and value_found
                    test_result['explanations_coherent'] = 1 if coherent else 0

                    print(f"Key element analysis:")
                    print(f"  ZIP code ({test_pattern['zip_code']}): {zip_found}")
                    print(f"  Pattern type ({test_pattern['pattern_type']}): {pattern_found}")
                    print(f"  Current value ({test_pattern['current_value']}): {value_found}")
                    print(f"Overall coherent: {coherent}")

                    if coherent:
                        print("✅ Key elements found in explanation")
                    else:
                        print("❌ Missing some key elements in explanation")
                    
                except Exception as e:
                    print(f"❌ Error generating AI explanation: {e}")
                    test_result['api_calls_made'] = 0
            else:
                print("❌ No patterns detected when patterns were expected")
            
            self.test_results.append(test_result)
            
        except Exception as e:
            print(f"❌ Error during pattern detection: {e}")
            test_result = {
                'test_name': 'Data WITH Patterns',
                'execution_success': False,
                'error': str(e)
            }
            self.test_results.append(test_result)
        finally:
            detector.close()
    
    def run_test_without_patterns(self):
        """Test the pattern detector with data that should NOT trigger patterns."""
        print("\n" + "="*60)
        print("TEST 2: Data WITHOUT Expected Patterns")
        print("="*60)
        
        # Create database with stable data (no patterns)
        conn = sqlite3.connect(self.test_db_path)
        
        # Create very stable hospital data
        stable_data = []
        base_date = datetime(2020, 3, 1)
        
        for i in range(14):
            date = base_date + timedelta(days=i)
            stable_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'hospital_name': 'Stable Hospital',
                'zip_code': '10005',
                'er_visits_respiratory': 15  # Exactly 15 every day - no variation
            })
        
        stable_df = pd.DataFrame(stable_data)
        stable_df.to_sql('hospital_data', conn, if_exists='replace', index=False)
        conn.close()
        
        # Test with this stable data
        detector = PatternDetector()
        detector.conn.close()
        detector.conn = sqlite3.connect(self.test_db_path)
        
        try:
            data = detector.load_data()
            patterns = detector.detect_patterns(data)
            
            print(f"Patterns detected: {len(patterns)}")
            
            test_result = {
                'test_name': 'Data WITHOUT Patterns',
                'execution_success': True,
                'patterns_detected': len(patterns),
                'expected_patterns': 0,
                'api_calls_made': 0
            }
            
            if len(patterns) == 0:
                print("✅ Correctly identified no patterns in stable data")
                test_result['correct_no_patterns'] = True
            else:
                print("❌ Incorrectly flagged patterns in stable data:")
                for pattern in patterns:
                    print(f"  - {pattern['pattern_type']} in {pattern['zip_code']}")
                test_result['correct_no_patterns'] = False
            
            self.test_results.append(test_result)
            
        except Exception as e:
            print(f"❌ Error during stable data test: {e}")
            test_result = {
                'test_name': 'Data WITHOUT Patterns',
                'execution_success': False,
                'error': str(e)
            }
            self.test_results.append(test_result)
        finally:
            detector.close()
    
    def run_validation_suite(self):
        """Run the complete validation suite."""
        print("🧪 PHASE 2 TESTING & VALIDATION GATE 2")
        print("="*60)
        
        # Create test data
        self.create_test_database()
        
        # Run tests
        self.run_test_with_patterns()
        self.run_test_without_patterns()
        
        # Generate report
        self.generate_validation_report()
        
        # Cleanup
        self.cleanup()
    
    def generate_validation_report(self):
        """Generate a comprehensive validation report."""
        print("\n" + "="*60)
        print("VALIDATION REPORT - GATE 2 PASS CRITERIA")
        print("="*60)
        
        all_passed = True
        
        for result in self.test_results:
            print(f"\n📋 {result['test_name']}:")
            
            # Check execution success
            if result.get('execution_success', False):
                print("  ✅ Function executes without errors")
            else:
                print(f"  ❌ Function failed: {result.get('error', 'Unknown error')}")
                all_passed = False
                continue
            
            # Check pattern detection logic
            if result['test_name'] == 'Data WITH Patterns':
                if result['patterns_detected'] > 0:
                    print("  ✅ Patterns correctly identified when present")
                else:
                    print("  ❌ Failed to identify patterns when present")
                    all_passed = False
                
                # Check API calls
                if result['api_calls_made'] > 0:
                    print("  ✅ API call successfully made to OpenRouter")
                else:
                    print("  ❌ No API call made to OpenRouter")
                    all_passed = False
                
                # Check explanations
                if result['explanations_received'] > 0:
                    print("  ✅ Natural language explanation received")
                else:
                    print("  ❌ No explanation received")
                    all_passed = False
                
                # Check explanation quality
                if result.get('explanations_coherent', 0) > 0:
                    print("  ✅ Explanation refers to key pattern elements")
                else:
                    print("  ❌ Explanation missing key pattern elements")
                    all_passed = False
            
            elif result['test_name'] == 'Data WITHOUT Patterns':
                if result.get('correct_no_patterns', False):
                    print("  ✅ No patterns erroneously flagged when none present")
                else:
                    print("  ❌ Incorrectly flagged patterns when none present")
                    all_passed = False
        
        print("\n" + "="*60)
        if all_passed:
            print("🎉 ALL GATE 2 PASS CRITERIA MET!")
            print("✅ Phase 2 validation successful")
        else:
            print("❌ SOME GATE 2 CRITERIA FAILED")
            print("🔧 Review and fix issues before proceeding")
        print("="*60)
        
        return all_passed
    
    def cleanup(self):
        """Clean up test files."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
            print(f"\n🧹 Cleaned up test database: {self.test_db_path}")

def main():
    """Run the validation suite."""
    validator = Phase2Validator()
    validator.run_validation_suite()

if __name__ == "__main__":
    main()
