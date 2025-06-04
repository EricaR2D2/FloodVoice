#!/usr/bin/env python3
"""
Comprehensive test suite for the Scenario Simulation Engine
"""

import requests
import json

def test_scenario_simulation():
    """Test different threshold scenarios to demonstrate the simulation engine"""
    
    print("🎯 **SCENARIO SIMULATION ENGINE - COMPREHENSIVE TEST**")
    print("=" * 60)
    
    # Test scenarios with different sensitivity levels
    scenarios = [
        {
            "name": "Conservative (Default)",
            "description": "Standard thresholds - fewer, high-confidence alerts",
            "params": {
                "sim_spike_percentage": 30,
                "sim_drop_percentage": 30,
                "sim_high_value_threshold": 20,
                "days_back": 365
            }
        },
        {
            "name": "Moderate Sensitivity",
            "description": "Balanced thresholds - moderate alert volume",
            "params": {
                "sim_spike_percentage": 25,
                "sim_drop_percentage": 25,
                "sim_high_value_threshold": 18,
                "days_back": 365
            }
        },
        {
            "name": "High Sensitivity",
            "description": "Lower thresholds - more alerts, early detection",
            "params": {
                "sim_spike_percentage": 20,
                "sim_drop_percentage": 20,
                "sim_high_value_threshold": 15,
                "days_back": 365
            }
        },
        {
            "name": "Very High Sensitivity",
            "description": "Very low thresholds - maximum alert coverage",
            "params": {
                "sim_spike_percentage": 15,
                "sim_drop_percentage": 15,
                "sim_high_value_threshold": 10,
                "days_back": 365
            }
        }
    ]
    
    results = []
    
    for scenario in scenarios:
        print(f"\n📊 **{scenario['name']}**")
        print(f"📝 {scenario['description']}")
        print(f"⚙️  Thresholds: Spike {scenario['params']['sim_spike_percentage']}%, Drop {scenario['params']['sim_drop_percentage']}%, High {scenario['params']['sim_high_value_threshold']}%")
        
        try:
            response = requests.post(
                'http://localhost:5000/api/simulate-alerts',
                json=scenario['params'],
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                alerts_found = data['alerts_found']
                
                print(f"✅ Simulation successful: {alerts_found} alerts found")
                
                # Analyze alert types
                if data['simulated_alerts']:
                    alert_types = {}
                    for alert in data['simulated_alerts']:
                        alert_type = alert['pattern_type']
                        if alert_type not in alert_types:
                            alert_types[alert_type] = 0
                        alert_types[alert_type] += 1
                    
                    print(f"📈 Alert breakdown: {dict(alert_types)}")
                    
                    # Show sample alerts
                    print("📋 Sample alerts:")
                    for i, alert in enumerate(data['simulated_alerts'][:3]):
                        print(f"   {i+1}. {alert['date']} - {alert['pattern_type']} in ZIP {alert['zip_code']}")
                        print(f"      {alert['brief_description']}")
                
                results.append({
                    'scenario': scenario['name'],
                    'alerts': alerts_found,
                    'thresholds': scenario['params']
                })
                
            else:
                print(f"❌ Simulation failed: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Summary analysis
    print("\n" + "=" * 60)
    print("📊 **SIMULATION RESULTS SUMMARY**")
    print("=" * 60)
    
    for result in results:
        print(f"{result['scenario']:20} | {result['alerts']:3} alerts | Spike: {result['thresholds']['sim_spike_percentage']:2}% Drop: {result['thresholds']['sim_drop_percentage']:2}% High: {result['thresholds']['sim_high_value_threshold']:2}%")
    
    if len(results) > 1:
        min_alerts = min(r['alerts'] for r in results)
        max_alerts = max(r['alerts'] for r in results)
        print(f"\n📈 **Sensitivity Impact**: {min_alerts} → {max_alerts} alerts ({max_alerts - min_alerts:+} difference)")
        print(f"🎯 **Recommendation**: Choose thresholds based on desired alert volume and response capacity")
    
    print("\n✅ **Scenario Simulation Engine Test Complete!**")
    print("🎉 The simulation successfully demonstrates 'what-if' analysis capabilities")

if __name__ == "__main__":
    test_scenario_simulation()
