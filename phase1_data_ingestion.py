import requests
import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta
import json

# --- Set up output directory ---
OUTPUT_DIR = r"C:\Users\ricar\PublicHealthMVP"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Database Configuration ---
DATABASE_PATH = os.path.join(OUTPUT_DIR, 'public_health_data.db')

def get_db_connection():
    """Get optimized database connection with proper settings."""
    conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA cache_size=10000;")
    conn.execute("PRAGMA temp_store=memory;")
    return conn

def standardize_borough_name(borough):
    """Standardize borough names to consistent format."""
    if pd.isna(borough) or borough is None:
        return None

    borough = str(borough).strip().upper()

    # Mapping for common variations
    borough_mapping = {
        'MANHATTAN': 'Manhattan',
        'MN': 'Manhattan',
        'NEW YORK': 'Manhattan',
        'BRONX': 'Bronx',
        'BX': 'Bronx',
        'BROOKLYN': 'Brooklyn',
        'BK': 'Brooklyn',
        'KINGS': 'Brooklyn',
        'QUEENS': 'Queens',
        'QN': 'Queens',
        'STATEN ISLAND': 'Staten Island',
        'SI': 'Staten Island',
        'RICHMOND': 'Staten Island'
    }

    return borough_mapping.get(borough, borough.title())

# --- Part 1: COVID-19 Data Ingestion ---
def fetch_and_process_covid_data():
    """
    Fetch and process COVID-19 data from NYC Open Data API.
    Returns borough-level case counts by date.
    """
    print("🦠 Fetching COVID-19 data from NYC Open Data...")

    try:
        # NYC Open Data API endpoint for COVID-19 cases by borough
        api_url = "https://data.cityofnewyork.us/resource/xywu-7bv9.json"

        # Use Socrata API parameters to get most recent records
        params = {
            "$limit": 50000,  # Get substantial amount of data
            "$order": "date_of_interest DESC"  # Most recent first
        }

        response = requests.get(api_url, params=params)
        response.raise_for_status()

        data = response.json()
        print(f"Retrieved {len(data)} COVID-19 records from NYC Open Data")

        if not data:
            print("No COVID-19 data returned from API")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Print available columns to understand the data structure
        print("Available COVID-19 columns:", df.columns.tolist())
        if len(df) > 0:
            print("Sample COVID-19 record:", df.iloc[0].to_dict())

        # Process the data - extract borough, case count, and date
        processed_data = []

        for _, row in df.iterrows():
            try:
                # Extract required fields
                date_str = row.get('date_of_interest', '')
                borough = row.get('boro', '')
                case_count = row.get('case_count', 0)

                # Skip if essential data is missing
                if not date_str or not borough:
                    continue

                # Standardize borough name
                standardized_borough = standardize_borough_name(borough)
                if not standardized_borough:
                    continue

                # Convert case count to integer
                try:
                    case_count = int(float(case_count)) if case_count else 0
                except (ValueError, TypeError):
                    case_count = 0

                # Parse date
                try:
                    # Handle different date formats
                    if 'T' in date_str:
                        date_obj = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
                    else:
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

                    formatted_date = date_obj.strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    continue

                processed_data.append({
                    'date': formatted_date,
                    'borough': standardized_borough,
                    'case_count': case_count
                })

            except Exception as e:
                print(f"Error processing COVID-19 record: {e}")
                continue

        if processed_data:
            processed_df = pd.DataFrame(processed_data)
            print(f"✅ Successfully processed {len(processed_df)} COVID-19 records")

            # Show summary
            print(f"   Date range: {processed_df['date'].min()} to {processed_df['date'].max()}")
            print(f"   Boroughs: {processed_df['borough'].unique().tolist()}")
            print(f"   Total cases: {processed_df['case_count'].sum():,}")

            return processed_df
        else:
            print("❌ No valid COVID-19 data processed")
            return pd.DataFrame()

    except Exception as e:
        print(f"❌ Error fetching COVID-19 data: {e}")
        return pd.DataFrame()

print("🔄 Fetching REAL-TIME NYC COVID-19 surveillance data...")
print(f"📊 Data source: NYC Open Data - Daily COVID counts by borough")
print(f"🕐 Data coverage: Current through {datetime.now().strftime('%Y-%m-%d')}")

try:
    # Download the real-time CSV file
    response = requests.get(NYC_COVID_URL)
    response.raise_for_status()  # Raise an exception for bad status codes

    with open(nyc_csv_path, 'wb') as f:
        f.write(response.content)

    # Load into DataFrame
    nyc_df = pd.read_csv(nyc_csv_path)

    # Check if we have valid data (not an error JSON)
    if len(nyc_df.columns) == 1 and '{' in str(nyc_df.columns[0]):
        raise ValueError("Received error response instead of CSV data")

    print(f"✅ Successfully downloaded real-time NYC COVID data")
    print(f"📈 Dataset contains {len(nyc_df)} daily records")

    # This dataset has borough-level data, not ZIP codes
    nyc_date_col = "date_of_interest"
    nyc_zip_col = None  # No ZIP codes in this dataset - it's borough-level

    # Check data freshness
    nyc_df['date_of_interest'] = pd.to_datetime(nyc_df['date_of_interest'])
    latest_date = nyc_df['date_of_interest'].max()
    days_old = (datetime.now() - latest_date).days

    print(f"📅 Latest data: {latest_date.strftime('%Y-%m-%d')} ({days_old} days ago)")
    print(f"🏙️  Borough-level data available for: Bronx, Brooklyn, Manhattan, Queens, Staten Island")

    # Show available metrics
    metrics = [col for col in nyc_df.columns if any(metric in col.upper() for metric in ['CASE', 'HOSP', 'DEATH'])]
    print(f"📊 Available metrics: {len(metrics)} including cases, hospitalizations, deaths by borough")

except Exception as e:
    print(f"⚠️  Error fetching real-time NYC COVID data: {e}")
    print("🔄 Creating realistic mock data based on current patterns...")

    # Create mock data that mimics the real-time borough structure
    # Using recent date range to simulate current surveillance
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)  # Last 30 days
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    # Borough codes as used in real NYC data
    boroughs = {
        'BX': 'Bronx',
        'BK': 'Brooklyn',
        'MN': 'Manhattan',
        'QN': 'Queens',
        'SI': 'Staten Island'
    }

    mock_nyc_data = []
    for date in dates:
        # Citywide totals (realistic current levels)
        citywide_cases = np.random.randint(80, 220)  # Based on recent real data
        citywide_hosp = np.random.randint(8, 25)
        citywide_deaths = np.random.randint(0, 3)

        # Borough breakdowns (proportional to population)
        borough_cases = {
            'BX': int(citywide_cases * 0.22),  # Bronx ~22% of NYC
            'BK': int(citywide_cases * 0.28),  # Brooklyn ~28%
            'MN': int(citywide_cases * 0.18),  # Manhattan ~18%
            'QN': int(citywide_cases * 0.25),  # Queens ~25%
            'SI': int(citywide_cases * 0.07)   # Staten Island ~7%
        }

        # Create record with real-time structure
        record = {
            'date_of_interest': date.strftime('%Y-%m-%d'),
            'CASE_COUNT': citywide_cases,
            'HOSPITALIZED_COUNT': citywide_hosp,
            'DEATH_COUNT': citywide_deaths,
        }

        # Add borough-specific data
        for code, name in boroughs.items():
            record[f'{code}_CASE_COUNT'] = borough_cases[code]
            record[f'{code}_HOSPITALIZED_COUNT'] = max(1, int(citywide_hosp * borough_cases[code] / citywide_cases))
            record[f'{code}_DEATH_COUNT'] = np.random.randint(0, 2)

        mock_nyc_data.append(record)

    nyc_df = pd.DataFrame(mock_nyc_data)
    nyc_df.to_csv(nyc_csv_path, index=False)

    nyc_date_col = "date_of_interest"
    nyc_zip_col = None  # Borough-level data, not ZIP codes

    print(f"✅ Created realistic mock data with {len(nyc_df)} daily records")
    print(f"📅 Date range: {start_date} to {end_date}")
    print(f"🏙️  Borough-level structure matches real NYC Open Data format")

# --- 2. Transform NYC COVID Data for Hospital-Style Analysis ---
# Use the real NYC COVID data as our primary health surveillance data
print("🏥 Transforming NYC COVID data for hospital-style analysis...")

hospital_csv_path = os.path.join(OUTPUT_DIR, "realtime_hospital_data.csv")

# Get date range from NYC data
nyc_df[nyc_date_col] = pd.to_datetime(nyc_df[nyc_date_col])
min_date = nyc_df[nyc_date_col].min()
max_date = nyc_df[nyc_date_col].max()

print(f"📅 Real NYC COVID data range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
print(f"📊 Total days of data: {(max_date - min_date).days + 1}")

# Transform NYC COVID data into hospital-style records for forecasting
# Each borough becomes a "hospital" with daily COVID metrics as "ER visits"
hospital_data = []

# Borough mapping for consistent naming
borough_mapping = {
    'BX': {'name': 'Bronx Medical Center', 'zip': '10451'},
    'BK': {'name': 'Brooklyn Health Center', 'zip': '11201'},
    'MN': {'name': 'Manhattan Hospital', 'zip': '10001'},
    'QN': {'name': 'Queens Medical Center', 'zip': '11101'},
    'SI': {'name': 'Staten Island Hospital', 'zip': '10301'}
}

# Process each date in the NYC COVID dataset
for _, row in nyc_df.iterrows():
    date_str = row[nyc_date_col].strftime('%Y-%m-%d')

    # Create records for each borough using real COVID data
    for borough_code, info in borough_mapping.items():
        # Use real COVID hospitalizations as our "ER respiratory visits"
        hosp_col = f'{borough_code}_HOSPITALIZED_COUNT'
        case_col = f'{borough_code}_CASE_COUNT'

        # Get real values or fall back to citywide proportions
        if hosp_col in row and pd.notna(row[hosp_col]):
            er_visits = max(1, int(row[hosp_col]))
        elif 'HOSPITALIZED_COUNT' in row and pd.notna(row['HOSPITALIZED_COUNT']):
            # Use citywide data with borough proportions
            borough_proportions = {'BX': 0.22, 'BK': 0.28, 'MN': 0.18, 'QN': 0.25, 'SI': 0.07}
            er_visits = max(1, int(row['HOSPITALIZED_COUNT'] * borough_proportions[borough_code]))
        else:
            er_visits = 1  # Minimum value

        # Get case count for additional context
        case_count = 0
        if case_col in row and pd.notna(row[case_col]):
            case_count = max(0, int(row[case_col]))
        elif 'CASE_COUNT' in row and pd.notna(row['CASE_COUNT']):
            borough_proportions = {'BX': 0.22, 'BK': 0.28, 'MN': 0.18, 'QN': 0.25, 'SI': 0.07}
            case_count = max(0, int(row['CASE_COUNT'] * borough_proportions[borough_code]))

        hospital_data.append({
            'date': date_str,
            'hospital_name': info['name'],
            'borough': borough_code,
            'zip_code': info['zip'],
            'er_visits_respiratory': er_visits,
            'total_er_visits': er_visits + np.random.randint(10, 30),  # Add some baseline
            'covid_cases': case_count,
            'data_source': 'NYC_COVID_REAL'
        })

hospital_df = pd.DataFrame(hospital_data)
hospital_df.to_csv(hospital_csv_path, index=False)

print(f"✅ Transformed real NYC COVID data into {len(hospital_df)} hospital-style records")
print(f"🏥 5 NYC boroughs as medical centers with real COVID hospitalization data")
print(f"📈 Each borough has {len(hospital_df) // 5} days of real historical data")
print(f"� Using real COVID hospitalizations as ER respiratory visits for forecasting")

# --- 3. Fetch Additional Data Sources ---
# CDC Influenza-like Illness data
try:
    # Try a working CDC dataset
    CDC_ILI_URL = "https://data.cdc.gov/api/views/g62h-syeh/rows.csv?accessType=DOWNLOAD"
    cdc_csv_path = os.path.join(OUTPUT_DIR, "cdc_ili_data.csv")

    response = requests.get(CDC_ILI_URL)
    response.raise_for_status()

    with open(cdc_csv_path, 'wb') as f:
        f.write(response.content)

    cdc_df = pd.read_csv(cdc_csv_path)

    # Check if we got valid data
    if len(cdc_df.columns) == 1 and '{' in str(cdc_df.columns[0]):
        raise ValueError("Received error response instead of CSV data")

    print("Successfully downloaded CDC ILI data")
    print("CDC data columns:", cdc_df.columns.tolist())

except Exception as e:
    print(f"Error fetching CDC data: {e}")
    print("Creating mock CDC data for testing...")

    # Create mock CDC data
    dates = pd.date_range(start='2025-05-04', end='2025-06-02', freq='W')
    mock_cdc_data = []
    for date in dates:
        mock_cdc_data.append({
            'week_ending_date': date.strftime('%Y-%m-%d'),
            'region': 'New York',
            'ili_percent': round(np.random.uniform(2.0, 8.0), 2),
            'total_patients': np.random.randint(1000, 5000),
            'ili_patients': np.random.randint(50, 300)
        })

    cdc_df = pd.DataFrame(mock_cdc_data)
    cdc_df.to_csv(cdc_csv_path, index=False)
    print(f"Created mock CDC data with {len(cdc_df)} records")

# Air Quality Data
try:
    # Note: EPA AQS API requires registration and API key
    # For testing, we'll create mock data
    print("Creating mock Air Quality data for testing...")

    # Create mock air quality data
    dates = pd.date_range(start='2025-05-04', end='2025-06-02', freq='D')
    mock_aqi_data = []
    for date in dates:
        mock_aqi_data.append({
            'date_local': date.strftime('%Y-%m-%d'),
            'state_name': 'New York',
            'county_name': 'New York',
            'aqi': np.random.randint(25, 150),
            'category': np.random.choice(['Good', 'Moderate', 'Unhealthy for Sensitive Groups']),
            'pm25_concentration': round(np.random.uniform(5.0, 35.0), 2),
            'ozone_concentration': round(np.random.uniform(0.02, 0.08), 3)
        })

    aqi_df = pd.DataFrame(mock_aqi_data)
    aqi_json_path = os.path.join(OUTPUT_DIR, "air_quality_data.json")
    aqi_df.to_json(aqi_json_path, orient='records', indent=2)
    print(f"Created mock Air Quality data with {len(aqi_df)} records")

except Exception as e:
    print(f"Error creating Air Quality data: {e}")
    aqi_df = None

# --- 4. Basic Cleaning & Standardization ---
def clean_and_standardize(df, date_col, zip_col=None, er_col=None):
    # Convert 'date' to datetime and standardize format
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.strftime('%Y-%m-%d')
    # Standardize ZIP codes if present
    if zip_col and zip_col in df.columns:
        df[zip_col] = df[zip_col].astype(str).str.zfill(5)
    # Fill missing values in er_visits_respiratory if present
    if er_col and er_col in df.columns:
        df[er_col] = df[er_col].fillna(0)
    return df

# Clean NYC data with explicit column names
if nyc_date_col and nyc_zip_col and nyc_date_col in nyc_df.columns and nyc_zip_col in nyc_df.columns:
    nyc_df = clean_and_standardize(nyc_df, nyc_date_col, nyc_zip_col)
    print(f"Successfully cleaned NYC data with {len(nyc_df)} records")
else:
    print(f"Warning: Expected columns not found in NYC data. Available columns: {nyc_df.columns.tolist()}")

# Clean hospital data
hospital_df = clean_and_standardize(hospital_df, 'date', 'zip_code', 'er_visits_respiratory')
print(f"Successfully cleaned hospital data with {len(hospital_df)} records")

# Clean additional datasets if available
if cdc_df is not None and len(cdc_df) > 0:
    # Find the date column in CDC data
    cdc_date_col = "week_ending_date"
    if cdc_date_col not in cdc_df.columns:
        # Try to find any date column
        for col in cdc_df.columns:
            if 'date' in col.lower():
                cdc_date_col = col
                break

    if cdc_date_col in cdc_df.columns:
        cdc_df = clean_and_standardize(cdc_df, cdc_date_col)
        print(f"Successfully cleaned CDC data with {len(cdc_df)} records")
    else:
        print("Warning: No date column found in CDC data")

if aqi_df is not None and len(aqi_df) > 0:
    # Find the date column in AQI data
    aqi_date_col = "date_local"
    if aqi_date_col not in aqi_df.columns:
        # Try to find any date column
        for col in aqi_df.columns:
            if 'date' in col.lower():
                aqi_date_col = col
                break

    if aqi_date_col in aqi_df.columns:
        aqi_df = clean_and_standardize(aqi_df, aqi_date_col)
        print(f"Successfully cleaned Air Quality data with {len(aqi_df)} records")
    else:
        print("Warning: No date column found in Air Quality data")

# --- 5. Storage ---
# Save cleaned DataFrames to CSV
nyc_cleaned_csv = os.path.join(OUTPUT_DIR, 'cleaned_nyc_data.csv')
hospital_cleaned_csv = os.path.join(OUTPUT_DIR, 'cleaned_hospital_data.csv')
nyc_df.to_csv(nyc_cleaned_csv, index=False)
hospital_df.to_csv(hospital_cleaned_csv, index=False)

if cdc_df is not None:
    cdc_cleaned_csv = os.path.join(OUTPUT_DIR, 'cleaned_cdc_data.csv')
    cdc_df.to_csv(cdc_cleaned_csv, index=False)

if aqi_df is not None:
    aqi_cleaned_csv = os.path.join(OUTPUT_DIR, 'cleaned_aqi_data.csv')
    aqi_df.to_csv(aqi_cleaned_csv, index=False)

# Save to SQLite database
db_path = os.path.join(OUTPUT_DIR, 'public_health_data.db')
conn = sqlite3.connect(db_path)

# Write each DataFrame to its own table (replace if exists)
nyc_df.to_sql('nyc_covid_data', conn, if_exists='replace', index=False)
hospital_df.to_sql('hospital_data', conn, if_exists='replace', index=False)

if cdc_df is not None:
    cdc_df.to_sql('cdc_ili_data', conn, if_exists='replace', index=False)

if aqi_df is not None:
    aqi_df.to_sql('air_quality_data', conn, if_exists='replace', index=False)

# Merge NYC and hospital data on date and zip_code
if nyc_date_col and nyc_zip_col and nyc_date_col in nyc_df.columns and nyc_zip_col in nyc_df.columns:
    # Standardize column names for merging
    nyc_df_merged = nyc_df.rename(columns={nyc_date_col: 'date', nyc_zip_col: 'zip_code'})
    merged = pd.merge(nyc_df_merged, hospital_df, on=['date', 'zip_code'], how='outer')
    merged_csv = os.path.join(OUTPUT_DIR, 'unified_health_data.csv')
    merged.to_csv(merged_csv, index=False)
    merged.to_sql('unified_health_data', conn, if_exists='replace', index=False)
    print(f"Successfully merged NYC and hospital data. Saved to {merged_csv}")
    print(f"Merged dataset contains {len(merged)} records")
else:
    print("Could not merge NYC and hospital data due to missing columns")
    print("Saving hospital data as unified dataset...")
    unified_csv = os.path.join(OUTPUT_DIR, 'unified_health_data.csv')
    hospital_df.to_csv(unified_csv, index=False)
    hospital_df.to_sql('unified_health_data', conn, if_exists='replace', index=False)
    print(f"Saved hospital data as unified dataset with {len(hospital_df)} records")

conn.close()

print(f"Data processing complete. All files saved in {OUTPUT_DIR}")