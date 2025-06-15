import sqlite3
import pandas as pd

# Test the database queries that the map uses
conn = sqlite3.connect('public_health_data.db')

print('Testing hospital query...')
hospital_query = """
    SELECT zip_code, hospital_name, COUNT(*) as visit_count,
           AVG(CASE WHEN er_visits_respiratory > 0 THEN
               (CAST(er_visits_respiratory AS FLOAT) / CAST(total_er_visits AS FLOAT)) * 100
               ELSE 0 END) as respiratory_pct
    FROM hospital_data
    WHERE date >= date('now', '-30 days')
    GROUP BY zip_code, hospital_name
    ORDER BY visit_count DESC
    LIMIT 20
"""
try:
    hospital_df = pd.read_sql_query(hospital_query, conn)
    print(f'Hospital data: {len(hospital_df)} rows')
    if len(hospital_df) > 0:
        print(hospital_df.head())
    else:
        print('No recent hospital data found')
except Exception as e:
    print(f'Hospital query error: {e}')

print('\nTesting tick query...')
tick_query = """
    SELECT zip_code, COUNT(*) as tick_cases,
           COUNT(CASE WHEN severity = 'Severe' THEN 1 END) as severe_cases
    FROM tick_disease_surveillance
    GROUP BY zip_code
    ORDER BY tick_cases DESC
"""
try:
    tick_df = pd.read_sql_query(tick_query, conn)
    print(f'Tick data: {len(tick_df)} rows')
    if len(tick_df) > 0:
        print(tick_df.head())
    else:
        print('No recent tick data found')
except Exception as e:
    print(f'Tick query error: {e}')

print('\nTesting weather query...')
weather_query = """
    SELECT station_name, AVG(temp_avg_f) as avg_temp,
           AVG(humidity_percent) as avg_humidity,
           AVG(tick_risk_score) as avg_tick_risk
    FROM weather_data
    GROUP BY station_name
"""
try:
    weather_df = pd.read_sql_query(weather_query, conn)
    print(f'Weather data: {len(weather_df)} rows')
    if len(weather_df) > 0:
        print(weather_df.head())
    else:
        print('No recent weather data found')
except Exception as e:
    print(f'Weather query error: {e}')

# Test with broader date ranges
print('\n=== TESTING WITH BROADER DATE RANGES ===')

print('\nTesting tick query (all data)...')
tick_query_all = "SELECT zip_code, COUNT(*) as tick_cases, COUNT(CASE WHEN severity = 'Severe' THEN 1 END) as severe_cases FROM tick_disease_surveillance GROUP BY zip_code"
try:
    tick_df_all = pd.read_sql_query(tick_query_all, conn)
    print(f'All tick data: {len(tick_df_all)} rows')
    if len(tick_df_all) > 0:
        print(tick_df_all.head())
except Exception as e:
    print(f'All tick query error: {e}')

print('\nTesting weather query (all data)...')
weather_query_all = "SELECT station_name, AVG(temp_avg_f) as avg_temp, AVG(humidity_percent) as avg_humidity, AVG(tick_risk_score) as avg_tick_risk FROM weather_data GROUP BY station_name"
try:
    weather_df_all = pd.read_sql_query(weather_query_all, conn)
    print(f'All weather data: {len(weather_df_all)} rows')
    if len(weather_df_all) > 0:
        print(weather_df_all.head())
except Exception as e:
    print(f'All weather query error: {e}')

conn.close()
