#!/usr/bin/env python3
"""Quick database check to diagnose map issues"""

import sqlite3
import json
import os

def check_database():
    """Check database tables and data"""
    try:
        conn = sqlite3.connect('public_health_data.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ Database tables: {[t[0] for t in tables]}")
        
        # Check COVID data - try different table names
        covid_tables = ['covid_daily_counts', 'nyc_covid_data', 'unified_health_data']
        for table in covid_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table} records: {count}")

                # Show sample data
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                sample = cursor.fetchall()
                print(f"   Sample data: {sample}")
            except Exception as e:
                print(f"❌ {table} error: {e}")
        
        # Test the exact query used by choropleth system
        print("\n🔍 Testing choropleth COVID query...")
        query = """
            SELECT 'Bronx' as area, SUM(BX_CASE_COUNT) as value, 'Cases' as metric
            FROM nyc_covid_data WHERE BX_CASE_COUNT IS NOT NULL
            UNION ALL
            SELECT 'Brooklyn' as area, SUM(BK_CASE_COUNT) as value, 'Cases' as metric
            FROM nyc_covid_data WHERE BK_CASE_COUNT IS NOT NULL
            UNION ALL
            SELECT 'Manhattan' as area, SUM(MN_CASE_COUNT) as value, 'Cases' as metric
            FROM nyc_covid_data WHERE MN_CASE_COUNT IS NOT NULL
            UNION ALL
            SELECT 'Queens' as area, SUM(QN_CASE_COUNT) as value, 'Cases' as metric
            FROM nyc_covid_data WHERE QN_CASE_COUNT IS NOT NULL
            UNION ALL
            SELECT 'Staten Island' as area, SUM(SI_CASE_COUNT) as value, 'Cases' as metric
            FROM nyc_covid_data WHERE SI_CASE_COUNT IS NOT NULL
        """
        cursor.execute(query)
        covid_results = cursor.fetchall()
        print(f"✅ COVID choropleth query results: {covid_results}")

        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_geojson():
    """Check GeoJSON files"""
    try:
        geojson_path = os.path.join('static', 'nyc_zipcodes.geojson')
        if os.path.exists(geojson_path):
            with open(geojson_path, 'r') as f:
                data = json.load(f)
            print(f"✅ GeoJSON loaded: {len(data['features'])} ZIP codes")
            return True
        else:
            print(f"❌ GeoJSON not found: {geojson_path}")
            return False
    except Exception as e:
        print(f"❌ GeoJSON error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Diagnosing map issues...")
    db_ok = check_database()
    geojson_ok = check_geojson()
    
    if db_ok and geojson_ok:
        print("✅ Basic components look good - issue might be in the web interface")
    else:
        print("❌ Found issues with basic components")
