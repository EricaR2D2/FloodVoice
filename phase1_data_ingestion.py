import requests
import pandas as pd
import numpy as np
import sqlite3
import os
from datetime import datetime, timedelta

# --- Set up output directory ---
OUTPUT_DIR = r"C:\Users\ricar\PublicHealthMVP"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 1. Fetch NYC Open Data (COVID-19 by ZIP code) ---
# Using a working NYC COVID dataset
NYC_COVID_URL = "https://data.cityofnewyork.us/api/views/rc75-m7u3/rows.csv?accessType=DOWNLOAD"
nyc_csv_path = os.path.join(OUTPUT_DIR, "nyc_covid_data.csv")

try:
    # Download the CSV file
    response = requests.get(NYC_COVID_URL)
    response.raise_for_status()  # Raise an exception for bad status codes

    with open(nyc_csv_path, 'wb') as f:
        f.write(response.content)

    # Load into DataFrame
    nyc_df = pd.read_csv(nyc_csv_path)

    # Print column names to help identify date and ZIP columns
    print("NYC COVID data columns:", nyc_df.columns.tolist())

    # Check if we have valid data (not an error JSON)
    if len(nyc_df.columns) == 1 and '{' in str(nyc_df.columns[0]):
        raise ValueError("Received error response instead of CSV data")

    # Explicitly set date and ZIP columns based on actual column names
    # These will be updated based on what we actually receive
    nyc_date_col = None
    nyc_zip_col = None

    # Try to identify date and ZIP columns automatically
    for col in nyc_df.columns:
        if 'date' in col.lower():
            nyc_date_col = col
        if 'zip' in col.lower() or 'postal' in col.lower():
            nyc_zip_col = col

    print(f"Identified date column: {nyc_date_col}")
    print(f"Identified ZIP column: {nyc_zip_col}")

except Exception as e:
    print(f"Error fetching NYC COVID data: {e}")
    print("Creating mock NYC data for testing...")

    # Create mock NYC COVID data that aligns with hospital data
    dates = pd.date_range(start='2025-05-04', end='2025-06-02', freq='D')
    zip_codes = ['10029', '11432', '10457', '11201', '10455']

    mock_nyc_data = []
    for date in dates:
        for zip_code in zip_codes:
            mock_nyc_data.append({
                'date_of_interest': date.strftime('%Y-%m-%d'),
                'modified_zip': zip_code,
                'covid_case_count': np.random.randint(5, 25),
                'covid_death_count': np.random.randint(0, 3),
                'covid_hospitalized_count': np.random.randint(1, 8)
            })

    nyc_df = pd.DataFrame(mock_nyc_data)
    nyc_df.to_csv(nyc_csv_path, index=False)

    nyc_date_col = "date_of_interest"
    nyc_zip_col = "modified_zip"

    print(f"Created mock NYC data with {len(nyc_df)} records")
    print("NYC COVID data columns:", nyc_df.columns.tolist())

# --- 2. Load and Adjust Mock Hospital Data ---
hospital_csv_path = os.path.join(OUTPUT_DIR, "mock_hospital_data.csv")
if not os.path.exists(hospital_csv_path):
    raise FileNotFoundError(f"Expected mock_hospital_data.csv in {OUTPUT_DIR}. Please place the file there.")
hospital_df = pd.read_csv(hospital_csv_path)

# Get date range from NYC data to align hospital data dates
if nyc_date_col in nyc_df.columns:
    nyc_df[nyc_date_col] = pd.to_datetime(nyc_df[nyc_date_col])
    min_date = nyc_df[nyc_date_col].min()
    max_date = nyc_df[nyc_date_col].max()
    
    # Adjust hospital data dates to match NYC data date range
    hospital_df['date'] = pd.to_datetime(hospital_df['date'])
    date_diff = hospital_df['date'].min() - min_date
    hospital_df['date'] = hospital_df['date'] - date_diff
    
    print(f"Aligned hospital data dates with NYC data: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")

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