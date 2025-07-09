#!/usr/bin/env python3
import sqlite3
import pandas as pd
import json

def test_filter_matching():
    """Test if data points are properly matching dashboard filters."""
    
    conn = sqlite3.connect('public_health_data.db')
    
    print("🎯 FILTER MATCHING TEST")
    print("=" * 50)
    
    # Test 1: Borough filter matching
    print("\n🏙️ TESTING BOROUGH FILTERS")
    print("-" * 30)
    
    boroughs = ['Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island']
    
    for borough in boroughs:
        # Test hospital data filtering
        hospital_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM real_hospital_data
            WHERE borough = ?
        """, conn, params=[borough]).iloc[0]['count']
        
        # Test flu data filtering
        flu_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM flu_surveillance_data
            WHERE borough = ?
        """, conn, params=[borough]).iloc[0]['count']
        
        # Test pattern detection filtering
        pattern_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM pattern_detections p
            JOIN real_hospital_data h ON p.hospital_name = h.hospital_name
            WHERE h.borough = ?
        """, conn, params=[borough]).iloc[0]['count']
        
        print(f"   {borough}:")
        print(f"     🏥 Hospital records: {hospital_count}")
        print(f"     🦠 Flu records: {flu_count}")
        print(f"     📊 Pattern records: {pattern_count}")
        
        if hospital_count == 0 and flu_count == 0:
            print(f"     ⚠️  WARNING: No data for {borough}")
    
    # Test 2: ZIP code filter matching
    print("\n📮 TESTING ZIP CODE FILTERS")
    print("-" * 30)
    
    # Get sample ZIP codes from different data sources
    sample_zips = pd.read_sql_query("""
        SELECT DISTINCT zip_code
        FROM real_hospital_data
        LIMIT 5
    """, conn)
    
    for _, row in sample_zips.iterrows():
        zip_code = row['zip_code']
        
        # Test across different data sources
        hospital_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM real_hospital_data
            WHERE zip_code = ?
        """, conn, params=[zip_code]).iloc[0]['count']
        
        flu_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM flu_surveillance_data
            WHERE zip_code = ?
        """, conn, params=[zip_code]).iloc[0]['count']
        
        restaurant_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM restaurant_inspection_data
            WHERE zip_code = ?
        """, conn, params=[zip_code]).iloc[0]['count']
        
        air_quality_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM enhanced_air_quality_data
            WHERE zip_code = ?
        """, conn, params=[zip_code]).iloc[0]['count']
        
        print(f"   ZIP {zip_code}:")
        print(f"     🏥 Hospital: {hospital_count}")
        print(f"     🦠 Flu: {flu_count}")
        print(f"     🍽️ Restaurant: {restaurant_count}")
        print(f"     🌬️ Air Quality: {air_quality_count}")
        
        total_records = hospital_count + flu_count + restaurant_count + air_quality_count
        if total_records == 0:
            print(f"     ⚠️  WARNING: No data for ZIP {zip_code}")
    
    # Test 3: Date range filter matching
    print("\n📅 TESTING DATE RANGE FILTERS")
    print("-" * 30)
    
    # Test recent data (last 30 days)
    recent_hospital = pd.read_sql_query("""
        SELECT COUNT(*) as count
        FROM real_hospital_data
        WHERE date >= date('now', '-30 days')
    """, conn).iloc[0]['count']
    
    recent_flu = pd.read_sql_query("""
        SELECT COUNT(*) as count
        FROM flu_surveillance_data
        WHERE date >= date('now', '-30 days')
    """, conn).iloc[0]['count']
    
    recent_patterns = pd.read_sql_query("""
        SELECT COUNT(*) as count
        FROM pattern_detections
        WHERE date >= date('now', '-30 days')
    """, conn).iloc[0]['count']
    
    print("   Last 30 days:")
    print(f"     🏥 Hospital records: {recent_hospital}")
    print(f"     🦠 Flu records: {recent_flu}")
    print(f"     📊 Pattern records: {recent_patterns}")
    
    if recent_hospital == 0:
        print("     ⚠️  WARNING: No recent hospital data")
    if recent_flu == 0:
        print("     ⚠️  WARNING: No recent flu data")
    
    # Test 4: Illness type filter matching
    print("\n🦠 TESTING ILLNESS TYPE FILTERS")
    print("-" * 30)
    
    illness_types = ['Influenza-like Illness', 'Foodborne Illness Risk', 'Air Quality Related']
    
    for illness_type in illness_types:
        # Count records for each illness type
        flu_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM flu_surveillance_data
            WHERE illness_type = ?
        """, conn, params=[illness_type]).iloc[0]['count']
        
        restaurant_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM restaurant_inspection_data
            WHERE illness_type = ?
        """, conn, params=[illness_type]).iloc[0]['count']
        
        air_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM enhanced_air_quality_data
            WHERE illness_type = ?
        """, conn, params=[illness_type]).iloc[0]['count']
        
        total_count = flu_count + restaurant_count + air_count
        
        print(f"   {illness_type}:")
        print(f"     🦠 Flu data: {flu_count}")
        print(f"     🍽️ Restaurant data: {restaurant_count}")
        print(f"     🌬️ Air quality data: {air_count}")
        print(f"     📊 Total: {total_count}")
        
        if total_count == 0:
            print(f"     ⚠️  WARNING: No data for {illness_type}")
    
    # Test 5: Risk level filter matching
    print("\n⚠️ TESTING RISK LEVEL FILTERS")
    print("-" * 30)
    
    risk_levels = ['LOW', 'MEDIUM', 'HIGH']
    
    for risk_level in risk_levels:
        # Count patterns by risk level
        pattern_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM pattern_detections
            WHERE confidence_level = ?
        """, conn, params=[risk_level]).iloc[0]['count']
        
        # Count foodborne risk by level
        foodborne_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM foodborne_illness_risk_summary
            WHERE risk_level = ?
        """, conn, params=[risk_level]).iloc[0]['count']
        
        # Count air quality risk by level
        air_risk_count = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM air_quality_summary
            WHERE risk_level = ?
        """, conn, params=[risk_level]).iloc[0]['count']
        
        total_count = pattern_count + foodborne_count + air_risk_count
        
        print(f"   {risk_level} Risk:")
        print(f"     📊 Pattern detections: {pattern_count}")
        print(f"     🍽️ Foodborne risk: {foodborne_count}")
        print(f"     🌬️ Air quality risk: {air_risk_count}")
        print(f"     📊 Total: {total_count}")
        
        if total_count == 0:
            print(f"     ⚠️  WARNING: No {risk_level} risk data")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ Filter matching test complete!")

if __name__ == "__main__":
    test_filter_matching()
