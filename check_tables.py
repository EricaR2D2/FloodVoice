import sqlite3

conn = sqlite3.connect('public_health_data.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print('Available tables:')
for table in tables:
    print(f'  - {table[0]}')
    
    # Get column info for each table
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print(f'    Columns: {[col[1] for col in columns]}')
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f'    Rows: {count}')
    print()

conn.close()
