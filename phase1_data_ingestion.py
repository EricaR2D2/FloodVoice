import requests
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta

# --- Set up output directory ---
OUTPUT_DIR = r"C:\Users\ricar\PublicHealthMVP"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 1. Fetch NYC Open Data (COVID-19 by ZIP code) ---
NYC_COVID_URL = "https://data.cityofnewyork.us/api/views/xdss-u53e/rows.csv?accessType=DOWNLOAD"
nyc_csv_path = os.path.join(OUTPUT_DIR, "nyc_covid_data.csv")

# Download the CSV file
response = requests.get(NYC_COVID_URL)
with open(nyc_csv_path, 'wb') as f:
    f.write(response.content)

# Load into DataFrame
nyc_df = pd.read_csv(nyc_csv_path)

# Print column names to help identify date and ZIP columns
print("NYC COVID data columns:", nyc_df.columns.tolist())

# Explicitly set date and ZIP columns based on actual column names
# Replace these with the actual column names from your dataset
nyc_date_col = "date_of_interest"  # Update this with the actual date column name
nyc_zip_col = "modified_zip"       # Update this with the actual ZIP column name

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
# CDC Influenza-like Illness data (example URL - replace with actual API endpoint)
try:
    CDC_ILI_URL = "https://data.cdc.gov/api/views/x32p-8y75/rows.csv?accessType=DOWNLOAD"
    cdc_csv_path = os.path.join(OUTPUT_DIR, "cdc_ili_data.csv")
    
    response = requests.get(CDC_ILI_URL)
    with open(cdc_csv_path, 'wb') as f:
        f.write(response.content)
    
    cdc_df = pd.read_csv(cdc_csv_path)
    print("Successfully downloaded CDC ILI data")
except Exception as e:
    print(f"Error fetching CDC data: {e}")
    cdc_df = None

# Air Quality Data (example - replace with actual API endpoint)
try:
    AQI_URL = "https://aqs.epa.gov/data/api/dailyData/byState?email=your-email@example.com&key=your-api-key&param=44201&bdate=20200101&edate=20201231&state=36"
    aqi_json_path = os.path.join(OUTPUT_DIR, "air_quality_data.json")
    
    response = requests.get(AQI_URL)
    with open(aqi_json_path, 'wb') as f:
        f.write(response.content)
    
    # Note: This might need adjustment based on the actual API response format
    aqi_df = pd.read_json(aqi_json_path)
    print("Successfully downloaded Air Quality data")
except Exception as e:
    print(f"Error fetching Air Quality data: {e}")
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
if nyc_date_col in nyc_df.columns and nyc_zip_col in nyc_df.columns:
    nyc_df = clean_and_standardize(nyc_df, nyc_date_col, nyc_zip_col)
else:
    print(f"Warning: Expected columns not found in NYC data. Available columns: {nyc_df.columns.tolist()}")

# Clean hospital data
hospital_df = clean_and_standardize(hospital_df, 'date', 'zip_code', 'er_visits_respiratory')

# Clean additional datasets if available
if cdc_df is not None:
    # Adjust column names based on actual CDC data
    cdc_date_col = "week_ending_date"  # Update with actual column name
    cdc_df = clean_and_standardize(cdc_df, cdc_date_col)

if aqi_df is not None:
    # Adjust column names based on actual AQI data
    aqi_date_col = "date_local"  # Update with actual column name
    aqi_df = clean_and_standardize(aqi_df, aqi_date_col)

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
if nyc_date_col in nyc_df.columns and nyc_zip_col in nyc_df.columns:
    # Standardize column names for merging
    nyc_df_merged = nyc_df.rename(columns={nyc_date_col: 'date', nyc_zip_col: 'zip_code'})
    merged = pd.merge(nyc_df_merged, hospital_df, on=['date', 'zip_code'], how='outer')
    merged_csv = os.path.join(OUTPUT_DIR, 'unified_health_data.csv')
    merged.to_csv(merged_csv, index=False)
    merged.to_sql('unified_health_data', conn, if_exists='replace', index=False)
    print(f"Successfully merged NYC and hospital data. Saved to {merged_csv}")
else:
    print("Could not merge NYC and hospital data due to missing columns")

conn.close()

print(f"Data processing complete. All files saved in {OUTPUT_DIR}")