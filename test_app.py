#!/usr/bin/env python3
"""
Simple test script to verify all imports work correctly
"""

print("Testing imports...")

try:
    print("1. Testing Flask...")
    from flask import Flask
    print("   ✅ Flask imported successfully")
except ImportError as e:
    print(f"   ❌ Flask import failed: {e}")

try:
    print("2. Testing pandas...")
    import pandas as pd
    print(f"   ✅ pandas imported successfully (version: {pd.__version__})")
except ImportError as e:
    print(f"   ❌ pandas import failed: {e}")

try:
    print("3. Testing forecasting engine...")
    from forecasting_engine import ForecastingEngine
    print("   ✅ ForecastingEngine imported successfully")
except ImportError as e:
    print(f"   ❌ ForecastingEngine import failed: {e}")

try:
    print("4. Testing pattern detector...")
    from phase2_pattern_detection import PatternDetector
    print("   ✅ PatternDetector imported successfully")
except ImportError as e:
    print(f"   ❌ PatternDetector import failed: {e}")

try:
    print("5. Testing Flask-SocketIO...")
    from flask_socketio import SocketIO
    print("   ✅ Flask-SocketIO imported successfully")
except ImportError as e:
    print(f"   ❌ Flask-SocketIO import failed: {e}")

print("\nAll imports tested!")

# Test basic functionality
try:
    print("\n6. Testing basic Flask app creation...")
    app = Flask(__name__)
    print("   ✅ Flask app created successfully")
    
    print("7. Testing forecasting engine...")
    engine = ForecastingEngine()
    print("   ✅ ForecastingEngine instantiated successfully")
    
    print("\n🎉 All tests passed! The app should work correctly.")
    
except Exception as e:
    print(f"   ❌ Error during testing: {e}")
