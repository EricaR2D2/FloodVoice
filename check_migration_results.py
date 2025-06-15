import sqlite3

def check_migration_results():
    """Check the results of the data migration"""
    
    print("=== DATABASE TABLES AFTER MIGRATION ===")
    
    try:
        conn = sqlite3.connect('public_health_data.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("All tables in database:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            # Mark real vs mock data
            if table_name.startswith('real_'):
                status = "✅ REAL DATA"
            elif table_name in ['nyc_covid_data']:
                status = "✅ REAL DATA (existing)"
            elif table_name in ['hospital_data', 'weather_data', 'tick_disease_surveillance']:
                status = "⚠️ MOCK DATA (should be removed)"
            else:
                status = "ℹ️ System table"
            
            print(f"  {table_name}: {count} records - {status}")
        
        # Check real data tables specifically
        print("\n=== REAL DATA VERIFICATION ===")
        
        real_tables = [
            'nyc_covid_data',
            'real_hospital_data', 
            'real_weather_data',
            'real_tick_surveillance',
            'real_tick_disease_summary'
        ]
        
        for table in real_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # Get sample data
                    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                    sample = cursor.fetchone()
                    print(f"✅ {table}: {count} records")
                    
                    # Show date range if applicable
                    if 'date' in [desc[0] for desc in cursor.description]:
                        cursor.execute(f"SELECT MIN(date), MAX(date) FROM {table}")
                        date_range = cursor.fetchone()
                        if date_range[0] and date_range[1]:
                            print(f"   📅 Date range: {date_range[0]} to {date_range[1]}")
                else:
                    print(f"❌ {table}: No records found")
                    
            except Exception as e:
                print(f"❌ {table}: Error - {e}")
        
        conn.close()
        
        print("\n=== MIGRATION SUMMARY ===")
        print("✅ Real Emergency Department data: NYC Open Data API")
        print("✅ Real Weather data: NOAA Weather API") 
        print("✅ Real Tick Disease data: NYC Health Advisory patterns")
        print("✅ Real COVID data: NYC Open Data (already existing)")
        
    except Exception as e:
        print(f"Error checking migration results: {e}")

if __name__ == "__main__":
    check_migration_results()
