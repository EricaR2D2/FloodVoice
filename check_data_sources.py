import sqlite3
import pandas as pd

conn = sqlite3.connect('public_health_data.db')

print('=== DATA SOURCE ANALYSIS ===')

# Check hospital data
print('\n🏥 HOSPITAL DATA:')
hospital_sample = pd.read_sql_query('SELECT * FROM hospital_data LIMIT 5', conn)
print('Sample records:')
print(hospital_sample[['date', 'hospital_name', 'borough', 'zip_code', 'data_source']])

hospital_sources = pd.read_sql_query('SELECT data_source, COUNT(*) as count FROM hospital_data GROUP BY data_source', conn)
print('\nData sources:')
print(hospital_sources)

# Check date ranges
date_range = pd.read_sql_query('SELECT MIN(date) as earliest, MAX(date) as latest FROM hospital_data', conn)
print(f'\nDate range: {date_range.iloc[0]["earliest"]} to {date_range.iloc[0]["latest"]}')

# Check tick disease data
print('\n🦟 TICK DISEASE DATA:')
tick_sample = pd.read_sql_query('SELECT * FROM tick_disease_surveillance LIMIT 5', conn)
print('Sample records:')
print(tick_sample[['report_date', 'zip_code', 'disease_type', 'case_id']])

tick_date_range = pd.read_sql_query('SELECT MIN(report_date) as earliest, MAX(report_date) as latest FROM tick_disease_surveillance', conn)
print(f'Date range: {tick_date_range.iloc[0]["earliest"]} to {tick_date_range.iloc[0]["latest"]}')

# Check weather data
print('\n🌡️ WEATHER DATA:')
weather_sample = pd.read_sql_query('SELECT * FROM weather_data LIMIT 5', conn)
print('Sample records:')
print(weather_sample[['date', 'station_name', 'temp_avg_f', 'tick_risk_score']])

weather_date_range = pd.read_sql_query('SELECT MIN(date) as earliest, MAX(date) as latest FROM weather_data', conn)
print(f'Date range: {weather_date_range.iloc[0]["earliest"]} to {weather_date_range.iloc[0]["latest"]}')

# Check NYC COVID data (real data)
print('\n🦠 NYC COVID DATA:')
covid_sample = pd.read_sql_query('SELECT * FROM nyc_covid_data LIMIT 3', conn)
print('Sample records:')
print(covid_sample[['date_of_interest', 'CASE_COUNT', 'BX_CASE_COUNT', 'BK_CASE_COUNT']])

covid_date_range = pd.read_sql_query('SELECT MIN(date_of_interest) as earliest, MAX(date_of_interest) as latest FROM nyc_covid_data', conn)
print(f'Date range: {covid_date_range.iloc[0]["earliest"]} to {covid_date_range.iloc[0]["latest"]}')

print('\n=== SUMMARY ===')
print('✅ NYC COVID Data: REAL (from NYC Open Data)')
print('❓ Hospital Data: Need to verify source')
print('❓ Tick Disease Data: Need to verify source') 
print('❓ Weather Data: Need to verify source')

conn.close()
