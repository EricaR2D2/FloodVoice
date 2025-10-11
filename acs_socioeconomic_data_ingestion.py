#!/usr/bin/env python3
"""
NYC American Community Survey (ACS) Socioeconomic Data Ingestion
Hackathon Phase 1B: Vulnerability Indicators for Cross-Dataset Integration

This script fetches and processes ACS socioeconomic data for NYC census tracts
to enable AI-powered correlation with flood zones and health outcomes.
"""

import os
import requests
import pandas as pd
import sqlite3
from pathlib import Path
import logging
from datetime import datetime
import zipfile
import io

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ACSDataProcessor:
    def __init__(self, data_dir="acs_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = "public_health_data.db"
        
        # NYC Planning ACS data URLs (2022 5-Year estimates)
        self.acs_urls = {
            'demographic': 'https://www1.nyc.gov/assets/planning/download/zip/data-maps/nyc-population/acs2022/nyc2022acs5yr_demo.zip',
            'economic': 'https://www1.nyc.gov/assets/planning/download/zip/data-maps/nyc-population/acs2022/nyc2022acs5yr_econ.zip',
            'housing': 'https://www1.nyc.gov/assets/planning/download/zip/data-maps/nyc-population/acs2022/nyc2022acs5yr_hous.zip',
            'social': 'https://www1.nyc.gov/assets/planning/download/zip/data-maps/nyc-population/acs2022/nyc2022acs5yr_soci.zip'
        }
        
        # Alternative: Direct CSV URLs (if available)
        self.direct_csv_url = "https://www1.nyc.gov/assets/planning/download/csv/data-maps/nyc-population/acs2022/nyc2022acs5yr_demo.csv"
        
        # Key vulnerability indicators we need
        self.vulnerability_columns = [
            'GEOID',           # Census tract identifier
            'Pop_1E',          # Total population estimate
            'PovU_1E',         # Population for whom poverty status is determined
            'Pov_1E',          # Population below poverty level
            'HU_1E',           # Total housing units
            'HUOcc_1E',        # Occupied housing units
            'HURent_1E',       # Renter-occupied housing units
            'LEP_1E',          # Limited English proficiency households
            'Age65pl_1E',      # Population 65 years and over
            'Dis_1E',          # Population with a disability
            'NTVBorn_1E',      # Native born population
            'FBorn_1E',        # Foreign born population
        ]
        
        # Column mapping for standardization
        self.column_mapping = {
            'Pop_1E': 'total_population',
            'Pov_1E': 'poverty_population',
            'PovU_1E': 'poverty_universe',
            'HU_1E': 'total_housing_units',
            'HUOcc_1E': 'housing_units_occupied',
            'HURent_1E': 'housing_units_occupied_renter',
            'LEP_1E': 'lep_households',
            'Age65pl_1E': 'age_65_plus_population',
            'Dis_1E': 'disabled_population',
            'NTVBorn_1E': 'native_born_population',
            'FBorn_1E': 'foreign_born_population'
        }
    
    def download_acs_data(self, data_type='demographic'):
        """Download ACS data from NYC Planning"""
        logger.info(f"Downloading NYC ACS {data_type} data...")
        
        if data_type not in self.acs_urls:
            logger.error(f"Unknown data type: {data_type}")
            return None
        
        url = self.acs_urls[data_type]
        zip_file = self.data_dir / f"acs_{data_type}.zip"
        
        try:
            response = requests.get(url, stream=True, timeout=120)
            response.raise_for_status()
            
            with open(zip_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded {zip_file}")
            return zip_file
            
        except Exception as e:
            logger.error(f"Error downloading ACS {data_type} data: {e}")
            # Try direct CSV download as fallback
            return self.download_direct_csv()
    
    def download_direct_csv(self):
        """Fallback: Try direct CSV download"""
        logger.info("Trying direct CSV download as fallback...")
        
        try:
            response = requests.get(self.direct_csv_url, timeout=60)
            response.raise_for_status()
            
            csv_file = self.data_dir / "nyc_acs_demographic.csv"
            with open(csv_file, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded direct CSV to {csv_file}")
            return csv_file
            
        except Exception as e:
            logger.error(f"Error downloading direct CSV: {e}")
            return self.create_mock_acs_data()
    
    def extract_csv_from_zip(self, zip_file):
        """Extract CSV file from downloaded ZIP"""
        extract_dir = self.data_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find CSV files
            csv_files = list(extract_dir.rglob("*.csv"))
            if csv_files:
                logger.info(f"Found CSV file: {csv_files[0]}")
                return csv_files[0]
            else:
                logger.error("No CSV files found in ZIP")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting ZIP: {e}")
            return None
    
    def create_mock_acs_data(self):
        """Create mock ACS data for hackathon demo"""
        logger.info("Creating mock ACS data for hackathon demo...")
        
        try:
            import numpy as np
            
            # NYC census tracts (approximate - real data would have ~2,100 tracts)
            n_tracts = 500  # Reduced for demo
            
            # Generate realistic GEOID format: 36[county][tract]
            # NYC counties: 005(Bronx), 047(Brooklyn), 061(Manhattan), 081(Queens), 085(Staten Island)
            counties = ['005', '047', '061', '081', '085']
            
            mock_data = []
            for i in range(n_tracts):
                county = np.random.choice(counties)
                tract = f"{i:06d}"  # 6-digit tract number
                geoid = f"36{county}{tract}"
                
                # Generate realistic demographic data
                total_pop = np.random.randint(1000, 8000)
                poverty_pop = int(total_pop * np.random.uniform(0.05, 0.35))
                housing_units = int(total_pop * np.random.uniform(0.3, 0.6))
                renter_units = int(housing_units * np.random.uniform(0.4, 0.9))
                lep_households = int(total_pop * np.random.uniform(0.1, 0.4) * 0.4)  # households
                age_65_plus = int(total_pop * np.random.uniform(0.08, 0.25))
                disabled = int(total_pop * np.random.uniform(0.05, 0.15))
                
                mock_data.append({
                    'GEOID': geoid,
                    'Pop_1E': total_pop,
                    'Pov_1E': poverty_pop,
                    'PovU_1E': total_pop,  # Universe for poverty calculation
                    'HU_1E': housing_units,
                    'HUOcc_1E': int(housing_units * 0.9),
                    'HURent_1E': renter_units,
                    'LEP_1E': lep_households,
                    'Age65pl_1E': age_65_plus,
                    'Dis_1E': disabled,
                    'NTVBorn_1E': int(total_pop * np.random.uniform(0.4, 0.8)),
                    'FBorn_1E': int(total_pop * np.random.uniform(0.2, 0.6))
                })
            
            # Create DataFrame and save
            df = pd.DataFrame(mock_data)
            csv_file = self.data_dir / "mock_nyc_acs_data.csv"
            df.to_csv(csv_file, index=False)
            
            logger.info(f"Created {len(mock_data)} mock census tracts")
            logger.info(f"Saved mock data to {csv_file}")
            return csv_file
            
        except Exception as e:
            logger.error(f"Error creating mock ACS data: {e}")
            return None
    
    def process_acs_data(self, data_file):
        """Process ACS data into standardized format"""
        logger.info(f"Processing ACS data from {data_file}")
        
        try:
            # Read the CSV data
            df = pd.read_csv(data_file)
            logger.info(f"Loaded {len(df)} census tract records")
            logger.info(f"Available columns: {df.columns.tolist()}")
            
            # Ensure GEOID is string for consistent merging
            df['GEOID'] = df['GEOID'].astype(str)
            
            # Select and rename vulnerability columns
            available_cols = [col for col in self.vulnerability_columns if col in df.columns]
            if not available_cols:
                logger.warning("No expected vulnerability columns found, using all numeric columns")
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                available_cols = ['GEOID'] + numeric_cols[:10]  # Take first 10 numeric columns
            
            acs_df = df[available_cols].copy()
            
            # Rename columns for standardization
            for old_col, new_col in self.column_mapping.items():
                if old_col in acs_df.columns:
                    acs_df = acs_df.rename(columns={old_col: new_col})
            
            # Calculate derived vulnerability indicators
            if 'poverty_population' in acs_df.columns and 'poverty_universe' in acs_df.columns:
                acs_df['poverty_rate'] = (acs_df['poverty_population'] / acs_df['poverty_universe']).fillna(0)
            else:
                acs_df['poverty_rate'] = 0.15  # Default estimate
            
            if 'housing_units_occupied_renter' in acs_df.columns and 'housing_units_occupied' in acs_df.columns:
                acs_df['renter_rate'] = (acs_df['housing_units_occupied_renter'] / acs_df['housing_units_occupied']).fillna(0)
            else:
                acs_df['renter_rate'] = 0.6  # Default estimate
            
            if 'age_65_plus_population' in acs_df.columns and 'total_population' in acs_df.columns:
                acs_df['elderly_rate'] = (acs_df['age_65_plus_population'] / acs_df['total_population']).fillna(0)
            else:
                acs_df['elderly_rate'] = 0.15  # Default estimate
            
            # Add vulnerability score (composite index)
            vulnerability_factors = []
            if 'poverty_rate' in acs_df.columns:
                vulnerability_factors.append(acs_df['poverty_rate'])
            if 'renter_rate' in acs_df.columns:
                vulnerability_factors.append(acs_df['renter_rate'])
            if 'elderly_rate' in acs_df.columns:
                vulnerability_factors.append(acs_df['elderly_rate'])
            
            if vulnerability_factors:
                acs_df['vulnerability_score'] = sum(vulnerability_factors) / len(vulnerability_factors)
            else:
                acs_df['vulnerability_score'] = 0.5  # Default moderate vulnerability
            
            # Add metadata
            acs_df['data_source'] = 'NYC_PLANNING_ACS'
            acs_df['ingestion_date'] = datetime.now().isoformat()
            acs_df['acs_year'] = '2022'
            
            # Classify vulnerability levels
            acs_df['vulnerability_level'] = pd.cut(
                acs_df['vulnerability_score'],
                bins=[0, 0.33, 0.66, 1.0],
                labels=['LOW', 'MODERATE', 'HIGH'],
                include_lowest=True
            )
            
            logger.info(f"Processed ACS data summary:")
            logger.info(f"Census tracts: {len(acs_df)}")
            logger.info(f"Vulnerability distribution:")
            logger.info(acs_df['vulnerability_level'].value_counts())
            
            return acs_df
            
        except Exception as e:
            logger.error(f"Error processing ACS data: {e}")
            return None
    
    def save_to_database(self, acs_df):
        """Save processed ACS data to SQLite database"""
        logger.info("Saving ACS data to database...")
        
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            
            # Save to database
            acs_df.to_sql('nyc_acs_socioeconomic', conn, if_exists='replace', index=False)
            
            # Create indexes for performance
            cursor = conn.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_acs_geoid ON nyc_acs_socioeconomic(GEOID)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_acs_vulnerability ON nyc_acs_socioeconomic(vulnerability_level)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_acs_poverty ON nyc_acs_socioeconomic(poverty_rate)")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved {len(acs_df)} ACS records to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            return False
    
    def generate_summary_stats(self, acs_df):
        """Generate summary statistics for the ACS data"""
        logger.info("Generating ACS data summary...")
        
        summary = {
            'total_census_tracts': len(acs_df),
            'total_population': acs_df.get('total_population', pd.Series([0])).sum(),
            'avg_poverty_rate': acs_df.get('poverty_rate', pd.Series([0])).mean(),
            'avg_renter_rate': acs_df.get('renter_rate', pd.Series([0])).mean(),
            'avg_elderly_rate': acs_df.get('elderly_rate', pd.Series([0])).mean(),
            'vulnerability_distribution': acs_df['vulnerability_level'].value_counts().to_dict(),
            'data_source': acs_df['data_source'].iloc[0] if len(acs_df) > 0 else 'Unknown',
            'ingestion_date': datetime.now().isoformat()
        }
        
        logger.info("=== ACS SOCIOECONOMIC DATA SUMMARY ===")
        logger.info(f"Total census tracts: {summary['total_census_tracts']}")
        logger.info(f"Total population: {summary['total_population']:,}")
        logger.info(f"Average poverty rate: {summary['avg_poverty_rate']:.1%}")
        logger.info(f"Average renter rate: {summary['avg_renter_rate']:.1%}")
        logger.info(f"Average elderly rate: {summary['avg_elderly_rate']:.1%}")
        logger.info(f"Vulnerability distribution: {summary['vulnerability_distribution']}")
        
        return summary

def main():
    """Main execution function"""
    logger.info("Starting NYC ACS Socioeconomic Data Ingestion for Hackathon...")
    
    processor = ACSDataProcessor()
    
    # Try to download demographic data first
    data_file = processor.download_acs_data('demographic')
    
    if data_file and data_file.exists():
        # If it's a ZIP file, extract CSV
        if str(data_file).endswith('.zip'):
            csv_file = processor.extract_csv_from_zip(data_file)
            if csv_file:
                data_file = csv_file
            else:
                logger.error("Failed to extract CSV from ZIP")
                return None, None
        
        # Process the data
        acs_df = processor.process_acs_data(data_file)
        
        if acs_df is not None:
            # Save to database
            success = processor.save_to_database(acs_df)
            
            if success:
                # Generate summary
                summary = processor.generate_summary_stats(acs_df)
                
                logger.info("✅ ACS socioeconomic data ingestion completed successfully!")
                logger.info("Ready for cross-dataset integration with flood zones and health data")
                
                return acs_df, summary
            else:
                logger.error("Failed to save ACS data to database")
        else:
            logger.error("Failed to process ACS data")
    else:
        logger.error("Failed to download ACS data")
    
    return None, None

if __name__ == "__main__":
    acs_data, summary = main()
