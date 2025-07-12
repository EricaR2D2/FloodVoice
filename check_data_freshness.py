#!/usr/bin/env python3
"""
Check current data freshness across all sources
"""

import sqlite3
import pandas as pd
from datetime import datetime

def check_data_freshness():
    """Check freshness of all data sources."""
    
    print("🔍 CHECKING CURRENT DATA FRESHNESS")
    print("=" * 50)
    
    conn = sqlite3.connect('public_health_data.db')
    
    # Data sources to check
    data_sources = [
        ('Hospital Data', 'real_hospital_data', 'date'),
        ('NYC COVID Data', 'nyc_covid_data', 'date_of_interest'),
        ('COVID Daily Counts', 'covid_daily_counts', 'date_of_interest'),
        ('Enhanced Air Quality', 'enhanced_air_quality_data', 'date'),
        ('Restaurant Data', 'restaurant_inspection_data', 'date'),
        ('CDC ILI Data', 'cdc_ili_data', 'week_ending_date'),
        ('Flu Surveillance', 'flu_surveillance_data', 'date')
    ]
    
    freshness_data = []
    
    for name, table, date_col in data_sources:
        try:
            # Check if table exists
            table_check = pd.read_sql_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'", conn)
            
            if table_check.empty:
                print(f"⚠️ {name}: Table '{table}' does not exist")
                continue
            
            # Get latest date and record count
            query = f"SELECT MAX({date_col}) as latest_date, COUNT(*) as total_records FROM {table}"
            result = pd.read_sql_query(query, conn)
            
            if not result.empty and result.iloc[0]['latest_date']:
                latest_date_str = result.iloc[0]['latest_date']
                total_records = result.iloc[0]['total_records']
                
                # Parse date (handle different formats)
                try:
                    if ' ' in str(latest_date_str):
                        latest_date = datetime.strptime(latest_date_str.split(' ')[0], '%Y-%m-%d')
                    else:
                        latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')
                except:
                    latest_date = datetime.strptime(str(latest_date_str)[:10], '%Y-%m-%d')
                
                days_old = (datetime.now() - latest_date).days
                
                status = "🟢 CURRENT" if days_old <= 7 else "🟡 RECENT" if days_old <= 30 else "🔴 OUTDATED"
                
                print(f"{status} {name}:")
                print(f"   Latest: {latest_date.strftime('%Y-%m-%d')} ({days_old} days old)")
                print(f"   Records: {total_records:,}")
                
                freshness_data.append({
                    'name': name,
                    'table': table,
                    'latest_date': latest_date,
                    'latest_date_str': latest_date.strftime('%Y-%m-%d'),
                    'days_old': days_old,
                    'total_records': total_records,
                    'status': status
                })
            else:
                print(f"⚠️ {name}: No data found in table '{table}'")
                
        except Exception as e:
            print(f"❌ {name}: Error checking data - {e}")
    
    conn.close()
    
    # Find the most recent date across all sources
    if freshness_data:
        most_recent = min(freshness_data, key=lambda x: x['days_old'])
        print(f"\n📅 MOST RECENT DATA:")
        print(f"   Source: {most_recent['name']}")
        print(f"   Date: {most_recent['latest_date_str']}")
        print(f"   Days old: {most_recent['days_old']}")
        
        # Check what the dashboard is currently showing
        print(f"\n🎯 DASHBOARD IMPACT:")
        if most_recent['days_old'] <= 7:
            print(f"   ✅ Dashboard will show CURRENT data")
        elif most_recent['days_old'] <= 30:
            print(f"   ⚠️ Dashboard will show RECENT data")
        else:
            print(f"   ❌ Dashboard will show OUTDATED data")
            
        return most_recent['latest_date_str']
    else:
        print(f"\n❌ No valid data found in any source")
        return None

if __name__ == "__main__":
    latest_date = check_data_freshness()
    print(f"\n🎯 RECOMMENDED ACTION:")
    if latest_date:
        latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
        days_old = (datetime.now() - latest_dt).days
        
        if days_old > 7:
            print(f"   📅 Update data to show more recent July dates")
            print(f"   🎯 Target: {datetime.now().strftime('%Y-%m-%d')} (today)")
        else:
            print(f"   ✅ Data freshness is acceptable for demo")
    else:
        print(f"   ❌ Need to investigate data availability")
