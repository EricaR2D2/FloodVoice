#!/usr/bin/env python3
"""
Choropleth Map System for Public Health MVP
Creates maps with actual ZIP code boundaries showing health data as filled areas
"""

import folium
import pandas as pd
import sqlite3
import json
import os
from datetime import datetime, timedelta
import numpy as np

class ChoroplethMapSystem:
    """Advanced mapping system with ZIP code boundary visualization"""
    
    def __init__(self, db_path="public_health_data.db"):
        self.db_path = db_path
        self.map_center = [40.7831, -73.9712]  # NYC center
        self.default_zoom = 10
        
        # Load NYC ZIP code boundaries
        self.zip_boundaries = self.load_zip_boundaries()
        
        # Bright, colorful schemes for different illness types (light theme)
        self.illness_colors = {
            'COVID-19': ['#FFE5E5', '#FFB3B3', '#FF8080', '#FF4D4D', '#FF1A1A', '#E60000', '#CC0000'],
            'Flu': ['#E5F9FF', '#B3F0FF', '#80E7FF', '#4DDDFF', '#1AD4FF', '#00BFFF', '#0099CC'],
            'Foodborne': ['#E5F3FF', '#B3E0FF', '#80CCFF', '#4DB8FF', '#1AA3FF', '#0080FF', '#0066CC'],
            'Air Quality': ['#F0FFF0', '#D4F4D4', '#B8E8B8', '#9CDD9C', '#80D180', '#64C564', '#4CAF4C'],
            'Hospital ER': ['#F5E5FF', '#E6B3FF', '#D680FF', '#C74DFF', '#B81AFF', '#9900E6', '#7A00B8'],
            'Tick Disease': ['#FFF5E5', '#FFE6B3', '#FFD680', '#FFC74D', '#FFB81A', '#FFA500', '#E6940A']
        }
        
        # Risk level colors
        self.risk_colors = {
            'LOW': '#48BB78',      # Green
            'MEDIUM': '#ED8936',   # Orange  
            'HIGH': '#E53E3E',     # Red
            'HAZARDOUS': '#805AD5' # Purple
        }
    
    def load_zip_boundaries(self):
        """Load NYC ZIP code boundaries from GeoJSON file"""

        try:
            # Try the correct filename first
            geojson_path = os.path.join('static', 'nyc_zipcodes.geojson')

            if os.path.exists(geojson_path):
                with open(geojson_path, 'r') as f:
                    zip_data = json.load(f)

                print(f"✅ Loaded ZIP code boundaries: {len(zip_data['features'])} ZIP codes")
                return zip_data
            else:
                # Fallback to alternative filename
                geojson_path = os.path.join('static', 'ny_zip_codes.geojson')
                if os.path.exists(geojson_path):
                    with open(geojson_path, 'r') as f:
                        zip_data = json.load(f)

                    print(f"✅ Loaded ZIP code boundaries: {len(zip_data['features'])} ZIP codes")
                    return zip_data
                else:
                    print(f"❌ ZIP code boundaries file not found: {geojson_path}")
                    return None

        except Exception as e:
            print(f"❌ Error loading ZIP code boundaries: {e}")
            return None
    
    def extract_zip_code(self, feature):
        """Extract ZIP code from feature properties, handling both ZCTA5CE10 and MODZCTA"""
        props = feature['properties']
        return props.get('ZCTA5CE10') or props.get('MODZCTA') or ''

    def filter_nyc_zip_codes(self, borough=None, zip_code=None):
        """Filter NYC ZIP codes by borough and/or specific ZIP code

        Args:
            borough (str, optional): Borough name to filter by (case-insensitive)
            zip_code (str, optional): Specific ZIP code to filter by

        Returns:
            dict: Valid GeoJSON FeatureCollection with filtered features
        """

        print(f"🔍 FILTERING GEOJSON DATA:")
        print(f"   Borough filter: {borough}")
        print(f"   ZIP code filter: {zip_code}")

        # 1. Start with a copy of the full, original GeoJSON data
        if not self.zip_boundaries:
            print(f"   ⚠️ No zip_boundaries data available!")
            return None

        # 2. If both filters are None/empty, return deep copy of original data
        if not borough and not zip_code:
            print(f"   No filters applied - returning full dataset")
            import copy
            result = copy.deepcopy(self.zip_boundaries)
            print(f"   Returned {len(result.get('features', []))} features (unfiltered)")
            return result

        # 3. Apply filters to the features list
        print(f"   Applying filters to {len(self.zip_boundaries.get('features', []))} features...")
        filtered_features = self.zip_boundaries['features']

        # Filter by borough if provided
        if borough:
            print(f"   Filtering by borough: {borough}")
            borough_filtered = []
            for feature in filtered_features:
                feature_borough = feature.get('properties', {}).get('boro_name', '')
                if feature_borough.lower() == borough.lower():
                    borough_filtered.append(feature)
            filtered_features = borough_filtered
            print(f"   After borough filter: {len(filtered_features)} features")

        # Filter by ZIP code if provided
        if zip_code:
            print(f"   Filtering by ZIP code: {zip_code}")
            zip_filtered = []
            for feature in filtered_features:
                feature_zip = feature.get('properties', {}).get('MODZCTA', '')
                if str(feature_zip) == str(zip_code):
                    zip_filtered.append(feature)
            filtered_features = zip_filtered
            print(f"   After ZIP code filter: {len(filtered_features)} features")

        # 4. Construct and return new, valid GeoJSON dictionary
        result = {}

        # Copy all original top-level keys
        for key, value in self.zip_boundaries.items():
            if key != 'features':
                result[key] = value

        # Set the filtered features
        result['features'] = filtered_features

        print(f"   ✅ Final filtered result: {len(filtered_features)} features")
        print(f"   Result keys: {list(result.keys())}")

        return result
    
    def create_choropleth_map(self, illness_type, date_range=None, borough_filter=None):
        """Create a choropleth map showing illness data by ZIP code boundaries"""

        print(f"🗺️ Creating choropleth map for {illness_type}...")

        # Create base map centered on NYC with light, colorful theme
        m = folium.Map(
            location=self.map_center,
            zoom_start=self.default_zoom,
            tiles=None
        )

        # Add bright, colorful tile layer
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            name='Light Theme',
            overlay=False,
            control=True
        ).add_to(m)

        # Fetch health data into DataFrame
        df = self.get_illness_data_by_zip(illness_type, date_range, borough_filter)

        # Check if DataFrame is empty
        if df.empty:
            print(f"⚠️ No data found for {illness_type} with current filters")
            print(f"   Filters: date_range={date_range}, borough={borough_filter}")
            print(f"   Creating base map with ZIP code boundaries only...")

            # Do NOT attempt to create folium.Choropleth layer
            # Instead, create base map with only GeoJSON boundaries
            if self.zip_boundaries:
                nyc_boundaries = self.filter_nyc_zip_codes(borough=borough_filter)
                if nyc_boundaries:
                    # Add base GeoJSON layer of all ZIP code boundaries
                    folium.GeoJson(
                        nyc_boundaries,
                        style_function=lambda feature: {
                            'fillColor': '#F8F9FA',      # Very light gray fill
                            'color': '#6C757D',          # Medium gray border
                            'weight': 1.5,
                            'fillOpacity': 0.2,          # Low opacity so boundaries are subtle
                            'opacity': 0.8
                        },
                        popup=folium.GeoJsonPopup(
                            fields=['MODZCTA'],
                            aliases=['ZIP Code:'],
                            localize=True,
                            labels=True,
                            style="background-color: rgba(0,0,0,0.8); color: white; padding: 8px;",
                        ),
                        tooltip=folium.GeoJsonTooltip(
                            fields=['MODZCTA'],
                            aliases=['ZIP Code:'],
                            localize=True,
                            sticky=True,
                            labels=True,
                            style="""
                                background-color: rgba(0,0,0,0.8);
                                border: 2px solid white;
                                border-radius: 3px;
                                color: white;
                                padding: 5px;
                            """,
                            max_width=200,
                        )
                    ).add_to(m)

                    # Add a message overlay indicating no data
                    no_data_html = f"""
                    <div style="position: fixed;
                                top: 10px; left: 50px; width: 300px; height: 80px;
                                background-color: rgba(255, 255, 255, 0.9);
                                border: 2px solid #FFC107;
                                border-radius: 5px;
                                padding: 10px;
                                font-family: Arial, sans-serif;
                                font-size: 14px;
                                z-index: 9999;">
                        <strong>⚠️ No Data Available</strong><br>
                        No {illness_type} data found for the selected filters.<br>
                        Showing ZIP code boundaries only.
                    </div>
                    """
                    m.get_root().html.add_child(folium.Element(no_data_html))

            print(f"✅ Base choropleth map created for {illness_type} (no data available)")
            return m

        # DataFrame is NOT empty - proceed with existing logic to create choropleth
        print(f"📊 Found {len(df)} data points for {illness_type}")

        if self.zip_boundaries:
            # Filter to NYC ZIP codes only
            nyc_boundaries = self.filter_nyc_zip_codes(borough=borough_filter)

            if nyc_boundaries:
                # Create choropleth layer with actual data
                self.add_choropleth_layer(m, nyc_boundaries, df, illness_type)

                # Add legend
                self.add_choropleth_legend(m, illness_type, df)

                # Add data summary
                self.add_data_summary(m, df, illness_type)

        print(f"✅ Choropleth map created for {illness_type} with data visualization")
        return m
    
    def get_illness_data_by_zip(self, illness_type, date_range=None, borough_filter=None, zip_code_filter=None):
        """Get illness data aggregated by ZIP code"""
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            if illness_type == 'COVID-19':
                # Get COVID data by borough (we'll map to ZIP codes)
                query = """
                    SELECT 'Bronx' as area, SUM(BX_CASE_COUNT) as value, 'Cases' as metric
                    FROM nyc_covid_data WHERE BX_CASE_COUNT IS NOT NULL
                    UNION ALL
                    SELECT 'Brooklyn' as area, SUM(BK_CASE_COUNT) as value, 'Cases' as metric
                    FROM nyc_covid_data WHERE BK_CASE_COUNT IS NOT NULL
                    UNION ALL
                    SELECT 'Manhattan' as area, SUM(MN_CASE_COUNT) as value, 'Cases' as metric
                    FROM nyc_covid_data WHERE MN_CASE_COUNT IS NOT NULL
                    UNION ALL
                    SELECT 'Queens' as area, SUM(QN_CASE_COUNT) as value, 'Cases' as metric
                    FROM nyc_covid_data WHERE QN_CASE_COUNT IS NOT NULL
                    UNION ALL
                    SELECT 'Staten Island' as area, SUM(SI_CASE_COUNT) as value, 'Cases' as metric
                    FROM nyc_covid_data WHERE SI_CASE_COUNT IS NOT NULL
                """
                
                df = pd.read_sql_query(query, conn)
                # Map borough data to representative ZIP codes
                df = self.map_borough_to_zip_codes(df)
                
            elif illness_type == 'Flu':
                query = """
                    SELECT zip_code as area, 
                           AVG(flu_percentage) as value,
                           'Flu Rate %' as metric
                    FROM flu_surveillance_data
                    WHERE 1=1
                """
                
                if date_range:
                    query += f" AND date >= '{date_range[0]}' AND date <= '{date_range[1]}'"
                
                if borough_filter:
                    query += f" AND borough = '{borough_filter}'"
                
                query += " GROUP BY zip_code HAVING COUNT(*) > 5"
                
                df = pd.read_sql_query(query, conn)
                
            elif illness_type == 'Foodborne':
                query = """
                    SELECT zip_code as area,
                           foodborne_risk_score as value,
                           'Risk Score' as metric
                    FROM foodborne_illness_risk_summary
                    WHERE 1=1
                """
                
                if borough_filter:
                    query += f" AND borough = '{borough_filter}'"
                
                df = pd.read_sql_query(query, conn)
                
            elif illness_type == 'Air Quality':
                query = """
                    SELECT zip_code as area,
                           air_quality_score as value,
                           'AQI Score' as metric
                    FROM air_quality_summary
                    WHERE zip_code IS NOT NULL AND zip_code != ''
                """
                
                if borough_filter:
                    query += f" AND borough = '{borough_filter}'"
                
                df = pd.read_sql_query(query, conn)
                
            elif illness_type == 'Hospital ER':
                query = """
                    SELECT zip_code as area,
                           AVG(respiratory_percentage) as value,
                           'Respiratory %' as metric
                    FROM real_hospital_data
                    WHERE 1=1
                """
                
                if date_range:
                    query += f" AND date >= '{date_range[0]}' AND date <= '{date_range[1]}'"
                
                if borough_filter:
                    query += f" AND borough = '{borough_filter}'"
                
                query += " GROUP BY zip_code"
                
                df = pd.read_sql_query(query, conn)
                
            elif illness_type == 'Tick Disease':
                query = """
                    SELECT zip_code as area,
                           total_cases as value,
                           'Total Cases' as metric
                    FROM real_tick_disease_summary
                    WHERE 1=1
                """
                
                if borough_filter:
                    query += f" AND borough = '{borough_filter}'"
                
                df = pd.read_sql_query(query, conn)
            
            else:
                df = pd.DataFrame()
            
            conn.close()
            
            # Clean and validate data
            if not df.empty:
                df['area'] = df['area'].astype(str)
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df = df.dropna(subset=['value'])
                df = df[df['value'] > 0]  # Remove zero values
                
                print(f"📊 Loaded {len(df)} records for {illness_type}")
            
            return df
            
        except Exception as e:
            print(f"❌ Error getting illness data: {e}")
            return pd.DataFrame()
    
    def map_borough_to_zip_codes(self, borough_df):
        """Map borough-level data to representative ZIP codes"""
        
        # Representative ZIP codes for each borough
        borough_zip_mapping = {
            'Bronx': ['10451', '10452', '10453', '10454', '10455', '10456', '10457', '10458', '10459', '10460'],
            'Brooklyn': ['11201', '11203', '11204', '11205', '11206', '11207', '11208', '11209', '11210', '11211'],
            'Manhattan': ['10001', '10002', '10003', '10004', '10005', '10006', '10007', '10009', '10010', '10011'],
            'Queens': ['11101', '11102', '11103', '11104', '11105', '11106', '11354', '11355', '11356', '11357'],
            'Staten Island': ['10301', '10302', '10303', '10304', '10305', '10306', '10307', '10308', '10309', '10310']
        }
        
        zip_data = []
        
        for _, row in borough_df.iterrows():
            borough = row['area']
            value = row['value']
            metric = row['metric']
            
            if borough in borough_zip_mapping:
                # Distribute the borough value across its ZIP codes with some variation
                zip_codes = borough_zip_mapping[borough]
                base_value = value / len(zip_codes)
                
                for i, zip_code in enumerate(zip_codes):
                    # Add realistic variation (±20%)
                    variation = np.random.uniform(0.8, 1.2)
                    zip_value = base_value * variation
                    
                    zip_data.append({
                        'area': zip_code,
                        'value': zip_value,
                        'metric': metric
                    })
        
        return pd.DataFrame(zip_data)
    
    def add_choropleth_layer(self, map_obj, boundaries, data, illness_type):
        """Add choropleth layer to the map"""
        
        # Create a dictionary for quick data lookup
        data_dict = dict(zip(data['area'].astype(str), data['value']))
        
        # Calculate value ranges for color scaling
        values = data['value'].values
        if len(values) > 0:
            min_val = np.min(values)
            max_val = np.max(values)
            
            # Create color scale
            colors = self.illness_colors.get(illness_type, self.illness_colors['COVID-19'])
            
            def get_color(zip_code):
                value = data_dict.get(str(zip_code), 0)
                if value == 0:
                    return '#E2E8F0'  # Light gray for no data
                
                # Normalize value to 0-1 range
                normalized = (value - min_val) / (max_val - min_val) if max_val > min_val else 0
                
                # Map to color index
                color_index = min(int(normalized * (len(colors) - 1)), len(colors) - 1)
                return colors[color_index]
            
            def style_function(feature):
                zip_code = self.extract_zip_code(feature)
                color = get_color(zip_code)

                return {
                    'fillColor': color,
                    'color': '#2C3E50',  # Dark blue-gray border for contrast
                    'weight': 2,
                    'fillOpacity': 0.8,
                    'opacity': 1.0
                }
            
            def highlight_function(feature):
                return {
                    'fillColor': '#FFD700',  # Gold highlight
                    'color': '#2D3748',
                    'weight': 3,
                    'fillOpacity': 0.9,
                    'opacity': 1.0
                }
            
            # Add choropleth layer
            choropleth = folium.GeoJson(
                boundaries,
                style_function=style_function,
                highlight_function=highlight_function,
                popup=folium.GeoJsonPopup(
                    fields=['MODZCTA'],
                    aliases=['ZIP Code:'],
                    localize=True,
                    labels=True,
                    style="background-color: rgba(0,0,0,0.8); color: white;",
                ),
                tooltip=folium.GeoJsonTooltip(
                    fields=['MODZCTA'],
                    aliases=[f'{illness_type} - ZIP Code:'],
                    localize=True,
                    sticky=True,
                    labels=True,
                    style="""
                        background-color: rgba(0,0,0,0.9);
                        border: 2px solid white;
                        border-radius: 8px;
                        color: white;
                        padding: 10px;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        font-size: 12px;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    """,
                    max_width=250,
                )
            )
            
            choropleth.add_to(map_obj)
            
            # Add custom popups with health data
            self.add_custom_popups(map_obj, boundaries, data_dict, illness_type)
    
    def add_custom_popups(self, map_obj, boundaries, data_dict, illness_type):
        """Add custom popups with detailed health information"""

        for feature in boundaries['features']:
            zip_code = self.extract_zip_code(feature)
            value = data_dict.get(str(zip_code), 0)

            # Get additional data for this ZIP code
            additional_data = self.get_zip_code_details(zip_code, illness_type)

            if value > 0 or additional_data:  # Show popup even if current illness has no data but other data exists
                # Calculate centroid of ZIP code for popup placement
                coords = feature['geometry']['coordinates']
                if feature['geometry']['type'] == 'Polygon':
                    coords = coords[0]
                elif feature['geometry']['type'] == 'MultiPolygon':
                    coords = coords[0][0]

                # Simple centroid calculation
                lats = [coord[1] for coord in coords]
                lons = [coord[0] for coord in coords]
                center_lat = sum(lats) / len(lats)
                center_lon = sum(lons) / len(lons)

                # Determine risk level based on value
                risk_level = self.determine_risk_level(value, illness_type)
                risk_color = self.get_risk_color(risk_level)

                # Create comprehensive popup content
                popup_html = f"""
                <div style="width: 320px; background-color: rgba(255,255,255,0.98); color: #2C3E50; padding: 18px; border-radius: 10px; border: 3px solid {self.illness_colors[illness_type][4]}; box-shadow: 0 6px 12px rgba(0,0,0,0.15); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                    <h4 style="color: {self.illness_colors[illness_type][5]}; margin-top: 0; margin-bottom: 15px; font-weight: bold; border-bottom: 2px solid {self.illness_colors[illness_type][4]}; padding-bottom: 8px;">
                        <i class="fas fa-map-marker-alt"></i> ZIP Code {zip_code}
                    </h4>

                    <div style="margin-bottom: 12px;">
                        <p style="margin: 4px 0; font-weight: 600;"><i class="fas fa-building"></i> <strong>Borough:</strong> {additional_data.get('borough', 'Unknown')}</p>
                        <p style="margin: 4px 0; font-weight: 600;"><i class="fas fa-calendar"></i> <strong>Last Updated:</strong> {additional_data.get('last_updated', 'N/A')}</p>
                    </div>

                    <div style="background-color: rgba(52, 152, 219, 0.1); padding: 12px; border-radius: 6px; margin-bottom: 12px;">
                        <p style="margin: 4px 0; font-weight: 600; color: {self.illness_colors[illness_type][5]};"><strong>{illness_type} Data:</strong></p>
                        <p style="font-size: 1.4em; color: {self.illness_colors[illness_type][6]}; font-weight: bold; margin: 8px 0;">
                            {value:.1f} {self.get_unit_label(illness_type)}
                        </p>
                        <p style="margin: 4px 0; font-size: 0.9em;">
                            <span style="background-color: {risk_color}; color: white; padding: 2px 8px; border-radius: 12px; font-weight: bold;">
                                {risk_level} RISK
                            </span>
                        </p>
                    </div>

                    <div style="background-color: rgba(236, 240, 241, 0.8); padding: 10px; border-radius: 6px; margin-bottom: 10px;">
                        <p style="margin: 3px 0; font-size: 0.9em;"><strong>Total Cases Reported:</strong> {additional_data.get('total_cases', 'N/A')}</p>
                        <p style="margin: 3px 0; font-size: 0.9em;"><strong>Population Density:</strong> {additional_data.get('population_density', 'N/A')}</p>
                        <p style="margin: 3px 0; font-size: 0.9em;"><strong>Active Alerts:</strong> {additional_data.get('active_alerts', 0)}</p>
                    </div>

                    <p style="font-size: 0.85em; color: #7F8C8D; margin-bottom: 0; text-align: center; font-style: italic;">
                        <i class="fas fa-info-circle"></i> Click for detailed analysis and trends
                    </p>
                </div>
                """

                # Add invisible marker for popup
                folium.Marker(
                    location=[center_lat, center_lon],
                    popup=folium.Popup(popup_html, max_width=350),
                    icon=folium.Icon(color='blue', icon='info-sign', prefix='fa'),
                    opacity=0  # Make marker invisible
                ).add_to(map_obj)

    def add_choropleth_legend(self, map_obj, illness_type, data):
        """Add color legend for choropleth map"""

        if data.empty:
            return

        colors = self.illness_colors.get(illness_type, self.illness_colors['COVID-19'])
        min_val = data['value'].min()
        max_val = data['value'].max()
        metric = data['metric'].iloc[0] if not data.empty else 'Value'

        legend_html = f'''
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 220px; height: auto;
                    background-color: rgba(255, 255, 255, 0.95); border:3px solid {colors[4]}; z-index:9999;
                    font-size:14px; color: #2C3E50; padding: 18px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h4 style="margin-top:0; color: {colors[5]}; font-weight: bold;">{illness_type}</h4>
        <p style="margin: 8px 0; font-size: 13px; font-weight: 600; color: #34495E;">{metric}</p>
        '''

        # Create color gradient legend
        for i, color in enumerate(colors):
            if i == 0:
                value_range = f"{min_val:.1f}"
            elif i == len(colors) - 1:
                value_range = f"{max_val:.1f}"
            else:
                range_val = min_val + (max_val - min_val) * (i / (len(colors) - 1))
                value_range = f"{range_val:.1f}"

            legend_html += f'''
            <p style="margin: 5px 0; font-weight: 500;">
                <span style="background-color: {color}; width: 22px; height: 16px; display: inline-block; margin-right: 8px; border: 2px solid #2C3E50; border-radius: 3px;"></span>
                {value_range}
            </p>
            '''

        legend_html += '''
        <p style="margin: 10px 0 0 0; font-size: 12px; color: #7F8C8D; font-weight: 500;">
            <span style="background-color: #E2E8F0; width: 22px; height: 16px; display: inline-block; margin-right: 8px; border: 2px solid #2C3E50; border-radius: 3px;"></span>
            No Data
        </p>
        </div>
        '''

        map_obj.get_root().html.add_child(folium.Element(legend_html))

    def add_data_summary(self, map_obj, data, illness_type):
        """Add data summary panel to the map"""

        if data.empty:
            return

        total_areas = len(data)
        avg_value = data['value'].mean()
        max_value = data['value'].max()
        min_value = data['value'].min()
        metric = data['metric'].iloc[0] if not data.empty else 'Value'

        summary_html = f'''
        <div style="position: fixed;
                    top: 10px; right: 10px; width: 280px; height: auto;
                    background-color: rgba(255, 255, 255, 0.95); border:3px solid {self.illness_colors[illness_type][4]}; z-index:9999;
                    font-size:14px; color: #2C3E50; padding: 18px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h4 style="margin-top:0; color: {self.illness_colors[illness_type][5]}; font-weight: bold;">
            <i class="fas fa-chart-bar"></i> {illness_type} Summary
        </h4>
        <p style="margin: 10px 0; font-weight: 600;"><strong>Areas with Data:</strong> <span style="color: {self.illness_colors[illness_type][5]};">{total_areas}</span></p>
        <p style="margin: 10px 0; font-weight: 600;"><strong>Average {metric}:</strong> <span style="color: {self.illness_colors[illness_type][5]};">{avg_value:.1f}</span></p>
        <p style="margin: 10px 0; font-weight: 600;"><strong>Highest {metric}:</strong> <span style="color: {self.illness_colors[illness_type][6]};">{max_value:.1f}</span></p>
        <p style="margin: 10px 0; font-weight: 600;"><strong>Lowest {metric}:</strong> <span style="color: {self.illness_colors[illness_type][3]};">{min_value:.1f}</span></p>
        <hr style="border-color: {self.illness_colors[illness_type][4]}; margin: 12px 0; border-width: 2px;">
        <p style="margin: 8px 0; font-size: 13px; color: #7F8C8D; font-weight: 500;">
            <i class="fas fa-info-circle"></i> Hover over areas for details
        </p>
        </div>
        '''

        map_obj.get_root().html.add_child(folium.Element(summary_html))

    def create_multi_illness_choropleth(self, illness_types, date_range=None, borough_filter=None):
        """Create a map with multiple illness types as separate layers"""

        print(f"🗺️ Creating multi-illness choropleth map...")

        # Create base map
        m = folium.Map(
            location=self.map_center,
            zoom_start=self.default_zoom,
            tiles=None
        )

        # Add dark theme tile layer
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            name='Dark Theme',
            overlay=False,
            control=True
        ).add_to(m)

        # Add each illness type as a separate layer
        for illness_type in illness_types:
            illness_data = self.get_illness_data_by_zip(illness_type, date_range, borough_filter)

            if not illness_data.empty and self.zip_boundaries:
                nyc_boundaries = self.filter_nyc_zip_codes(borough=borough_filter)

                if nyc_boundaries:
                    # Create feature group for this illness type
                    feature_group = folium.FeatureGroup(name=f'{illness_type} Choropleth', show=True)

                    # Add choropleth to feature group
                    self.add_choropleth_to_group(feature_group, nyc_boundaries, illness_data, illness_type)

                    # Add feature group to map
                    feature_group.add_to(m)

        # Add layer control
        folium.LayerControl(collapsed=False).add_to(m)

        # Add multi-illness legend
        self.add_multi_illness_legend(m, illness_types)

        print(f"✅ Multi-illness choropleth map created with {len(illness_types)} illness types")
        return m

    def add_choropleth_to_group(self, feature_group, boundaries, data, illness_type):
        """Add choropleth layer to a feature group"""

        # Create data dictionary
        data_dict = dict(zip(data['area'].astype(str), data['value']))

        # Calculate value ranges
        values = data['value'].values
        if len(values) > 0:
            min_val = np.min(values)
            max_val = np.max(values)
            colors = self.illness_colors.get(illness_type, self.illness_colors['COVID-19'])

            def get_color(zip_code):
                value = data_dict.get(str(zip_code), 0)
                if value == 0:
                    return '#E2E8F0'

                normalized = (value - min_val) / (max_val - min_val) if max_val > min_val else 0
                color_index = min(int(normalized * (len(colors) - 1)), len(colors) - 1)
                return colors[color_index]

            def style_function(feature):
                zip_code = self.extract_zip_code(feature)
                color = get_color(zip_code)

                return {
                    'fillColor': color,
                    'color': '#2D3748',
                    'weight': 1,
                    'fillOpacity': 0.6,
                    'opacity': 1.0
                }

            # Add choropleth to feature group
            folium.GeoJson(
                boundaries,
                style_function=style_function,
                popup=folium.GeoJsonPopup(
                    fields=['MODZCTA'],
                    aliases=[f'ZIP Code ({illness_type}):'],
                    localize=True,
                    labels=True,
                    style="background-color: rgba(0,0,0,0.8); color: white;",
                ),
                tooltip=folium.GeoJsonTooltip(
                    fields=['MODZCTA'],
                    aliases=[f'{illness_type} - ZIP Code:'],
                    localize=True,
                    sticky=True,
                    labels=True,
                    style="""
                        background-color: rgba(0,0,0,0.9);
                        color: white;
                        border-radius: 8px;
                        padding: 10px;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        font-size: 12px;
                        border: 2px solid white;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                    """,
                    max_width=250,
                )
            ).add_to(feature_group)

    def add_multi_illness_legend(self, map_obj, illness_types):
        """Add legend for multiple illness types"""

        legend_html = '''
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 220px; height: auto;
                    background-color: rgba(0, 0, 0, 0.8); border:2px solid grey; z-index:9999;
                    font-size:14px; color: white; padding: 15px; border-radius: 5px;">
        <h4 style="margin-top:0; color: #fff;">
            <i class="fas fa-layer-group"></i> Health Data Layers
        </h4>
        '''

        for illness_type in illness_types:
            colors = self.illness_colors.get(illness_type, self.illness_colors['COVID-19'])
            main_color = colors[4]  # Use middle color as representative

            legend_html += f'''
            <p style="margin: 8px 0;">
                <span style="background-color: {main_color}; width: 20px; height: 15px; display: inline-block; margin-right: 8px; border: 1px solid #666; border-radius: 2px;"></span>
                {illness_type}
            </p>
            '''

        legend_html += '''
        <hr style="border-color: #666; margin: 10px 0;">
        <p style="margin: 5px 0; font-size: 12px; color: #CBD5E0;">
            <i class="fas fa-eye"></i> Use layer control to toggle visibility
        </p>
        <p style="margin: 5px 0; font-size: 12px; color: #CBD5E0;">
            <i class="fas fa-mouse-pointer"></i> Click areas for details
        </p>
        </div>
        '''

        map_obj.get_root().html.add_child(folium.Element(legend_html))

    def export_choropleth_data(self, illness_type, date_range=None, borough_filter=None):
        """Export choropleth data for API endpoints"""

        illness_data = self.get_illness_data_by_zip(illness_type, date_range, borough_filter)

        if not illness_data.empty:
            return {
                'illness_type': illness_type,
                'data_count': len(illness_data),
                'date_range': date_range,
                'borough_filter': borough_filter,
                'data': illness_data.to_dict('records'),
                'statistics': {
                    'min_value': float(illness_data['value'].min()),
                    'max_value': float(illness_data['value'].max()),
                    'avg_value': float(illness_data['value'].mean()),
                    'total_areas': len(illness_data)
                }
            }

        return None

    def get_zip_code_details(self, zip_code, illness_type):
        """Get additional details for a ZIP code from the database"""

        try:
            conn = sqlite3.connect(self.db_path)

            # Get borough information using ZIP code mapping
            borough = self.get_borough_from_zip(zip_code)

            # Get illness-specific data and last updated date
            total_cases = 0
            last_updated = 'N/A'

            if illness_type == 'COVID-19':
                # Get COVID data for this borough
                borough_col_map = {
                    'Bronx': 'BX_CASE_COUNT',
                    'Brooklyn': 'BK_CASE_COUNT',
                    'Manhattan': 'MN_CASE_COUNT',
                    'Queens': 'QN_CASE_COUNT',
                    'Staten Island': 'SI_CASE_COUNT'
                }

                if borough in borough_col_map:
                    covid_query = f"""
                        SELECT SUM({borough_col_map[borough]}) as total,
                               MAX(date_of_interest) as latest
                        FROM nyc_covid_data
                        WHERE {borough_col_map[borough]} IS NOT NULL
                    """
                    covid_result = pd.read_sql_query(covid_query, conn)
                    if not covid_result.empty:
                        total_cases = int(covid_result.iloc[0]['total'] or 0)
                        last_updated = covid_result.iloc[0]['latest'] or 'N/A'

            elif illness_type == 'Hospital ER':
                # Get hospital data for this ZIP code
                hospital_query = """
                    SELECT SUM(total_visits) as total, MAX(date) as latest
                    FROM real_hospital_data
                    WHERE zip_code = ? AND total_visits IS NOT NULL
                """
                hospital_result = pd.read_sql_query(hospital_query, conn, params=[zip_code])
                if not hospital_result.empty:
                    total_cases = int(hospital_result.iloc[0]['total'] or 0)
                    last_updated = hospital_result.iloc[0]['latest'] or 'N/A'

            elif illness_type == 'Flu':
                # Get flu data for this ZIP code
                flu_query = """
                    SELECT SUM(flu_like_visits) as total, MAX(date) as latest
                    FROM flu_surveillance_data
                    WHERE zip_code = ? AND flu_like_visits IS NOT NULL
                """
                flu_result = pd.read_sql_query(flu_query, conn, params=[zip_code])
                if not flu_result.empty:
                    total_cases = int(flu_result.iloc[0]['total'] or 0)
                    last_updated = flu_result.iloc[0]['latest'] or 'N/A'

            elif illness_type == 'Foodborne':
                # Get foodborne data for this ZIP code
                foodborne_query = """
                    SELECT COUNT(*) as total, MAX(date) as latest
                    FROM restaurant_inspection_data
                    WHERE zip_code = ? AND is_high_risk_foodborne = 1
                """
                foodborne_result = pd.read_sql_query(foodborne_query, conn, params=[zip_code])
                if not foodborne_result.empty:
                    total_cases = int(foodborne_result.iloc[0]['total'] or 0)
                    last_updated = foodborne_result.iloc[0]['latest'] or 'N/A'

            elif illness_type == 'Tick Disease':
                # Get tick disease data for this ZIP code
                tick_query = """
                    SELECT SUM(case_count) as total, MAX(date) as latest
                    FROM tick_disease_data
                    WHERE zip_code = ? AND case_count IS NOT NULL
                """
                tick_result = pd.read_sql_query(tick_query, conn, params=[zip_code])
                if not tick_result.empty:
                    total_cases = int(tick_result.iloc[0]['total'] or 0)
                    last_updated = tick_result.iloc[0]['latest'] or 'N/A'

            elif illness_type == 'Air Quality':
                # Get air quality data for this borough
                air_query = """
                    SELECT AVG(air_quality_score) as avg_score, MAX(data_date) as latest
                    FROM air_quality_summary
                    WHERE borough = ? AND air_quality_score IS NOT NULL
                """
                air_result = pd.read_sql_query(air_query, conn, params=[borough])
                if not air_result.empty:
                    total_cases = int(air_result.iloc[0]['avg_score'] or 0)
                    last_updated = air_result.iloc[0]['latest'] or 'N/A'

            # Get active alerts for this ZIP code
            alerts_query = """
                SELECT COUNT(*) as count FROM pattern_detections
                WHERE zip_code = ? AND detection_timestamp >= datetime('now', '-7 days')
            """
            alerts_result = pd.read_sql_query(alerts_query, conn, params=[zip_code])
            active_alerts = int(alerts_result.iloc[0]['count']) if not alerts_result.empty else 0

            # Get population density estimate based on borough
            population_density = self.get_population_density(borough)

            conn.close()

            return {
                'borough': borough,
                'total_cases': f"{total_cases:,}" if total_cases > 0 else '0',
                'population_density': population_density,
                'active_alerts': active_alerts,
                'last_updated': last_updated
            }

        except Exception as e:
            print(f"Error getting ZIP code details for {zip_code}: {e}")
            return {
                'borough': self.get_borough_from_zip(zip_code),
                'total_cases': '0',
                'population_density': 'Medium',
                'active_alerts': 0,
                'last_updated': 'N/A'
            }

    def determine_risk_level(self, value, illness_type):
        """Determine risk level based on value and illness type"""

        if value == 0:
            return 'LOW'

        # Define thresholds based on illness type
        thresholds = {
            'COVID-19': {'low': 10, 'medium': 50, 'high': 100},
            'Flu': {'low': 5, 'medium': 20, 'high': 50},
            'Foodborne': {'low': 2, 'medium': 10, 'high': 25},
            'Air Quality': {'low': 50, 'medium': 100, 'high': 150},
            'Hospital ER': {'low': 20, 'medium': 100, 'high': 200},
            'Tick Disease': {'low': 1, 'medium': 5, 'high': 15}
        }

        illness_thresholds = thresholds.get(illness_type, {'low': 10, 'medium': 50, 'high': 100})

        if value <= illness_thresholds['low']:
            return 'LOW'
        elif value <= illness_thresholds['medium']:
            return 'MEDIUM'
        elif value <= illness_thresholds['high']:
            return 'HIGH'
        else:
            return 'CRITICAL'

    def get_risk_color(self, risk_level):
        """Get color for risk level"""

        colors = {
            'LOW': '#27AE60',      # Green
            'MEDIUM': '#F39C12',   # Orange
            'HIGH': '#E74C3C',     # Red
            'CRITICAL': '#8E44AD'  # Purple
        }

        return colors.get(risk_level, '#95A5A6')  # Default gray

    def get_unit_label(self, illness_type):
        """Get appropriate unit label for illness type"""

        units = {
            'COVID-19': 'cases',
            'Flu': 'visits',
            'Foodborne': 'incidents',
            'Air Quality': 'AQI',
            'Hospital ER': 'visits',
            'Tick Disease': 'cases'
        }

        return units.get(illness_type, 'cases')

    def get_borough_from_zip(self, zip_code):
        """Get borough name from ZIP code using NYC ZIP code mapping"""

        # NYC ZIP code to borough mapping (major ZIP codes)
        zip_to_borough = {
            # Manhattan
            '10001': 'Manhattan', '10002': 'Manhattan', '10003': 'Manhattan', '10004': 'Manhattan',
            '10005': 'Manhattan', '10006': 'Manhattan', '10007': 'Manhattan', '10009': 'Manhattan',
            '10010': 'Manhattan', '10011': 'Manhattan', '10012': 'Manhattan', '10013': 'Manhattan',
            '10014': 'Manhattan', '10016': 'Manhattan', '10017': 'Manhattan', '10018': 'Manhattan',
            '10019': 'Manhattan', '10020': 'Manhattan', '10021': 'Manhattan', '10022': 'Manhattan',
            '10023': 'Manhattan', '10024': 'Manhattan', '10025': 'Manhattan', '10026': 'Manhattan',
            '10027': 'Manhattan', '10028': 'Manhattan', '10029': 'Manhattan', '10030': 'Manhattan',
            '10031': 'Manhattan', '10032': 'Manhattan', '10033': 'Manhattan', '10034': 'Manhattan',
            '10035': 'Manhattan', '10036': 'Manhattan', '10037': 'Manhattan', '10038': 'Manhattan',
            '10039': 'Manhattan', '10040': 'Manhattan', '10044': 'Manhattan', '10065': 'Manhattan',
            '10075': 'Manhattan', '10128': 'Manhattan', '10280': 'Manhattan', '10282': 'Manhattan',

            # Bronx
            '10451': 'Bronx', '10452': 'Bronx', '10453': 'Bronx', '10454': 'Bronx',
            '10455': 'Bronx', '10456': 'Bronx', '10457': 'Bronx', '10458': 'Bronx',
            '10459': 'Bronx', '10460': 'Bronx', '10461': 'Bronx', '10462': 'Bronx',
            '10463': 'Bronx', '10464': 'Bronx', '10465': 'Bronx', '10466': 'Bronx',
            '10467': 'Bronx', '10468': 'Bronx', '10469': 'Bronx', '10470': 'Bronx',
            '10471': 'Bronx', '10472': 'Bronx', '10473': 'Bronx', '10474': 'Bronx',
            '10475': 'Bronx',

            # Brooklyn
            '11201': 'Brooklyn', '11203': 'Brooklyn', '11204': 'Brooklyn', '11205': 'Brooklyn',
            '11206': 'Brooklyn', '11207': 'Brooklyn', '11208': 'Brooklyn', '11209': 'Brooklyn',
            '11210': 'Brooklyn', '11211': 'Brooklyn', '11212': 'Brooklyn', '11213': 'Brooklyn',
            '11214': 'Brooklyn', '11215': 'Brooklyn', '11216': 'Brooklyn', '11217': 'Brooklyn',
            '11218': 'Brooklyn', '11219': 'Brooklyn', '11220': 'Brooklyn', '11221': 'Brooklyn',
            '11222': 'Brooklyn', '11223': 'Brooklyn', '11224': 'Brooklyn', '11225': 'Brooklyn',
            '11226': 'Brooklyn', '11228': 'Brooklyn', '11229': 'Brooklyn', '11230': 'Brooklyn',
            '11231': 'Brooklyn', '11232': 'Brooklyn', '11233': 'Brooklyn', '11234': 'Brooklyn',
            '11235': 'Brooklyn', '11236': 'Brooklyn', '11237': 'Brooklyn', '11238': 'Brooklyn',
            '11239': 'Brooklyn', '11249': 'Brooklyn', '11252': 'Brooklyn', '11256': 'Brooklyn',

            # Queens
            '11101': 'Queens', '11102': 'Queens', '11103': 'Queens', '11104': 'Queens',
            '11105': 'Queens', '11106': 'Queens', '11109': 'Queens', '11354': 'Queens',
            '11355': 'Queens', '11356': 'Queens', '11357': 'Queens', '11358': 'Queens',
            '11360': 'Queens', '11361': 'Queens', '11362': 'Queens', '11363': 'Queens',
            '11364': 'Queens', '11365': 'Queens', '11366': 'Queens', '11367': 'Queens',
            '11368': 'Queens', '11369': 'Queens', '11370': 'Queens', '11372': 'Queens',
            '11373': 'Queens', '11374': 'Queens', '11375': 'Queens', '11377': 'Queens',
            '11378': 'Queens', '11379': 'Queens', '11385': 'Queens', '11411': 'Queens',
            '11412': 'Queens', '11413': 'Queens', '11414': 'Queens', '11415': 'Queens',
            '11416': 'Queens', '11417': 'Queens', '11418': 'Queens', '11419': 'Queens',
            '11420': 'Queens', '11421': 'Queens', '11422': 'Queens', '11423': 'Queens',
            '11426': 'Queens', '11427': 'Queens', '11428': 'Queens', '11429': 'Queens',
            '11432': 'Queens', '11433': 'Queens', '11434': 'Queens', '11435': 'Queens',
            '11436': 'Queens', '11691': 'Queens', '11692': 'Queens', '11693': 'Queens',
            '11694': 'Queens', '11697': 'Queens',

            # Staten Island
            '10301': 'Staten Island', '10302': 'Staten Island', '10303': 'Staten Island',
            '10304': 'Staten Island', '10305': 'Staten Island', '10306': 'Staten Island',
            '10307': 'Staten Island', '10308': 'Staten Island', '10309': 'Staten Island',
            '10310': 'Staten Island', '10311': 'Staten Island', '10312': 'Staten Island',
            '10313': 'Staten Island', '10314': 'Staten Island'
        }

        return zip_to_borough.get(str(zip_code), 'NYC')

    def get_population_density(self, borough):
        """Get population density description for borough"""

        # NYC borough population densities (approximate)
        density_map = {
            'Manhattan': 'Very High (74,000/sq mi)',
            'Brooklyn': 'High (37,000/sq mi)',
            'Bronx': 'High (34,000/sq mi)',
            'Queens': 'Medium (21,000/sq mi)',
            'Staten Island': 'Low (8,000/sq mi)',
            'NYC': 'High (27,000/sq mi)'
        }

        return density_map.get(borough, 'Medium')

# Example usage and testing
if __name__ == "__main__":
    print("🗺️ Testing Choropleth Map System...")

    # Create choropleth map system
    choropleth_system = ChoroplethMapSystem()

    # Test single illness type choropleth
    print("\n📊 Creating COVID-19 choropleth map...")
    covid_map = choropleth_system.create_choropleth_map('COVID-19')

    if covid_map:
        covid_map.save('covid_choropleth_map.html')
        print("✅ COVID-19 choropleth map saved: covid_choropleth_map.html")

    # Test multi-illness choropleth
    print("\n📊 Creating multi-illness choropleth map...")
    illness_types = ['COVID-19', 'Flu', 'Foodborne', 'Air Quality']
    multi_map = choropleth_system.create_multi_illness_choropleth(illness_types)

    if multi_map:
        multi_map.save('multi_illness_choropleth_map.html')
        print("✅ Multi-illness choropleth map saved: multi_illness_choropleth_map.html")

    print("\n🎯 Choropleth map system testing complete!")
