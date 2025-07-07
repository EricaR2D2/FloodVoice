#!/usr/bin/env python3
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def analyze_data_quality():
    """Comprehensive data quality analysis for Public Health MVP."""
    
    conn = sqlite3.connect('public_health_data.db')
    
    print("🔍 PUBLIC HEALTH MVP - DATA QUALITY ANALYSIS")
    print("=" * 60)
    
    # 1. Check for data freshness issues
    print("\n📅 DATA FRESHNESS ANALYSIS")
    print("-" * 40)
    
    # Check hospital data freshness
    hospital_dates = pd.read_sql_query("""
        SELECT MIN(date) as earliest, MAX(date) as latest, COUNT(*) as records
        FROM real_hospital_data
    """, conn)
    
    if not hospital_dates.empty and hospital_dates.iloc[0]['latest']:
        latest_date = pd.to_datetime(hospital_dates.iloc[0]['latest'])
        days_old = (datetime.now() - latest_date).days
        print(f"🏥 Hospital Data: {hospital_dates.iloc[0]['latest']} ({days_old} days old)")
        if days_old > 7:
            print("   ⚠️  WARNING: Hospital data is outdated")
        else:
            print("   ✅ Hospital data is current")
    
    # Check flu surveillance freshness
    flu_dates = pd.read_sql_query("""
        SELECT MIN(date) as earliest, MAX(date) as latest, COUNT(*) as records
        FROM flu_surveillance_data
    """, conn)
    
    if not flu_dates.empty and flu_dates.iloc[0]['latest']:
        latest_date = pd.to_datetime(flu_dates.iloc[0]['latest'])
        days_old = (datetime.now() - latest_date).days
        print(f"🦠 Flu Data: {flu_dates.iloc[0]['latest']} ({days_old} days old)")
        if days_old > 30:
            print("   ⚠️  WARNING: Flu surveillance data is outdated")
        else:
            print("   ✅ Flu surveillance data is acceptable")
    
    # 2. Check for missing/null values
    print("\n🔍 MISSING DATA ANALYSIS")
    print("-" * 40)
    
    # Check hospital data completeness
    hospital_nulls = pd.read_sql_query("""
        SELECT 
            COUNT(*) as total_records,
            SUM(CASE WHEN hospital_name IS NULL THEN 1 ELSE 0 END) as null_hospital_names,
            SUM(CASE WHEN zip_code IS NULL THEN 1 ELSE 0 END) as null_zip_codes,
            SUM(CASE WHEN respiratory_visits IS NULL THEN 1 ELSE 0 END) as null_respiratory_visits,
            SUM(CASE WHEN total_visits IS NULL THEN 1 ELSE 0 END) as null_total_visits
        FROM real_hospital_data
    """, conn)
    
    print("🏥 Hospital Data Completeness:")
    for col in ['null_hospital_names', 'null_zip_codes', 'null_respiratory_visits', 'null_total_visits']:
        null_count = hospital_nulls.iloc[0][col]
        total = hospital_nulls.iloc[0]['total_records']
        pct = (null_count / total * 100) if total > 0 else 0
        status = "⚠️" if pct > 5 else "✅"
        print(f"   {status} {col.replace('null_', '').replace('_', ' ').title()}: {null_count}/{total} ({pct:.1f}% missing)")
    
    # 3. Check for data consistency issues
    print("\n⚖️ DATA CONSISTENCY ANALYSIS")
    print("-" * 40)
    
    # Check for impossible values in hospital data
    hospital_consistency = pd.read_sql_query("""
        SELECT 
            COUNT(*) as total_records,
            SUM(CASE WHEN respiratory_visits > total_visits THEN 1 ELSE 0 END) as respiratory_exceeds_total,
            SUM(CASE WHEN respiratory_visits < 0 THEN 1 ELSE 0 END) as negative_respiratory,
            SUM(CASE WHEN total_visits < 0 THEN 1 ELSE 0 END) as negative_total,
            SUM(CASE WHEN respiratory_percentage > 100 THEN 1 ELSE 0 END) as percentage_over_100
        FROM real_hospital_data
    """, conn)
    
    print("🏥 Hospital Data Consistency:")
    consistency_checks = [
        ('respiratory_exceeds_total', 'Respiratory visits > Total visits'),
        ('negative_respiratory', 'Negative respiratory visits'),
        ('negative_total', 'Negative total visits'),
        ('percentage_over_100', 'Percentage > 100%')
    ]
    
    for col, desc in consistency_checks:
        issue_count = hospital_consistency.iloc[0][col]
        status = "⚠️" if issue_count > 0 else "✅"
        print(f"   {status} {desc}: {issue_count} records")
    
    # 4. Check filter matching issues
    print("\n🎯 FILTER MATCHING ANALYSIS")
    print("-" * 40)
    
    # Check ZIP code format consistency
    zip_formats = pd.read_sql_query("""
        SELECT 
            LENGTH(zip_code) as zip_length,
            COUNT(*) as count,
            MIN(zip_code) as example
        FROM real_hospital_data
        WHERE zip_code IS NOT NULL
        GROUP BY LENGTH(zip_code)
        ORDER BY count DESC
    """, conn)
    
    print("📮 ZIP Code Format Analysis:")
    for _, row in zip_formats.iterrows():
        status = "✅" if row['zip_length'] == 5 else "⚠️"
        print(f"   {status} Length {row['zip_length']}: {row['count']} records (e.g., {row['example']})")
    
    # Check borough consistency
    borough_consistency = pd.read_sql_query("""
        SELECT borough, COUNT(*) as count
        FROM real_hospital_data
        WHERE borough IS NOT NULL
        GROUP BY borough
        ORDER BY count DESC
    """, conn)
    
    print("\n🏙️ Borough Distribution:")
    expected_boroughs = ['Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island']
    for _, row in borough_consistency.iterrows():
        status = "✅" if row['borough'] in expected_boroughs else "⚠️"
        print(f"   {status} {row['borough']}: {row['count']} records")
    
    # 5. Check pattern detection data quality
    print("\n🔍 PATTERN DETECTION ANALYSIS")
    print("-" * 40)
    
    pattern_stats = pd.read_sql_query("""
        SELECT 
            COUNT(*) as total_patterns,
            COUNT(DISTINCT hospital_name) as unique_hospitals,
            COUNT(DISTINCT zip_code) as unique_zip_codes,
            AVG(confidence_score) as avg_confidence,
            MIN(date) as earliest_pattern,
            MAX(date) as latest_pattern
        FROM pattern_detections
    """, conn)
    
    print("📊 Pattern Detection Summary:")
    print(f"   Total patterns detected: {pattern_stats.iloc[0]['total_patterns']:,}")
    print(f"   Unique hospitals: {pattern_stats.iloc[0]['unique_hospitals']}")
    print(f"   Unique ZIP codes: {pattern_stats.iloc[0]['unique_zip_codes']}")
    print(f"   Average confidence: {pattern_stats.iloc[0]['avg_confidence']:.2f}")
    print(f"   Date range: {pattern_stats.iloc[0]['earliest_pattern']} to {pattern_stats.iloc[0]['latest_pattern']}")
    
    # Check for patterns with missing explanations
    missing_explanations = pd.read_sql_query("""
        SELECT COUNT(*) as patterns_without_explanation
        FROM pattern_detections
        WHERE ai_explanation IS NULL OR ai_explanation = ''
    """, conn)
    
    missing_count = missing_explanations.iloc[0]['patterns_without_explanation']
    total_patterns = pattern_stats.iloc[0]['total_patterns']
    missing_pct = (missing_count / total_patterns * 100) if total_patterns > 0 else 0
    status = "⚠️" if missing_pct > 10 else "✅"
    print(f"   {status} Patterns without AI explanation: {missing_count} ({missing_pct:.1f}%)")
    
    # 6. Check data source diversity
    print("\n📊 DATA SOURCE DIVERSITY")
    print("-" * 40)
    
    # Check different data sources
    data_sources = pd.read_sql_query("""
        SELECT 'Hospital' as data_type, data_source, COUNT(*) as records
        FROM real_hospital_data
        GROUP BY data_source
        UNION ALL
        SELECT 'Flu Surveillance' as data_type, data_source, COUNT(*) as records
        FROM flu_surveillance_data
        GROUP BY data_source
        UNION ALL
        SELECT 'Restaurant Inspections' as data_type, data_source, COUNT(*) as records
        FROM restaurant_inspection_data
        GROUP BY data_source
        UNION ALL
        SELECT 'Air Quality' as data_type, data_source, COUNT(*) as records
        FROM enhanced_air_quality_data
        GROUP BY data_source
    """, conn)
    
    for _, row in data_sources.iterrows():
        print(f"   📈 {row['data_type']}: {row['data_source']} ({row['records']:,} records)")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Data quality analysis complete!")

if __name__ == "__main__":
    analyze_data_quality()
