#!/usr/bin/env python3
"""
Test script for the simulation API endpoint
"""

import requests
import json

def test_simulation_api():
    """Test the simulation API endpoint"""
    
    # Test parameters - more sensitive thresholds to see more alerts
    simulation_params = {
        "sim_spike_percentage": 20,  # More sensitive spike threshold
        "sim_drop_percentage": 20,   # More sensitive drop threshold
        "sim_high_value_threshold": 15,  # More sensitive consistently high threshold
        "days_back": 365  # Look at all available data
    }
    
    print("🧪 Testing Simulation API Endpoint")
    print(f"📊 Parameters: {simulation_params}")
    print("🚀 Sending request...")
    
    try:
        response = requests.post(
            'http://localhost:5000/api/simulate-alerts',
            json=simulation_params,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Simulation successful!")
            print(f"📈 Alerts found: {data['alerts_found']}")
            print(f"⚙️  Simulation params: {data['simulation_params']}")
            
            if data['simulated_alerts']:
                print("\n📋 Sample alerts:")
                for i, alert in enumerate(data['simulated_alerts'][:3]):  # Show first 3
                    print(f"  {i+1}. {alert['date']} - {alert['pattern_type']} in ZIP {alert['zip_code']}")
                    print(f"     {alert['brief_description']}")
                
                if len(data['simulated_alerts']) > 3:
                    print(f"     ... and {len(data['simulated_alerts']) - 3} more alerts")
            else:
                print("📭 No alerts found with these thresholds")
                
        else:
            print(f"❌ Simulation failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing simulation: {e}")

if __name__ == "__main__":
    test_simulation_api()
