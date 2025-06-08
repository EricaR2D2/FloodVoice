#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('public_health_data.db')
cursor = conn.cursor()

# Count all patterns
cursor.execute('SELECT COUNT(*) FROM pattern_detections')
total_patterns = cursor.fetchone()[0]
print(f'Total patterns: {total_patterns}')

# Count NYC COVID patterns (the new real data)
nyc_hospitals = ['Bronx Medical Center', 'Brooklyn Health Center', 'Manhattan Hospital', 'Queens Medical Center', 'Staten Island Hospital']
placeholders = ','.join(['?' for _ in nyc_hospitals])
cursor.execute(f'SELECT COUNT(*) FROM pattern_detections WHERE hospital_name IN ({placeholders})', nyc_hospitals)
nyc_patterns = cursor.fetchone()[0]
print(f'NYC COVID real patterns: {nyc_patterns}')

# Get sample NYC COVID patterns
cursor.execute(f'''
    SELECT id, hospital_name, zip_code, pattern_type, current_value, percentage_change, date
    FROM pattern_detections
    WHERE hospital_name IN ({placeholders})
    ORDER BY id DESC
    LIMIT 10
''', nyc_hospitals)
patterns = cursor.fetchall()

print('\nSample NYC COVID real patterns:')
for p in patterns:
    print(f'ID: {p[0]}, {p[1]} (ZIP {p[2]}), {p[3]}, Value: {p[4]}, Change: {p[5]:+.1f}%, Date: {p[6]}')

# Check hospital data counts for these hospitals
print('\nHospital data counts for NYC COVID hospitals:')
for hospital in nyc_hospitals:
    cursor.execute('SELECT COUNT(*) FROM hospital_data WHERE hospital_name = ?', (hospital,))
    count = cursor.fetchone()[0]
    print(f'{hospital}: {count} data records')

conn.close()
