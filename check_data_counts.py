#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('public_health_data.db')
cursor = conn.cursor()

# Check hospital data counts
cursor.execute('SELECT COUNT(*) FROM hospital_data WHERE hospital_name NOT LIKE "Test%"')
real_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM hospital_data WHERE hospital_name LIKE "Test%"')
test_count = cursor.fetchone()[0]

print(f'Real hospital records: {real_count}')
print(f'Test hospital records: {test_count}')

# Check pattern counts
cursor.execute('SELECT COUNT(*) FROM pattern_detections WHERE hospital_name NOT LIKE "Test%"')
real_patterns = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM pattern_detections WHERE hospital_name LIKE "Test%"')
test_patterns = cursor.fetchone()[0]

print(f'Real hospital patterns: {real_patterns}')
print(f'Test hospital patterns: {test_patterns}')

conn.close()
