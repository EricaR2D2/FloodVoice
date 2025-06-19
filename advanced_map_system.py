#!/usr/bin/env python3
"""
Advanced Map Layering System for Public Health MVP
Multi-layer interactive maps with filtering, dark theme, and real-time data
"""

import folium
import pandas as pd
import sqlite3
import json
from datetime import datetime, timedelta
import numpy as np

class AdvancedMapSystem:
    """Advanced mapping system with multi-layer support and filtering"""
    
    def __init__(self, db_path="public_health_data.db"):
        self.db_path = db_path
        self.map_center = [40.7831, -73.9712]  # NYC center
        self.default_zoom = 11
        
        # Color schemes for different illness types (dark theme compatible)
        self.illness_colors = {
            'COVID-19': '#FF6B6B',           # Red
            'Flu': '#4ECDC4',                # Teal
            'Foodborne': '#45B7D1',          # Blue
            'Air Quality': '#96CEB4',        # Green
            'Tick Disease': '#FFEAA7',       # Yellow
            'Hospital ER': '#DDA0DD',        # Plum
            'Mental Health': '#98D8C8'       # Mint
        }
        
        # Risk level colors
        self.risk_colors = {
            'LOW': '#2ECC71',      # Green
            'MEDIUM': '#F39C12',   # Orange
            'HIGH': '#E74C3C',     # Red
            'HAZARDOUS': '#8E44AD' # Purple
        }
    
    def create_multi_layer_map(self, illness_filters=None, date_range=None, borough_filter=None):
        """Create a multi-layer map with filtering capabilities"""
        
        print("🗺️ Creating advanced multi-layer map...")
        
        # Create base map with dark theme
        m = folium.Map(
            location=self.map_center,
            zoom_start=self.default_zoom,
            tiles=None  # We'll add custom tiles
        )
        
        # Add dark theme tile layer
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            name='Dark Theme',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Add light theme as alternative
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='Light Theme',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Create feature groups for each illness type
        illness_layers = {}
        
        # Add COVID-19 layer
        if not illness_filters or 'COVID-19' in illness_filters:
            covid_layer = self.create_covid_layer(date_range, borough_filter)
            if covid_layer:
                illness_layers['COVID-19'] = covid_layer
                covid_layer.add_to(m)
        
        # Add Flu surveillance layer
        if not illness_filters or 'Flu' in illness_filters:
            flu_layer = self.create_flu_layer(date_range, borough_filter)
            if flu_layer:
                illness_layers['Flu'] = flu_layer
                flu_layer.add_to(m)
        
        # Add Foodborne illness layer
        if not illness_filters or 'Foodborne' in illness_filters:
            foodborne_layer = self.create_foodborne_layer(date_range, borough_filter)
            if foodborne_layer:
                illness_layers['Foodborne'] = foodborne_layer
                foodborne_layer.add_to(m)
        
        # Add Air Quality layer
        if not illness_filters or 'Air Quality' in illness_filters:
            air_quality_layer = self.create_air_quality_layer(date_range, borough_filter)
            if air_quality_layer:
                illness_layers['Air Quality'] = air_quality_layer
                air_quality_layer.add_to(m)
        
        # Add Hospital ER layer
        if not illness_filters or 'Hospital ER' in illness_filters:
            hospital_layer = self.create_hospital_layer(date_range, borough_filter)
            if hospital_layer:
                illness_layers['Hospital ER'] = hospital_layer
                hospital_layer.add_to(m)
        
        # Add Tick Disease layer
        if not illness_filters or 'Tick Disease' in illness_filters:
            tick_layer = self.create_tick_disease_layer(date_range, borough_filter)
            if tick_layer:
                illness_layers['Tick Disease'] = tick_layer
                tick_layer.add_to(m)
        
        # Add layer control
        folium.LayerControl(collapsed=False).add_to(m)
        
        # Add custom legend
        self.add_legend(m, illness_layers.keys())
        
        # Add custom JavaScript for enhanced interactivity
        self.add_custom_javascript(m)
        
        print(f"✅ Created multi-layer map with {len(illness_layers)} illness types")
        return m
    
    def create_covid_layer(self, date_range=None, borough_filter=None):
        """Create COVID-19 data layer"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get COVID data by borough
            query = """
                SELECT 
                    date_of_interest,
                    'Bronx' as borough, BX_CASE_COUNT as cases, BX_HOSPITALIZED_COUNT as hospitalizations
                FROM nyc_covid_data
                WHERE BX_CASE_COUNT IS NOT NULL
                UNION ALL
                SELECT 
                    date_of_interest,
                    'Brooklyn' as borough, BK_CASE_COUNT as cases, BK_HOSPITALIZED_COUNT as hospitalizations
                FROM nyc_covid_data
                WHERE BK_CASE_COUNT IS NOT NULL
                UNION ALL
                SELECT 
                    date_of_interest,
                    'Manhattan' as borough, MN_CASE_COUNT as cases, MN_HOSPITALIZED_COUNT as hospitalizations
                FROM nyc_covid_data
                WHERE MN_CASE_COUNT IS NOT NULL
                UNION ALL
                SELECT 
                    date_of_interest,
                    'Queens' as borough, QN_CASE_COUNT as cases, QN_HOSPITALIZED_COUNT as hospitalizations
                FROM nyc_covid_data
                WHERE QN_CASE_COUNT IS NOT NULL
                UNION ALL
                SELECT 
                    date_of_interest,
                    'Staten Island' as borough, SI_CASE_COUNT as cases, SI_HOSPITALIZED_COUNT as hospitalizations
                FROM nyc_covid_data
                WHERE SI_CASE_COUNT IS NOT NULL
            """
            
            if date_range:
                query += f" AND date_of_interest >= '{date_range[0]}' AND date_of_interest <= '{date_range[1]}'"
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return None
            
            # Aggregate recent data by borough
            recent_data = df.groupby('borough').agg({
                'cases': 'sum',
                'hospitalizations': 'sum'
            }).reset_index()
            
            # Create feature group
            covid_layer = folium.FeatureGroup(name='COVID-19 Cases', show=True)
            
            # Borough coordinates
            borough_coords = {
                'Bronx': [40.8448, -73.8648],
                'Brooklyn': [40.6782, -73.9442],
                'Manhattan': [40.7831, -73.9712],
                'Queens': [40.7282, -73.7949],
                'Staten Island': [40.5795, -74.1502]
            }
            
            for _, row in recent_data.iterrows():
                borough = row['borough']
                cases = int(row['cases']) if pd.notna(row['cases']) else 0
                hospitalizations = int(row['hospitalizations']) if pd.notna(row['hospitalizations']) else 0
                
                if borough in borough_coords:
                    # Determine marker size based on case count
                    marker_size = min(50, max(10, cases / 100))
                    
                    # Determine color based on hospitalization rate
                    hosp_rate = (hospitalizations / cases * 100) if cases > 0 else 0
                    color = self.get_risk_color(hosp_rate, [0, 2, 5, 10])  # Hospitalization rate thresholds
                    
                    folium.CircleMarker(
                        location=borough_coords[borough],
                        radius=marker_size,
                        popup=f"""
                        <div style='width: 200px'>
                            <h4 style='color: {self.illness_colors['COVID-19']}'>{borough} - COVID-19</h4>
                            <p><strong>Total Cases:</strong> {cases:,}</p>
                            <p><strong>Hospitalizations:</strong> {hospitalizations:,}</p>
                            <p><strong>Hospitalization Rate:</strong> {hosp_rate:.1f}%</p>
                        </div>
                        """,
                        color=color,
                        fillColor=self.illness_colors['COVID-19'],
                        fillOpacity=0.7,
                        weight=2
                    ).add_to(covid_layer)
            
            return covid_layer
            
        except Exception as e:
            print(f"Error creating COVID layer: {e}")
            return None
    
    def create_flu_layer(self, date_range=None, borough_filter=None):
        """Create flu surveillance data layer"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT zip_code, borough, 
                       AVG(flu_percentage) as avg_flu_rate,
                       SUM(flu_like_visits) as total_flu_visits,
                       COUNT(*) as total_records
                FROM flu_surveillance_data
                WHERE 1=1
            """
            
            if date_range:
                query += f" AND date >= '{date_range[0]}' AND date <= '{date_range[1]}'"
            
            if borough_filter:
                query += f" AND borough = '{borough_filter}'"
            
            query += " GROUP BY zip_code, borough HAVING total_records > 5"
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return None
            
            # Create feature group
            flu_layer = folium.FeatureGroup(name='Flu Surveillance', show=True)
            
            for _, row in df.iterrows():
                zip_code = row['zip_code']
                borough = row['borough']
                flu_rate = float(row['avg_flu_rate']) if pd.notna(row['avg_flu_rate']) else 0
                flu_visits = int(row['total_flu_visits']) if pd.notna(row['total_flu_visits']) else 0
                
                # Get ZIP code coordinates (simplified - you'd want a proper ZIP code geocoding service)
                coords = self.get_zip_coordinates(zip_code, borough)
                
                if coords:
                    # Determine marker size and color based on flu rate
                    marker_size = min(30, max(5, flu_rate * 2))
                    color = self.get_risk_color(flu_rate, [5, 10, 15, 25])  # Flu rate thresholds
                    
                    folium.CircleMarker(
                        location=coords,
                        radius=marker_size,
                        popup=f"""
                        <div style='width: 200px'>
                            <h4 style='color: {self.illness_colors['Flu']}'>{zip_code} - Flu Surveillance</h4>
                            <p><strong>Borough:</strong> {borough}</p>
                            <p><strong>Avg Flu Rate:</strong> {flu_rate:.1f}%</p>
                            <p><strong>Total Flu Visits:</strong> {flu_visits:,}</p>
                        </div>
                        """,
                        color=color,
                        fillColor=self.illness_colors['Flu'],
                        fillOpacity=0.6,
                        weight=2
                    ).add_to(flu_layer)
            
            return flu_layer
            
        except Exception as e:
            print(f"Error creating flu layer: {e}")
            return None
    
    def create_foodborne_layer(self, date_range=None, borough_filter=None):
        """Create foodborne illness risk layer"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT zip_code, borough, foodborne_risk_score, 
                       high_risk_inspections, total_inspections, risk_level
                FROM foodborne_illness_risk_summary
                WHERE 1=1
            """
            
            if borough_filter:
                query += f" AND borough = '{borough_filter}'"
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return None
            
            # Create feature group
            foodborne_layer = folium.FeatureGroup(name='Foodborne Risk', show=True)
            
            for _, row in df.iterrows():
                zip_code = row['zip_code']
                borough = row['borough']
                risk_score = float(row['foodborne_risk_score']) if pd.notna(row['foodborne_risk_score']) else 0
                high_risk = int(row['high_risk_inspections']) if pd.notna(row['high_risk_inspections']) else 0
                total = int(row['total_inspections']) if pd.notna(row['total_inspections']) else 0
                risk_level = row['risk_level']
                
                coords = self.get_zip_coordinates(zip_code, borough)
                
                if coords:
                    # Determine marker size and color based on risk score
                    marker_size = min(25, max(5, risk_score / 4))
                    color = self.risk_colors.get(risk_level, '#95A5A6')
                    
                    folium.CircleMarker(
                        location=coords,
                        radius=marker_size,
                        popup=f"""
                        <div style='width: 200px'>
                            <h4 style='color: {self.illness_colors['Foodborne']}'>{zip_code} - Foodborne Risk</h4>
                            <p><strong>Borough:</strong> {borough}</p>
                            <p><strong>Risk Score:</strong> {risk_score:.1f}/100</p>
                            <p><strong>Risk Level:</strong> {risk_level}</p>
                            <p><strong>High-Risk Inspections:</strong> {high_risk}/{total}</p>
                        </div>
                        """,
                        color=color,
                        fillColor=self.illness_colors['Foodborne'],
                        fillOpacity=0.6,
                        weight=2
                    ).add_to(foodborne_layer)
            
            return foodborne_layer
            
        except Exception as e:
            print(f"Error creating foodborne layer: {e}")
            return None
    
    def create_air_quality_layer(self, date_range=None, borough_filter=None):
        """Create air quality data layer"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT location_name, borough, air_quality_score, 
                       avg_pm25, avg_ozone, risk_level, unhealthy_percentage
                FROM air_quality_summary
                WHERE 1=1
            """
            
            if borough_filter:
                query += f" AND borough = '{borough_filter}'"
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return None
            
            # Create feature group
            air_layer = folium.FeatureGroup(name='Air Quality', show=True)
            
            for _, row in df.iterrows():
                location = row['location_name']
                borough = row['borough']
                air_score = float(row['air_quality_score']) if pd.notna(row['air_quality_score']) else 0
                pm25 = float(row['avg_pm25']) if pd.notna(row['avg_pm25']) else 0
                ozone = float(row['avg_ozone']) if pd.notna(row['avg_ozone']) else 0
                risk_level = row['risk_level']
                unhealthy_pct = float(row['unhealthy_percentage']) if pd.notna(row['unhealthy_percentage']) else 0
                
                # Get location coordinates (simplified)
                coords = self.get_location_coordinates(location, borough)
                
                if coords:
                    # Determine marker size and color based on air quality score
                    marker_size = min(30, max(8, air_score / 3))
                    color = self.risk_colors.get(risk_level, '#95A5A6')
                    
                    folium.CircleMarker(
                        location=coords,
                        radius=marker_size,
                        popup=f"""
                        <div style='width: 220px'>
                            <h4 style='color: {self.illness_colors['Air Quality']}'>{location}</h4>
                            <p><strong>Borough:</strong> {borough}</p>
                            <p><strong>Air Quality Score:</strong> {air_score:.1f}/100</p>
                            <p><strong>Risk Level:</strong> {risk_level}</p>
                            <p><strong>Avg PM2.5:</strong> {pm25:.1f} μg/m³</p>
                            <p><strong>Avg Ozone:</strong> {ozone:.3f} ppm</p>
                            <p><strong>Unhealthy Days:</strong> {unhealthy_pct:.1f}%</p>
                        </div>
                        """,
                        color=color,
                        fillColor=self.illness_colors['Air Quality'],
                        fillOpacity=0.6,
                        weight=2
                    ).add_to(air_layer)
            
            return air_layer
            
        except Exception as e:
            print(f"Error creating air quality layer: {e}")
            return None

    def create_hospital_layer(self, date_range=None, borough_filter=None):
        """Create hospital ER data layer"""

        try:
            conn = sqlite3.connect(self.db_path)

            query = """
                SELECT hospital_name, borough, zip_code, latitude, longitude,
                       AVG(respiratory_percentage) as avg_respiratory_rate,
                       SUM(total_visits) as total_visits,
                       SUM(respiratory_visits) as total_respiratory
                FROM real_hospital_data
                WHERE 1=1
            """

            if date_range:
                query += f" AND date >= '{date_range[0]}' AND date <= '{date_range[1]}'"

            if borough_filter:
                query += f" AND borough = '{borough_filter}'"

            query += " GROUP BY hospital_name, borough, zip_code, latitude, longitude"

            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                return None

            # Create feature group
            hospital_layer = folium.FeatureGroup(name='Hospital ER', show=True)

            for _, row in df.iterrows():
                hospital = row['hospital_name']
                borough = row['borough']
                zip_code = row['zip_code']
                lat = float(row['latitude']) if pd.notna(row['latitude']) else None
                lon = float(row['longitude']) if pd.notna(row['longitude']) else None
                resp_rate = float(row['avg_respiratory_rate']) if pd.notna(row['avg_respiratory_rate']) else 0
                total_visits = int(row['total_visits']) if pd.notna(row['total_visits']) else 0
                resp_visits = int(row['total_respiratory']) if pd.notna(row['total_respiratory']) else 0

                if lat and lon:
                    # Determine marker size and color based on respiratory rate
                    marker_size = min(35, max(10, resp_rate * 1.5))
                    color = self.get_risk_color(resp_rate, [10, 20, 30, 40])  # Respiratory rate thresholds

                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=marker_size,
                        popup=f"""
                        <div style='width: 220px'>
                            <h4 style='color: {self.illness_colors['Hospital ER']}'>{hospital}</h4>
                            <p><strong>Borough:</strong> {borough}</p>
                            <p><strong>ZIP Code:</strong> {zip_code}</p>
                            <p><strong>Respiratory Rate:</strong> {resp_rate:.1f}%</p>
                            <p><strong>Total Visits:</strong> {total_visits:,}</p>
                            <p><strong>Respiratory Visits:</strong> {resp_visits:,}</p>
                        </div>
                        """,
                        color=color,
                        fillColor=self.illness_colors['Hospital ER'],
                        fillOpacity=0.7,
                        weight=2
                    ).add_to(hospital_layer)

            return hospital_layer

        except Exception as e:
            print(f"Error creating hospital layer: {e}")
            return None

    def create_tick_disease_layer(self, date_range=None, borough_filter=None):
        """Create tick disease surveillance layer"""

        try:
            conn = sqlite3.connect(self.db_path)

            query = """
                SELECT zip_code, borough, latitude, longitude,
                       total_cases, severe_cases, risk_level
                FROM real_tick_disease_summary
                WHERE 1=1
            """

            if borough_filter:
                query += f" AND borough = '{borough_filter}'"

            df = pd.read_sql_query(query, conn)
            conn.close()

            if df.empty:
                return None

            # Create feature group
            tick_layer = folium.FeatureGroup(name='Tick Disease', show=True)

            for _, row in df.iterrows():
                zip_code = row['zip_code']
                borough = row['borough']
                lat = float(row['latitude']) if pd.notna(row['latitude']) else None
                lon = float(row['longitude']) if pd.notna(row['longitude']) else None
                total_cases = int(row['total_cases']) if pd.notna(row['total_cases']) else 0
                severe_cases = int(row['severe_cases']) if pd.notna(row['severe_cases']) else 0
                risk_level = row['risk_level']

                if lat and lon and total_cases > 0:
                    # Determine marker size and color based on case count
                    marker_size = min(25, max(8, total_cases * 2))
                    color = self.risk_colors.get(risk_level, '#95A5A6')

                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=marker_size,
                        popup=f"""
                        <div style='width: 200px'>
                            <h4 style='color: {self.illness_colors['Tick Disease']}'>{zip_code} - Tick Disease</h4>
                            <p><strong>Borough:</strong> {borough}</p>
                            <p><strong>Total Cases:</strong> {total_cases}</p>
                            <p><strong>Severe Cases:</strong> {severe_cases}</p>
                            <p><strong>Risk Level:</strong> {risk_level}</p>
                        </div>
                        """,
                        color=color,
                        fillColor=self.illness_colors['Tick Disease'],
                        fillOpacity=0.6,
                        weight=2
                    ).add_to(tick_layer)

            return tick_layer

        except Exception as e:
            print(f"Error creating tick disease layer: {e}")
            return None

    def get_risk_color(self, value, thresholds):
        """Get color based on risk thresholds"""
        if value <= thresholds[0]:
            return self.risk_colors['LOW']
        elif value <= thresholds[1]:
            return self.risk_colors['MEDIUM']
        elif value <= thresholds[2]:
            return self.risk_colors['HIGH']
        else:
            return self.risk_colors['HAZARDOUS']

    def get_zip_coordinates(self, zip_code, borough):
        """Get approximate coordinates for ZIP code (simplified)"""
        # This is a simplified mapping - in production you'd use a proper geocoding service
        zip_coords = {
            # Manhattan
            '10001': [40.7505, -73.9934], '10002': [40.7157, -73.9860], '10003': [40.7310, -73.9896],
            '10004': [40.7047, -73.9861], '10005': [40.7061, -73.9969], '10006': [40.7090, -74.0134],
            '10007': [40.7130, -74.0088], '10009': [40.7267, -73.9787], '10010': [40.7391, -73.9826],
            '10011': [40.7406, -74.0014], '10012': [40.7256, -73.9986], '10013': [40.7197, -74.0031],
            '10014': [40.7342, -74.0065], '10016': [40.7452, -73.9785], '10017': [40.7520, -73.9717],
            '10018': [40.7549, -73.9925], '10019': [40.7656, -73.9831], '10020': [40.7589, -73.9759],
            '10021': [40.7697, -73.9584], '10022': [40.7575, -73.9718], '10023': [40.7756, -73.9828],
            '10024': [40.7864, -73.9761], '10025': [40.7957, -73.9667], '10026': [40.8018, -73.9527],
            '10027': [40.8116, -73.9537], '10028': [40.7766, -73.9534], '10029': [40.7917, -73.9441],
            '10030': [40.8180, -73.9428], '10031': [40.8251, -73.9501], '10032': [40.8387, -73.9422],
            '10033': [40.8502, -73.9343], '10034': [40.8677, -73.9250], '10035': [40.7957, -73.9389],

            # Brooklyn
            '11201': [40.6944, -73.9903], '11203': [40.6501, -73.9323], '11204': [40.6181, -73.9845],
            '11205': [40.6955, -73.9662], '11206': [40.7018, -73.9422], '11207': [40.6719, -73.8943],
            '11208': [40.6719, -73.8668], '11209': [40.6220, -74.0305], '11210': [40.6284, -73.9473],
            '11211': [40.7115, -73.9540], '11212': [40.6627, -73.9123], '11213': [40.6710, -73.9360],
            '11214': [40.5992, -73.9969], '11215': [40.6628, -73.9865], '11216': [40.6839, -73.9493],
            '11217': [40.6839, -73.9668], '11218': [40.6439, -73.9761], '11219': [40.6362, -73.9962],
            '11220': [40.6414, -74.0178], '11221': [40.6915, -73.9274], '11222': [40.7284, -73.9474],
            '11223': [40.5968, -73.9735], '11224': [40.5775, -73.9885], '11225': [40.6628, -73.9533],
            '11226': [40.6464, -73.9562], '11228': [40.6173, -74.0134], '11229': [40.6007, -73.9444],
            '11230': [40.6221, -73.9654], '11231': [40.6776, -74.0047], '11232': [40.6565, -74.0047],
            '11233': [40.6783, -73.9196], '11234': [40.6007, -73.9196], '11235': [40.5847, -73.9479],
            '11236': [40.6407, -73.9012], '11237': [40.7043, -73.8803], '11238': [40.6794, -73.9442],
            '11239': [40.6471, -73.8803], '11249': [40.7211, -73.9532], '11251': [40.6628, -73.9442],

            # Queens
            '11101': [40.7505, -73.9342], '11102': [40.7736, -73.9123], '11103': [40.7628, -73.9123],
            '11104': [40.7447, -73.9196], '11105': [40.7736, -73.8943], '11106': [40.7628, -73.8943],
            '11354': [40.7681, -73.8370], '11355': [40.7498, -73.8370], '11356': [40.7850, -73.8481],
            '11357': [40.7850, -73.8259], '11358': [40.7628, -73.7943], '11359': [40.7850, -73.7943],
            '11360': [40.7850, -73.7721], '11361': [40.7628, -73.7721], '11362': [40.7628, -73.7499],
            '11363': [40.7850, -73.7499], '11364': [40.7628, -73.7277], '11365': [40.7407, -73.7943],
            '11366': [40.7407, -73.7721], '11367': [40.7407, -73.7499], '11368': [40.7407, -73.8481],
            '11369': [40.7628, -73.8481], '11370': [40.7628, -73.8259], '11371': [40.7628, -73.8037],
            '11372': [40.7407, -73.8259], '11373': [40.7407, -73.8037], '11374': [40.7186, -73.8259],
            '11375': [40.7186, -73.8037], '11377': [40.7407, -73.7815], '11378': [40.7186, -73.8481],
            '11379': [40.7186, -73.8703], '11385': [40.6965, -73.8481], '11411': [40.6965, -73.7499],
            '11412': [40.6965, -73.7277], '11413': [40.6744, -73.7499], '11414': [40.6523, -73.8481],
            '11415': [40.7186, -73.8259], '11416': [40.6744, -73.8481], '11417': [40.6744, -73.8259],
            '11418': [40.6965, -73.8259], '11419': [40.6965, -73.8037], '11420': [40.6744, -73.8037],
            '11421': [40.6965, -73.7815], '11422': [40.6744, -73.7815], '11423': [40.6744, -73.7593],
            '11426': [40.7186, -73.7277], '11427': [40.6965, -73.7055], '11428': [40.6744, -73.7055],
            '11429': [40.7186, -73.7055], '11432': [40.7186, -73.7943], '11433': [40.6965, -73.7943],
            '11434': [40.6744, -73.7943], '11435': [40.6744, -73.8703], '11436': [40.6523, -73.8703],

            # Bronx
            '10451': [40.8202, -73.9244], '10452': [40.8370, -73.9244], '10453': [40.8537, -73.9244],
            '10454': [40.8202, -73.9022], '10455': [40.8202, -73.9133], '10456': [40.8370, -73.9022],
            '10457': [40.8537, -73.9022], '10458': [40.8704, -73.9022], '10459': [40.8202, -73.8800],
            '10460': [40.8370, -73.8800], '10461': [40.8537, -73.8467], '10462': [40.8537, -73.8578],
            '10463': [40.8871, -73.9022], '10464': [40.8537, -73.8022], '10465': [40.8370, -73.8245],
            '10466': [40.8704, -73.8467], '10467': [40.8871, -73.8689], '10468': [40.8704, -73.9022],
            '10469': [40.8704, -73.8467], '10470': [40.8871, -73.8467], '10471': [40.8871, -73.9244],
            '10472': [40.8370, -73.8578], '10473': [40.8202, -73.8578], '10474': [40.8202, -73.8689],
            '10475': [40.8704, -73.8245],

            # Staten Island
            '10301': [40.6362, -74.0776], '10302': [40.6284, -74.1487], '10303': [40.6362, -74.1598],
            '10304': [40.6095, -74.0887], '10305': [40.5992, -74.0776], '10306': [40.5775, -74.1265],
            '10307': [40.5053, -74.2265], '10308': [40.5414, -74.1598], '10309': [40.5297, -74.2043],
            '10310': [40.6284, -74.1154], '10311': [40.6173, -74.1598], '10312': [40.5414, -74.1932],
            '10313': [40.5775, -74.1598], '10314': [40.5992, -74.1598]
        }

        return zip_coords.get(zip_code, None)

    def get_location_coordinates(self, location_name, borough):
        """Get approximate coordinates for location name"""
        # Simplified location mapping
        if borough == 'Manhattan':
            return [40.7831, -73.9712]
        elif borough == 'Brooklyn':
            return [40.6782, -73.9442]
        elif borough == 'Queens':
            return [40.7282, -73.7949]
        elif borough == 'Bronx':
            return [40.8448, -73.8648]
        elif borough == 'Staten Island':
            return [40.5795, -74.1502]
        else:
            return [40.7831, -73.9712]  # Default to Manhattan center

    def add_legend(self, map_obj, active_layers):
        """Add custom legend to the map"""

        legend_html = '''
        <div style="position: fixed;
                    top: 10px; right: 10px; width: 200px; height: auto;
                    background-color: rgba(0, 0, 0, 0.8); border:2px solid grey; z-index:9999;
                    font-size:14px; color: white; padding: 10px">
        <h4 style="margin-top:0; color: #fff;">Health Data Layers</h4>
        '''

        for illness_type in active_layers:
            color = self.illness_colors.get(illness_type, '#95A5A6')
            legend_html += f'''
            <p style="margin: 5px 0;">
                <span style="color: {color}; font-size: 16px;">●</span> {illness_type}
            </p>
            '''

        legend_html += '''
        <hr style="border-color: #666;">
        <h5 style="margin: 5px 0; color: #fff;">Risk Levels</h5>
        <p style="margin: 2px 0;"><span style="color: #2ECC71;">●</span> Low</p>
        <p style="margin: 2px 0;"><span style="color: #F39C12;">●</span> Medium</p>
        <p style="margin: 2px 0;"><span style="color: #E74C3C;">●</span> High</p>
        <p style="margin: 2px 0;"><span style="color: #8E44AD;">●</span> Hazardous</p>
        </div>
        '''

        map_obj.get_root().html.add_child(folium.Element(legend_html))

    def add_custom_javascript(self, map_obj):
        """Add custom JavaScript for enhanced interactivity"""

        custom_js = '''
        <script>
        // Add custom map interactions
        document.addEventListener('DOMContentLoaded', function() {
            // Add opacity controls for layers
            var layerControl = document.querySelector('.leaflet-control-layers');
            if (layerControl) {
                layerControl.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
                layerControl.style.color = 'white';
            }

            // Enhance popup styling
            var style = document.createElement('style');
            style.innerHTML = `
                .leaflet-popup-content-wrapper {
                    background-color: rgba(0, 0, 0, 0.9);
                    color: white;
                    border-radius: 8px;
                }
                .leaflet-popup-tip {
                    background-color: rgba(0, 0, 0, 0.9);
                }
                .leaflet-control-layers {
                    background-color: rgba(0, 0, 0, 0.8) !important;
                    color: white !important;
                }
                .leaflet-control-layers label {
                    color: white !important;
                }
            `;
            document.head.appendChild(style);
        });
        </script>
        '''

        map_obj.get_root().html.add_child(folium.Element(custom_js))

    def create_heat_map_layer(self, illness_type, date_range=None, borough_filter=None):
        """Create heat map layer for specific illness type"""

        from folium.plugins import HeatMap

        try:
            conn = sqlite3.connect(self.db_path)
            heat_data = []

            if illness_type == 'COVID-19':
                # Get COVID case data with coordinates
                query = """
                    SELECT 'Bronx' as borough, BX_CASE_COUNT as cases
                    FROM nyc_covid_data WHERE BX_CASE_COUNT IS NOT NULL
                    UNION ALL
                    SELECT 'Brooklyn' as borough, BK_CASE_COUNT as cases
                    FROM nyc_covid_data WHERE BK_CASE_COUNT IS NOT NULL
                    UNION ALL
                    SELECT 'Manhattan' as borough, MN_CASE_COUNT as cases
                    FROM nyc_covid_data WHERE MN_CASE_COUNT IS NOT NULL
                    UNION ALL
                    SELECT 'Queens' as borough, QN_CASE_COUNT as cases
                    FROM nyc_covid_data WHERE QN_CASE_COUNT IS NOT NULL
                    UNION ALL
                    SELECT 'Staten Island' as borough, SI_CASE_COUNT as cases
                    FROM nyc_covid_data WHERE SI_CASE_COUNT IS NOT NULL
                """

                df = pd.read_sql_query(query, conn)

                borough_coords = {
                    'Bronx': [40.8448, -73.8648],
                    'Brooklyn': [40.6782, -73.9442],
                    'Manhattan': [40.7831, -73.9712],
                    'Queens': [40.7282, -73.7949],
                    'Staten Island': [40.5795, -74.1502]
                }

                for _, row in df.iterrows():
                    borough = row['borough']
                    cases = float(row['cases']) if pd.notna(row['cases']) else 0

                    if borough in borough_coords and cases > 0:
                        coords = borough_coords[borough]
                        # Normalize case count for heat map intensity
                        intensity = min(1.0, cases / 1000)  # Adjust scaling as needed
                        heat_data.append([coords[0], coords[1], intensity])

            elif illness_type == 'Flu':
                # Get flu data with ZIP code coordinates
                query = """
                    SELECT zip_code, borough, AVG(flu_percentage) as avg_flu_rate
                    FROM flu_surveillance_data
                    GROUP BY zip_code, borough
                    HAVING avg_flu_rate > 0
                """

                df = pd.read_sql_query(query, conn)

                for _, row in df.iterrows():
                    zip_code = row['zip_code']
                    borough = row['borough']
                    flu_rate = float(row['avg_flu_rate']) if pd.notna(row['avg_flu_rate']) else 0

                    coords = self.get_zip_coordinates(zip_code, borough)
                    if coords and flu_rate > 0:
                        intensity = min(1.0, flu_rate / 50)  # Normalize flu rate
                        heat_data.append([coords[0], coords[1], intensity])

            conn.close()

            if heat_data:
                heat_layer = folium.FeatureGroup(name=f'{illness_type} Heat Map', show=False)
                HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(heat_layer)
                return heat_layer
            else:
                return None

        except Exception as e:
            print(f"Error creating heat map for {illness_type}: {e}")
            return None

    def export_map_data(self, illness_filters=None, date_range=None, borough_filter=None):
        """Export filtered map data as JSON for API endpoints"""

        try:
            conn = sqlite3.connect(self.db_path)
            export_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'filters': {
                        'illness_types': illness_filters,
                        'date_range': date_range,
                        'borough': borough_filter
                    }
                },
                'layers': {}
            }

            # Export each illness type data
            if not illness_filters or 'COVID-19' in illness_filters:
                covid_data = self.get_covid_export_data(conn, date_range, borough_filter)
                if covid_data:
                    export_data['layers']['COVID-19'] = covid_data

            if not illness_filters or 'Flu' in illness_filters:
                flu_data = self.get_flu_export_data(conn, date_range, borough_filter)
                if flu_data:
                    export_data['layers']['Flu'] = flu_data

            # Add other illness types...

            conn.close()
            return export_data

        except Exception as e:
            print(f"Error exporting map data: {e}")
            return None

    def get_covid_export_data(self, conn, date_range=None, borough_filter=None):
        """Get COVID data for export"""

        query = """
            SELECT date_of_interest,
                   'Bronx' as borough, BX_CASE_COUNT as cases, BX_HOSPITALIZED_COUNT as hospitalizations
            FROM nyc_covid_data WHERE BX_CASE_COUNT IS NOT NULL
            UNION ALL
            SELECT date_of_interest,
                   'Brooklyn' as borough, BK_CASE_COUNT as cases, BK_HOSPITALIZED_COUNT as hospitalizations
            FROM nyc_covid_data WHERE BK_CASE_COUNT IS NOT NULL
            UNION ALL
            SELECT date_of_interest,
                   'Manhattan' as borough, MN_CASE_COUNT as cases, MN_HOSPITALIZED_COUNT as hospitalizations
            FROM nyc_covid_data WHERE MN_CASE_COUNT IS NOT NULL
            UNION ALL
            SELECT date_of_interest,
                   'Queens' as borough, QN_CASE_COUNT as cases, QN_HOSPITALIZED_COUNT as hospitalizations
            FROM nyc_covid_data WHERE QN_CASE_COUNT IS NOT NULL
            UNION ALL
            SELECT date_of_interest,
                   'Staten Island' as borough, SI_CASE_COUNT as cases, SI_HOSPITALIZED_COUNT as hospitalizations
            FROM nyc_covid_data WHERE SI_CASE_COUNT IS NOT NULL
        """

        if date_range:
            query += f" AND date_of_interest >= '{date_range[0]}' AND date_of_interest <= '{date_range[1]}'"

        if borough_filter:
            query += f" AND borough = '{borough_filter}'"

        df = pd.read_sql_query(query, conn)

        if not df.empty:
            return df.to_dict('records')
        return None

    def get_flu_export_data(self, conn, date_range=None, borough_filter=None):
        """Get flu data for export"""

        query = """
            SELECT date, zip_code, borough, flu_percentage, flu_like_visits, total_ed_visits
            FROM flu_surveillance_data
            WHERE 1=1
        """

        if date_range:
            query += f" AND date >= '{date_range[0]}' AND date <= '{date_range[1]}'"

        if borough_filter:
            query += f" AND borough = '{borough_filter}'"

        df = pd.read_sql_query(query, conn)

        if not df.empty:
            return df.to_dict('records')
        return None

# Example usage and testing
if __name__ == "__main__":
    print("🗺️ Testing Advanced Map System...")

    # Create map system
    map_system = AdvancedMapSystem()

    # Create multi-layer map
    advanced_map = map_system.create_multi_layer_map()

    if advanced_map:
        # Save map
        advanced_map.save('advanced_health_map.html')
        print("✅ Advanced multi-layer map created: advanced_health_map.html")
    else:
        print("❌ Failed to create advanced map")
