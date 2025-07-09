#!/usr/bin/env python3
"""
COVID-19 Daily Counts Data Ingestion for Public Health MVP
Ingests NYC COVID-19 Daily Counts dataset with borough-level data
"""

import requests
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import json

# Configuration
DATABASE_PATH = 'public_health_data.db'
API_ENDPOINT = 'https://data.cityofnewyork.us/resource/rc75-m7u3.json'

def get_db_connection():
    """Get optimized database connection."""
    conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA cache_size=10000;")
    conn.execute("PRAGMA temp_store=memory;")
    return conn

def create_covid_daily_table():
    """Create table for COVID-19 daily counts data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS covid_daily_counts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_of_interest TEXT NOT NULL,
                case_count INTEGER,
                probable_case_count INTEGER,
                hospitalized_count INTEGER,
                death_count INTEGER,
                case_count_7day_avg REAL,
                all_case_count_7day_avg REAL,
                hosp_count_7day_avg REAL,
                death_count_7day_avg REAL,
                
                -- Borough-specific data
                bx_case_count INTEGER,
                bx_probable_case_count INTEGER,
                bx_hospitalized_count INTEGER,
                bx_death_count INTEGER,
                bx_case_count_7day_avg REAL,
                bx_probable_case_count_7day_avg REAL,
                bx_all_case_count_7day_avg REAL,
                bx_hospitalized_count_7day_avg REAL,
                bx_death_count_7day_avg REAL,
                
                bk_case_count INTEGER,
                bk_probable_case_count INTEGER,
                bk_hospitalized_count INTEGER,
                bk_death_count INTEGER,
                bk_case_count_7day_avg REAL,
                bk_probable_case_count_7day_avg REAL,
                bk_all_case_count_7day_avg REAL,
                bk_hospitalized_count_7day_avg REAL,
                bk_death_count_7day_avg REAL,
                
                mn_case_count INTEGER,
                mn_probable_case_count INTEGER,
                mn_hospitalized_count INTEGER,
                mn_death_count INTEGER,
                mn_case_count_7day_avg REAL,
                mn_probable_case_count_7day_avg REAL,
                mn_all_case_count_7day_avg REAL,
                mn_hospitalized_count_7day_avg REAL,
                mn_death_count_7day_avg REAL,
                
                qn_case_count INTEGER,
                qn_probable_case_count INTEGER,
                qn_hospitalized_count INTEGER,
                qn_death_count INTEGER,
                qn_case_count_7day_avg REAL,
                qn_probable_case_count_7day_avg REAL,
                qn_all_case_count_7day_avg REAL,
                qn_hospitalized_count_7day_avg REAL,
                qn_death_count_7day_avg REAL,
                
                si_case_count INTEGER,
                si_probable_case_count INTEGER,
                si_hospitalized_count INTEGER,
                si_death_count INTEGER,
                si_case_count_7day_avg REAL,
                si_probable_case_count_7day_avg REAL,
                si_all_case_count_7day_avg REAL,
                si_hospitalized_count_7day_avg REAL,
                si_death_count_7day_avg REAL,
                
                incomplete INTEGER,
                data_source TEXT DEFAULT 'NYC Open Data - COVID Daily Counts',
                illness_type TEXT DEFAULT 'COVID-19',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(date_of_interest)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_covid_daily_date ON covid_daily_counts(date_of_interest)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_covid_daily_illness ON covid_daily_counts(illness_type)")
        
        conn.commit()
        print("✅ COVID-19 daily counts table created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False
    finally:
        conn.close()

def fetch_covid_daily_data(limit=50000):
    """Fetch COVID-19 daily counts data from NYC Open Data API."""
    print(f"🔄 Fetching COVID-19 daily counts data (limit: {limit})...")
    
    try:
        # Get data with limit and ordering
        params = {
            '$limit': limit,
            '$order': 'date_of_interest DESC'
        }
        
        response = requests.get(API_ENDPOINT, params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully fetched {len(data)} records")
            return data
        else:
            print(f"❌ API Error: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def process_covid_data(raw_data):
    """Process and clean COVID-19 daily counts data."""
    print("🔄 Processing COVID-19 daily counts data...")

    processed_records = []

    for record in raw_data:
        try:
            # Clean and convert date
            date_str = record.get('date_of_interest', '')
            if date_str:
                # Parse date and format consistently
                date_obj = datetime.strptime(date_str[:10], '%Y-%m-%d')
                clean_date = date_obj.strftime('%Y-%m-%d')
            else:
                continue  # Skip records without date

            # Helper function to safely convert to int
            def safe_int(value):
                try:
                    return int(float(value)) if value and value != '' else 0
                except (ValueError, TypeError):
                    return 0

            # Helper function to safely convert to float
            def safe_float(value):
                try:
                    return float(value) if value and value != '' else 0.0
                except (ValueError, TypeError):
                    return 0.0

            # Process the record
            processed_record = {
                'date_of_interest': clean_date,
                'case_count': safe_int(record.get('case_count')),
                'probable_case_count': safe_int(record.get('probable_case_count')),
                'hospitalized_count': safe_int(record.get('hospitalized_count')),
                'death_count': safe_int(record.get('death_count')),
                'case_count_7day_avg': safe_float(record.get('case_count_7day_avg')),
                'all_case_count_7day_avg': safe_float(record.get('all_case_count_7day_avg')),
                'hosp_count_7day_avg': safe_float(record.get('hosp_count_7day_avg')),
                'death_count_7day_avg': safe_float(record.get('death_count_7day_avg')),

                # Bronx data
                'bx_case_count': safe_int(record.get('bx_case_count')),
                'bx_probable_case_count': safe_int(record.get('bx_probable_case_count')),
                'bx_hospitalized_count': safe_int(record.get('bx_hospitalized_count')),
                'bx_death_count': safe_int(record.get('bx_death_count')),
                'bx_case_count_7day_avg': safe_float(record.get('bx_case_count_7day_avg')),
                'bx_probable_case_count_7day_avg': safe_float(record.get('bx_probable_case_count_7day_avg')),
                'bx_all_case_count_7day_avg': safe_float(record.get('bx_all_case_count_7day_avg')),
                'bx_hospitalized_count_7day_avg': safe_float(record.get('bx_hospitalized_count_7day_avg')),
                'bx_death_count_7day_avg': safe_float(record.get('bx_death_count_7day_avg')),

                # Brooklyn data
                'bk_case_count': safe_int(record.get('bk_case_count')),
                'bk_probable_case_count': safe_int(record.get('bk_probable_case_count')),
                'bk_hospitalized_count': safe_int(record.get('bk_hospitalized_count')),
                'bk_death_count': safe_int(record.get('bk_death_count')),
                'bk_case_count_7day_avg': safe_float(record.get('bk_case_count_7day_avg')),
                'bk_probable_case_count_7day_avg': safe_float(record.get('bk_probable_case_count_7day_avg')),
                'bk_all_case_count_7day_avg': safe_float(record.get('bk_all_case_count_7day_avg')),
                'bk_hospitalized_count_7day_avg': safe_float(record.get('bk_hospitalized_count_7day_avg')),
                'bk_death_count_7day_avg': safe_float(record.get('bk_death_count_7day_avg')),

                # Manhattan data
                'mn_case_count': safe_int(record.get('mn_case_count')),
                'mn_probable_case_count': safe_int(record.get('mn_probable_case_count')),
                'mn_hospitalized_count': safe_int(record.get('mn_hospitalized_count')),
                'mn_death_count': safe_int(record.get('mn_death_count')),
                'mn_case_count_7day_avg': safe_float(record.get('mn_case_count_7day_avg')),
                'mn_probable_case_count_7day_avg': safe_float(record.get('mn_probable_case_count_7day_avg')),
                'mn_all_case_count_7day_avg': safe_float(record.get('mn_all_case_count_7day_avg')),
                'mn_hospitalized_count_7day_avg': safe_float(record.get('mn_hospitalized_count_7day_avg')),
                'mn_death_count_7day_avg': safe_float(record.get('mn_death_count_7day_avg')),

                # Queens data
                'qn_case_count': safe_int(record.get('qn_case_count')),
                'qn_probable_case_count': safe_int(record.get('qn_probable_case_count')),
                'qn_hospitalized_count': safe_int(record.get('qn_hospitalized_count')),
                'qn_death_count': safe_int(record.get('qn_death_count')),
                'qn_case_count_7day_avg': safe_float(record.get('qn_case_count_7day_avg')),
                'qn_probable_case_count_7day_avg': safe_float(record.get('qn_probable_case_count_7day_avg')),
                'qn_all_case_count_7day_avg': safe_float(record.get('qn_all_case_count_7day_avg')),
                'qn_hospitalized_count_7day_avg': safe_float(record.get('qn_hospitalized_count_7day_avg')),
                'qn_death_count_7day_avg': safe_float(record.get('qn_death_count_7day_avg')),

                # Staten Island data
                'si_case_count': safe_int(record.get('si_case_count')),
                'si_probable_case_count': safe_int(record.get('si_probable_case_count')),
                'si_hospitalized_count': safe_int(record.get('si_hospitalized_count')),
                'si_death_count': safe_int(record.get('si_death_count')),
                'si_case_count_7day_avg': safe_float(record.get('si_case_count_7day_avg')),
                'si_probable_case_count_7day_avg': safe_float(record.get('si_probable_case_count_7day_avg')),
                'si_all_case_count_7day_avg': safe_float(record.get('si_all_case_count_7day_avg')),
                'si_hospitalized_count_7day_avg': safe_float(record.get('si_hospitalized_count_7day_avg')),
                'si_death_count_7day_avg': safe_float(record.get('si_death_count_7day_avg')),

                'incomplete': safe_int(record.get('incomplete')),
                'data_source': 'NYC Open Data - COVID Daily Counts',
                'illness_type': 'COVID-19',
                'created_at': datetime.now().isoformat()
            }

            processed_records.append(processed_record)

        except Exception as e:
            print(f"⚠️ Error processing record: {e}")
            continue

    print(f"✅ Processed {len(processed_records)} COVID-19 daily records")
    return processed_records

def save_covid_data_to_db(processed_data):
    """Save processed COVID-19 data to database."""
    print("🔄 Saving COVID-19 daily counts to database...")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Prepare insert statement
        insert_sql = """
            INSERT OR REPLACE INTO covid_daily_counts (
                date_of_interest, case_count, probable_case_count, hospitalized_count, death_count,
                case_count_7day_avg, all_case_count_7day_avg, hosp_count_7day_avg, death_count_7day_avg,
                bx_case_count, bx_probable_case_count, bx_hospitalized_count, bx_death_count,
                bx_case_count_7day_avg, bx_probable_case_count_7day_avg, bx_all_case_count_7day_avg,
                bx_hospitalized_count_7day_avg, bx_death_count_7day_avg,
                bk_case_count, bk_probable_case_count, bk_hospitalized_count, bk_death_count,
                bk_case_count_7day_avg, bk_probable_case_count_7day_avg, bk_all_case_count_7day_avg,
                bk_hospitalized_count_7day_avg, bk_death_count_7day_avg,
                mn_case_count, mn_probable_case_count, mn_hospitalized_count, mn_death_count,
                mn_case_count_7day_avg, mn_probable_case_count_7day_avg, mn_all_case_count_7day_avg,
                mn_hospitalized_count_7day_avg, mn_death_count_7day_avg,
                qn_case_count, qn_probable_case_count, qn_hospitalized_count, qn_death_count,
                qn_case_count_7day_avg, qn_probable_case_count_7day_avg, qn_all_case_count_7day_avg,
                qn_hospitalized_count_7day_avg, qn_death_count_7day_avg,
                si_case_count, si_probable_case_count, si_hospitalized_count, si_death_count,
                si_case_count_7day_avg, si_probable_case_count_7day_avg, si_all_case_count_7day_avg,
                si_hospitalized_count_7day_avg, si_death_count_7day_avg,
                incomplete, data_source, illness_type, created_at
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """

        # Insert data in batches
        batch_size = 1000
        inserted_count = 0

        for i in range(0, len(processed_data), batch_size):
            batch = processed_data[i:i + batch_size]

            batch_values = []
            for record in batch:
                values = (
                    record['date_of_interest'], record['case_count'], record['probable_case_count'],
                    record['hospitalized_count'], record['death_count'], record['case_count_7day_avg'],
                    record['all_case_count_7day_avg'], record['hosp_count_7day_avg'], record['death_count_7day_avg'],
                    record['bx_case_count'], record['bx_probable_case_count'], record['bx_hospitalized_count'],
                    record['bx_death_count'], record['bx_case_count_7day_avg'], record['bx_probable_case_count_7day_avg'],
                    record['bx_all_case_count_7day_avg'], record['bx_hospitalized_count_7day_avg'], record['bx_death_count_7day_avg'],
                    record['bk_case_count'], record['bk_probable_case_count'], record['bk_hospitalized_count'],
                    record['bk_death_count'], record['bk_case_count_7day_avg'], record['bk_probable_case_count_7day_avg'],
                    record['bk_all_case_count_7day_avg'], record['bk_hospitalized_count_7day_avg'], record['bk_death_count_7day_avg'],
                    record['mn_case_count'], record['mn_probable_case_count'], record['mn_hospitalized_count'],
                    record['mn_death_count'], record['mn_case_count_7day_avg'], record['mn_probable_case_count_7day_avg'],
                    record['mn_all_case_count_7day_avg'], record['mn_hospitalized_count_7day_avg'], record['mn_death_count_7day_avg'],
                    record['qn_case_count'], record['qn_probable_case_count'], record['qn_hospitalized_count'],
                    record['qn_death_count'], record['qn_case_count_7day_avg'], record['qn_probable_case_count_7day_avg'],
                    record['qn_all_case_count_7day_avg'], record['qn_hospitalized_count_7day_avg'], record['qn_death_count_7day_avg'],
                    record['si_case_count'], record['si_probable_case_count'], record['si_hospitalized_count'],
                    record['si_death_count'], record['si_case_count_7day_avg'], record['si_probable_case_count_7day_avg'],
                    record['si_all_case_count_7day_avg'], record['si_hospitalized_count_7day_avg'], record['si_death_count_7day_avg'],
                    record['incomplete'], record['data_source'], record['illness_type'], record['created_at']
                )
                batch_values.append(values)

            cursor.executemany(insert_sql, batch_values)
            inserted_count += len(batch)
            print(f"  Inserted batch: {inserted_count}/{len(processed_data)} records")

        conn.commit()
        print(f"✅ Successfully saved {inserted_count} COVID-19 daily records to database")
        return True

    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Main function to run COVID-19 daily counts ingestion."""
    print("🚀 Starting COVID-19 Daily Counts Data Ingestion")
    print("=" * 60)

    # Step 1: Create table
    if not create_covid_daily_table():
        print("❌ Failed to create table. Exiting.")
        return False

    # Step 2: Fetch data
    raw_data = fetch_covid_daily_data()
    if not raw_data:
        print("❌ Failed to fetch data. Exiting.")
        return False

    # Step 3: Process data
    processed_data = process_covid_data(raw_data)
    if not processed_data:
        print("❌ No data to process. Exiting.")
        return False

    # Step 4: Save to database
    if not save_covid_data_to_db(processed_data):
        print("❌ Failed to save data. Exiting.")
        return False

    print("\n🎉 COVID-19 Daily Counts ingestion completed successfully!")
    print(f"📊 Total records processed: {len(processed_data)}")

    # Show sample of what was ingested
    if processed_data:
        print("\n📋 Sample record:")
        sample = processed_data[0]
        print(f"  Date: {sample['date_of_interest']}")
        print(f"  Total Cases: {sample['case_count']}")
        print(f"  Total Hospitalizations: {sample['hospitalized_count']}")
        print(f"  Bronx Cases: {sample['bx_case_count']}")
        print(f"  Brooklyn Cases: {sample['bk_case_count']}")
        print(f"  Manhattan Cases: {sample['mn_case_count']}")
        print(f"  Queens Cases: {sample['qn_case_count']}")
        print(f"  Staten Island Cases: {sample['si_case_count']}")

    return True

if __name__ == "__main__":
    main()
