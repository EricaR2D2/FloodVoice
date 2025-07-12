#!/usr/bin/env python3
"""
Check NYC COVID data date format to fix parsing error
"""

import sqlite3
import pandas as pd

def check_covid_date_format():
    """Check the date format in nyc_covid_data table."""
    
    conn = sqlite3.connect('public_health_data.db')
    
    print('=== NYC COVID DATA DATE FORMAT ===')
    try:
        # Get sample dates from nyc_covid_data
        sample = pd.read_sql_query('SELECT date_of_interest FROM nyc_covid_data LIMIT 5', conn)
        print('Sample dates from nyc_covid_data:')
        for _, row in sample.iterrows():
            date_val = row['date_of_interest']
            print(f'  {repr(date_val)} (type: {type(date_val)}, length: {len(str(date_val))})')
        
        # Get the latest date
        latest = pd.read_sql_query('SELECT MAX(date_of_interest) as latest_date FROM nyc_covid_data', conn)
        latest_date = latest.iloc[0]['latest_date']
        print(f'\nLatest date: {repr(latest_date)}')
        print(f'Type: {type(latest_date)}')
        print(f'Length: {len(str(latest_date))}')
        
        # Test different parsing approaches
        print(f'\nTesting parsing approaches:')
        date_str = str(latest_date)
        
        print(f'1. Original string: {repr(date_str)}')
        print(f'2. Split by space: {date_str.split(" ")}')
        print(f'3. First 10 chars: {repr(date_str[:10])}')
        
        # Test if it contains time
        if ' ' in date_str:
            print(f'4. Contains space - likely has time component')
            date_part = date_str.split(' ')[0]
            print(f'5. Date part only: {repr(date_part)}')
        else:
            print(f'4. No space - date only')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
    
    conn.close()

if __name__ == "__main__":
    check_covid_date_format()
