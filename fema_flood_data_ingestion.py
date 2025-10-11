#!/usr/bin/env python3
"""
FEMA Flood Hazard Zones Data Ingestion for NYC
Hackathon Phase 1: Data Acquisition & Initial Processing

This script fetches FEMA flood hazard data for NYC and processes it
for integration with existing health surveillance data.
"""

import os
import requests
import zipfile
import geopandas as gpd
import pandas as pd
import sqlite3
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FEMAFloodDataProcessor:
    def __init__(self, data_dir="fema_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.db_path = "public_health_data.db"
        
        # FEMA flood data URLs for NYC boroughs
        self.fema_urls = {
            'manhattan': 'https://hazards.fema.gov/nfhlv2/output/State/DFIRM_DB_36061C_20110715.zip',
            'brooklyn_queens': 'https://hazards.fema.gov/nfhlv2/output/State/DFIRM_DB_36047C_20110715.zip',
            'bronx': 'https://hazards.fema.gov/nfhlv2/output/State/DFIRM_DB_36005C_20110715.zip',
            'staten_island': 'https://hazards.fema.gov/nfhlv2/output/State/DFIRM_DB_36085C_20110715.zip'
        }
        
        # Alternative: NYC Open Data flood zones (more accessible for hackathon)
        self.nyc_flood_url = "https://data.cityofnewyork.us/api/geospatial/27ya-gqtm?method=export&format=GeoJSON"

        # Backup: Create mock flood data for hackathon demo
        self.use_mock_data = True
        
    def create_mock_flood_data(self):
        """Create mock flood data for hackathon demo"""
        logger.info("Creating mock flood data for hackathon demo...")

        try:
            from shapely.geometry import Polygon
            import numpy as np

            # NYC borough coordinates (approximate)
            nyc_bounds = {
                'manhattan': {'lat': [40.700, 40.800], 'lon': [-74.020, -73.930]},
                'brooklyn': {'lat': [40.570, 40.740], 'lon': [-74.050, -73.860]},
                'queens': {'lat': [40.540, 40.800], 'lon': [-73.960, -73.700]},
                'bronx': {'lat': [40.790, 40.920], 'lon': [-73.930, -73.760]},
                'staten_island': {'lat': [40.480, 40.650], 'lon': [-74.260, -74.050]}
            }

            flood_zones = []
            zone_types = ['AE', 'A', 'X', 'VE', 'AH']

            for borough, bounds in nyc_bounds.items():
                # Create 5-10 flood zones per borough
                for i in range(np.random.randint(5, 11)):
                    # Random coordinates within borough bounds
                    lat_min, lat_max = bounds['lat']
                    lon_min, lon_max = bounds['lon']

                    # Create a small polygon
                    center_lat = np.random.uniform(lat_min, lat_max)
                    center_lon = np.random.uniform(lon_min, lon_max)

                    # Small polygon around center
                    size = 0.005  # About 500m
                    coords = [
                        (center_lon - size, center_lat - size),
                        (center_lon + size, center_lat - size),
                        (center_lon + size, center_lat + size),
                        (center_lon - size, center_lat + size),
                        (center_lon - size, center_lat - size)
                    ]

                    polygon = Polygon(coords)
                    zone_type = np.random.choice(zone_types)

                    flood_zones.append({
                        'FLD_ZONE': zone_type,
                        'ZONE_SUBTY': f"{zone_type}_SUBTYPE",
                        'DFIRM_ID': f"NYC_{borough.upper()}_{i:03d}",
                        'GIS_ID': f"{borough}_{i}",
                        'borough': borough,
                        'geometry': polygon
                    })

            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame(flood_zones, crs='EPSG:4326')

            # Save to file
            flood_file = self.data_dir / "mock_nyc_flood_zones.geojson"
            gdf.to_file(flood_file, driver='GeoJSON')

            logger.info(f"Created {len(flood_zones)} mock flood zones")
            logger.info(f"Saved mock data to {flood_file}")
            return flood_file

        except Exception as e:
            logger.error(f"Error creating mock flood data: {e}")
            return None

    def download_nyc_flood_data(self):
        """Download NYC flood hazard zones from NYC Open Data (faster for hackathon)"""
        logger.info("Downloading NYC flood hazard zones from NYC Open Data...")

        try:
            response = requests.get(self.nyc_flood_url, timeout=30)
            response.raise_for_status()

            flood_file = self.data_dir / "nyc_flood_zones.geojson"
            with open(flood_file, 'wb') as f:
                f.write(response.content)

            logger.info(f"Downloaded flood data to {flood_file}")
            return flood_file

        except Exception as e:
            logger.error(f"Error downloading NYC flood data: {e}")
            if self.use_mock_data:
                logger.info("Falling back to mock data for hackathon...")
                return self.create_mock_flood_data()
            return None
    
    def download_fema_data(self, borough):
        """Download FEMA DFIRM data for specific borough"""
        if borough not in self.fema_urls:
            logger.error(f"Unknown borough: {borough}")
            return None
            
        url = self.fema_urls[borough]
        zip_file = self.data_dir / f"fema_{borough}.zip"
        
        logger.info(f"Downloading FEMA data for {borough}...")
        
        try:
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(zip_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Downloaded {zip_file}")
            return zip_file
            
        except Exception as e:
            logger.error(f"Error downloading FEMA data for {borough}: {e}")
            return None
    
    def extract_and_process_fema(self, zip_file, borough):
        """Extract and process FEMA shapefile data"""
        extract_dir = self.data_dir / f"extracted_{borough}"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the flood zone shapefile
            shapefiles = list(extract_dir.rglob("*FLD_HAZ_AR*.shp"))
            if not shapefiles:
                shapefiles = list(extract_dir.rglob("*.shp"))
            
            if shapefiles:
                return shapefiles[0]
            else:
                logger.error(f"No shapefiles found in {extract_dir}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting {zip_file}: {e}")
            return None
    
    def process_flood_data(self, data_file):
        """Process flood hazard data into standardized format"""
        logger.info(f"Processing flood data from {data_file}")
        
        try:
            # Read the geospatial data
            if str(data_file).endswith('.geojson'):
                gdf = gpd.read_file(data_file)
            else:
                gdf = gpd.read_file(data_file)
            
            logger.info(f"Loaded {len(gdf)} flood zone features")
            logger.info(f"Original CRS: {gdf.crs}")
            
            # Convert to EPSG:4326 (WGS84) for consistency
            if gdf.crs != 'EPSG:4326':
                gdf = gdf.to_crs('EPSG:4326')
                logger.info("Converted to EPSG:4326")
            
            # Standardize column names based on data source
            if 'FLD_ZONE' in gdf.columns:
                # FEMA DFIRM format
                flood_df = gdf[['FLD_ZONE', 'ZONE_SUBTY', 'geometry']].copy()
                flood_df['DFIRM_ID'] = gdf.get('DFIRM_ID', 'NYC_FEMA')
                flood_df['GIS_ID'] = gdf.get('GIS_ID', range(len(gdf)))
            elif 'floodzone' in gdf.columns:
                # NYC Open Data format
                flood_df = gdf[['floodzone', 'geometry']].copy()
                flood_df['FLD_ZONE'] = flood_df['floodzone']
                flood_df['ZONE_SUBTY'] = gdf.get('subtype', 'Unknown')
                flood_df['DFIRM_ID'] = 'NYC_OPENDATA'
                flood_df['GIS_ID'] = range(len(gdf))
            elif 'fld_zone' in gdf.columns:
                # NYC Open Data format (lowercase)
                flood_df = gdf[['fld_zone', 'geometry']].copy()
                flood_df['FLD_ZONE'] = flood_df['fld_zone']
                flood_df['ZONE_SUBTY'] = gdf.get('gridcode', 'Unknown')
                flood_df['DFIRM_ID'] = 'NYC_OPENDATA'
                flood_df['GIS_ID'] = range(len(gdf))
                # Drop the original column to avoid duplication
                flood_df = flood_df.drop('fld_zone', axis=1)
            else:
                # Generic processing
                logger.warning("Unknown flood data format, using generic processing")
                flood_df = gdf.copy()
                flood_df['FLD_ZONE'] = 'Unknown'
                flood_df['ZONE_SUBTY'] = 'Unknown'
                flood_df['DFIRM_ID'] = 'GENERIC'
                flood_df['GIS_ID'] = range(len(gdf))
            
            # Add metadata
            flood_df['data_source'] = 'FEMA_FLOOD_ZONES'
            flood_df['ingestion_date'] = datetime.now().isoformat()
            flood_df['risk_level'] = flood_df['FLD_ZONE'].map(self.get_risk_level)
            
            # Calculate area for analysis
            flood_df['area_sq_meters'] = flood_df.geometry.area
            
            logger.info(f"Processed flood zones by type:")
            logger.info(flood_df['FLD_ZONE'].value_counts())
            
            return flood_df
            
        except Exception as e:
            logger.error(f"Error processing flood data: {e}")
            return None
    
    def get_risk_level(self, flood_zone):
        """Map FEMA flood zones to risk levels"""
        high_risk = ['A', 'AE', 'AH', 'AO', 'AR', 'A99', 'V', 'VE']
        moderate_risk = ['B', 'X']
        
        if any(zone in str(flood_zone).upper() for zone in high_risk):
            return 'HIGH'
        elif any(zone in str(flood_zone).upper() for zone in moderate_risk):
            return 'MODERATE'
        else:
            return 'LOW'
    
    def save_to_database(self, flood_df):
        """Save processed flood data to SQLite database"""
        logger.info("Saving flood data to database...")
        
        try:
            # Convert geometry to WKT for database storage
            flood_df_db = flood_df.copy()
            flood_df_db['geometry_wkt'] = flood_df_db.geometry.to_wkt()
            flood_df_db = flood_df_db.drop('geometry', axis=1)
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            
            # Save to database
            flood_df_db.to_sql('fema_flood_zones', conn, if_exists='replace', index=False)
            
            # Create indexes for performance
            cursor = conn.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_flood_zone ON fema_flood_zones(FLD_ZONE)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_level ON fema_flood_zones(risk_level)")
            
            conn.commit()
            conn.close()
            
            logger.info(f"Saved {len(flood_df_db)} flood zone records to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            return False
    
    def generate_summary_stats(self, flood_df):
        """Generate summary statistics for the flood data"""
        logger.info("Generating flood data summary...")
        
        summary = {
            'total_zones': len(flood_df),
            'zone_types': flood_df['FLD_ZONE'].value_counts().to_dict(),
            'risk_distribution': flood_df['risk_level'].value_counts().to_dict(),
            'total_area_sq_km': flood_df['area_sq_meters'].sum() / 1_000_000,
            'data_source': flood_df['data_source'].iloc[0] if len(flood_df) > 0 else 'Unknown',
            'ingestion_date': datetime.now().isoformat()
        }
        
        logger.info("=== FLOOD DATA SUMMARY ===")
        logger.info(f"Total flood zones: {summary['total_zones']}")
        logger.info(f"Zone types: {summary['zone_types']}")
        logger.info(f"Risk distribution: {summary['risk_distribution']}")
        logger.info(f"Total area: {summary['total_area_sq_km']:.2f} sq km")
        
        return summary

def main():
    """Main execution function"""
    logger.info("Starting FEMA Flood Data Ingestion for Hackathon...")
    
    processor = FEMAFloodDataProcessor()
    
    # Try NYC Open Data first (faster for hackathon)
    flood_file = processor.download_nyc_flood_data()
    
    if flood_file and flood_file.exists():
        # Process the downloaded data
        flood_df = processor.process_flood_data(flood_file)
        
        if flood_df is not None:
            # Save to database
            success = processor.save_to_database(flood_df)
            
            if success:
                # Generate summary
                summary = processor.generate_summary_stats(flood_df)
                
                logger.info("✅ FEMA flood data ingestion completed successfully!")
                logger.info("Ready for Phase 2: Cross-dataset integration")
                
                return flood_df, summary
            else:
                logger.error("Failed to save flood data to database")
        else:
            logger.error("Failed to process flood data")
    else:
        logger.error("Failed to download flood data")
    
    return None, None

if __name__ == "__main__":
    flood_data, summary = main()
