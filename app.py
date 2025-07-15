from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
import threading
import time
import folium
import os
from phase2_pattern_detection import PatternDetector
from forecasting_engine import ForecastingEngine
from models import User, init_user_db
from advanced_dashboard_routes import advanced_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'public_health_mvp_secret_key_2024')
socketio = SocketIO(app, cors_allowed_origins="*")

# Register blueprints
app.register_blueprint(advanced_bp)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    return User.get(int(user_id))

# Configuration
DATABASE_PATH = 'public_health_data.db'
UPDATE_INTERVAL = 3600  # 1 hour to prevent pattern detection overload

class DashboardManager:
    def __init__(self):
        self.last_update = None
        self.forecasting_engine = ForecastingEngine()
        self.alert_settings = {
            'spike_threshold': 30.0,
            'drop_threshold': 30.0,
            'consistently_high_threshold': 20.0,
            'email_notifications': True,
            'slack_notifications': False,
            'notification_email': 'analyst@nyc.gov'
        }
        
    def get_database_connection(self):
        """Get database connection."""
        return sqlite3.connect(DATABASE_PATH)
    
    def get_dashboard_summary(self):
        """Get summary statistics for dashboard."""
        print("🔍 Starting get_dashboard_summary...")
        conn = self.get_database_connection()

        try:
            # Enhanced data freshness check with detailed source information
            data_freshness = {
                'covid_daily_counts': {
                    **self.get_data_freshness('covid_daily_counts', 'date_of_interest'),
                    'source_name': 'COVID-19 Daily Counts',
                    'source_type': 'NYC Open Data',
                    'priority': 'high',
                    'description': 'Daily COVID-19 cases, hospitalizations, and deaths by borough'
                },
                'restaurant_data': {
                    **self.get_data_freshness('restaurant_inspection_data', 'date'),
                    'source_name': 'Restaurant Inspections',
                    'source_type': 'NYC Open Data',
                    'priority': 'high',
                    'description': 'Restaurant inspection results and foodborne illness risk'
                },
                'flu_surveillance': {
                    **self.get_data_freshness('flu_surveillance_data', 'date'),
                    'source_name': 'Flu Surveillance',
                    'source_type': 'CDC FluView (Current)',
                    'priority': 'medium',
                    'description': 'CDC FluView influenza-like illness surveillance for NY region'
                },
                'air_quality_data': {
                    **self.get_data_freshness('enhanced_air_quality_data', 'date'),
                    'source_name': 'Air Quality',
                    'source_type': 'EPA AirNow (Current)',
                    'priority': 'medium',
                    'description': 'Real-time air quality index and health risk indicators'
                },
                'hospital_data': {
                    **self.get_data_freshness('real_hospital_data', 'date'),
                    'source_name': 'Hospital ER Visits',
                    'source_type': 'Derived from COVID Data',
                    'priority': 'high',
                    'description': 'Emergency department respiratory visits by location'
                }
            }
            
            print("📊 Getting counts...")
            # Get total records count from real hospital data
            hospital_count_df = pd.read_sql_query("SELECT COUNT(*) as count FROM real_hospital_data", conn)
            hospital_count = int(hospital_count_df.iloc[0]['count'])

            pattern_count_df = pd.read_sql_query("SELECT COUNT(*) as count FROM pattern_detections", conn)
            pattern_count = int(pattern_count_df.iloc[0]['count'])
            print(f"✅ Counts - Hospital: {hospital_count}, Patterns: {pattern_count}")

            print("📊 Getting latest data across all sources...")
            # Get the most recent date across all data sources for demo freshness
            latest_dates = []

            # Check multiple data sources and find the most recent
            data_source_queries = [
                ("SELECT MAX(date) as latest_date FROM real_hospital_data", "Hospital Data"),
                ("SELECT MAX(date_of_interest) as latest_date FROM covid_daily_counts", "COVID Daily Counts"),
                ("SELECT MAX(date) as latest_date FROM restaurant_inspection_data", "Restaurant Data"),
                ("SELECT MAX(date) as latest_date FROM flu_surveillance_data", "Flu Surveillance"),
                ("SELECT MAX(date_of_interest) as latest_date FROM nyc_covid_data", "NYC COVID Data")
            ]

            for query, source_name in data_source_queries:
                try:
                    result = pd.read_sql_query(query, conn)
                    if not result.empty and result.iloc[0]['latest_date']:
                        date_str = result.iloc[0]['latest_date']
                        # Parse date (handle datetime format)
                        if ' ' in str(date_str):
                            date_str = date_str.split(' ')[0]
                        latest_dates.append((date_str, source_name))
                except Exception as e:
                    print(f"⚠️ Could not get latest date from {source_name}: {e}")

            # Find the most recent date
            if latest_dates:
                latest_dates.sort(reverse=True)  # Sort by date descending
                latest_data = latest_dates[0][0]  # Most recent date
                latest_source = latest_dates[0][1]  # Source name
                print(f"✅ Latest data: {latest_data} (from {latest_source})")
            else:
                latest_data = "2025-07-12"  # Fallback to today for demo
                print(f"⚠️ No latest data found, using fallback: {latest_data}")

            print("📊 Getting recent patterns...")
            # Get recent patterns (last 30 days to ensure we have data for the chart)
            recent_patterns = pd.read_sql_query("""
                SELECT pattern_type, COUNT(*) as count
                FROM pattern_detections
                WHERE date >= date('now', '-30 days')
                GROUP BY pattern_type
                ORDER BY count DESC
            """, conn)
            print(f"✅ Recent patterns shape: {recent_patterns.shape}")

            print("📊 Getting data sources...")
            # Get data source status
            air_quality_count = int(pd.read_sql_query("SELECT COUNT(*) as count FROM air_quality_data", conn).iloc[0]['count'])
            cdc_count = int(pd.read_sql_query("SELECT COUNT(*) as count FROM cdc_ili_data", conn).iloc[0]['count'])
            covid_count = int(pd.read_sql_query("SELECT COUNT(*) as count FROM nyc_covid_data", conn).iloc[0]['count'])

            data_sources = {
                'hospital_data': hospital_count > 0,
                'air_quality_data': air_quality_count > 0,
                'cdc_ili_data': cdc_count > 0,
                'nyc_covid_data': covid_count > 0
            }
            print(f"✅ Data sources: {data_sources}")

            print("📊 Building result...")

            # Calculate overall data freshness status
            current_sources = sum(1 for source in data_freshness.values() if source.get('status') == 'current')
            recent_sources = sum(1 for source in data_freshness.values() if source.get('status') == 'recent')
            outdated_sources = sum(1 for source in data_freshness.values() if source.get('status') == 'outdated')
            total_sources = len(data_freshness)

            # Determine overall freshness status
            if current_sources >= total_sources * 0.6:  # 60% or more current
                overall_freshness = 'excellent'
            elif current_sources + recent_sources >= total_sources * 0.8:  # 80% current or recent
                overall_freshness = 'good'
            else:
                overall_freshness = 'needs_attention'

            result = {
                'total_hospital_records': hospital_count,
                'total_patterns_detected': pattern_count,
                'latest_data_date': latest_data,
                'recent_patterns': recent_patterns.to_dict('records') if not recent_patterns.empty else [],
                'data_sources': data_sources,
                'last_update': datetime.now().isoformat(),
                'data_freshness': data_freshness,
                'overall_freshness': {
                    'status': overall_freshness,
                    'current_sources': current_sources,
                    'recent_sources': recent_sources,
                    'outdated_sources': outdated_sources,
                    'total_sources': total_sources
                }
            }
            print(f"✅ Result built successfully with {len(result)} keys")
            return result

        except Exception as e:
            print(f"❌ Error in get_dashboard_summary: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            conn.close()
    
    def get_data_freshness(self, table, date_column):
        """Get data freshness status for a table."""
        conn = self.get_database_connection()
        try:
            query = f"SELECT MAX({date_column}) as latest_date FROM {table}"
            df = pd.read_sql_query(query, conn)
            latest_date = df.iloc[0]['latest_date']
            
            if latest_date:
                # Handle different date formats (with or without time)
                date_str = str(latest_date).strip()
                parsed_date = None

                # Try multiple parsing approaches
                parsing_attempts = [
                    # Format: '2025-06-09 00:00:00' (datetime with time)
                    lambda d: datetime.strptime(d, '%Y-%m-%d %H:%M:%S'),
                    # Format: '2025-06-09' (date only)
                    lambda d: datetime.strptime(d, '%Y-%m-%d'),
                    # Extract date part from datetime string
                    lambda d: datetime.strptime(d.split(' ')[0], '%Y-%m-%d') if ' ' in d else None,
                    # Extract first 10 characters as date
                    lambda d: datetime.strptime(d[:10], '%Y-%m-%d') if len(d) >= 10 else None
                ]

                for attempt in parsing_attempts:
                    try:
                        parsed_date = attempt(date_str)
                        if parsed_date:
                            break
                    except (ValueError, AttributeError, IndexError):
                        continue

                if not parsed_date:
                    print(f"⚠️ Could not parse date: {repr(latest_date)}")
                    return {'status': 'unknown', 'days_old': None, 'latest_date': None}

                latest_date = parsed_date

                days_old = (datetime.now() - latest_date).days
                
                # Determine freshness status
                if days_old <= 7:
                    status = "current"
                elif days_old <= 30:
                    status = "recent"
                else:
                    status = "outdated"
                    
                return {
                    'latest_date': latest_date.strftime('%Y-%m-%d'),
                    'days_old': days_old,
                    'status': status
                }
            return {'status': 'unknown', 'days_old': None, 'latest_date': None}
        finally:
            conn.close()
    
    def get_hospital_data_for_chart(self, days=30):
        """Get hospital data for time series visualization."""
        conn = self.get_database_connection()
        
        try:
            query = """
                SELECT date, zip_code, hospital_name, respiratory_visits as er_visits_respiratory
                FROM real_hospital_data
                WHERE date >= date('now', '-{} days')
                ORDER BY date, zip_code
            """.format(days)
            
            df = pd.read_sql_query(query, conn)
            
            # Group by date for aggregate view
            daily_totals = df.groupby('date')['er_visits_respiratory'].sum().reset_index()
            
            # Group by ZIP code for geographic view
            zip_totals = df.groupby(['date', 'zip_code'])['er_visits_respiratory'].sum().reset_index()
            
            return {
                'daily_totals': daily_totals.to_dict('records'),
                'zip_breakdown': zip_totals.to_dict('records')
            }
            
        finally:
            conn.close()
    
    def get_recent_patterns(self, limit=10):
        """Get recent pattern detections."""
        conn = self.get_database_connection()

        try:
            query = """
                SELECT id, date, zip_code, hospital_name, pattern_type,
                       current_value, rolling_mean, percentage_change,
                       confidence_score, ai_explanation, detection_timestamp
                FROM pattern_detections
                ORDER BY
                    CASE
                        WHEN hospital_name LIKE '%Sinai%' OR hospital_name LIKE '%Montefiore%'
                             OR hospital_name LIKE '%NYU%' OR hospital_name LIKE '%Presbyterian%'
                             OR hospital_name LIKE '%Maimonides%' OR hospital_name LIKE '%Kings County%'
                             OR hospital_name LIKE '%Elmhurst%' OR hospital_name LIKE '%Jamaica%'
                        THEN 0 ELSE 1
                    END,
                    detection_timestamp DESC
                LIMIT ?
            """

            df = pd.read_sql_query(query, conn, params=[limit])

            # Convert to records and clean up any potential JSON issues
            records = df.to_dict('records')

            # Clean up each record to ensure JSON serialization works
            cleaned_records = []
            for record in records:
                cleaned_record = {}
                for key, value in record.items():
                    if value is None:
                        cleaned_record[key] = None
                    elif isinstance(value, (int, float, bool)):
                        cleaned_record[key] = value
                    else:
                        # Convert to string and clean up any problematic characters
                        cleaned_record[key] = str(value).replace('\x00', '').strip()
                cleaned_records.append(cleaned_record)

            return cleaned_records

        finally:
            conn.close()

    def get_pattern_by_id(self, pattern_id):
        """Get a specific pattern by ID."""
        conn = self.get_database_connection()

        try:
            query = """
                SELECT id, date, zip_code, hospital_name, pattern_type,
                       current_value, rolling_mean, percentage_change,
                       confidence_score, ai_explanation, detection_timestamp,
                       context_data
                FROM pattern_detections
                WHERE id = ?
            """

            df = pd.read_sql_query(query, conn, params=[pattern_id])
            if len(df) > 0:
                pattern = df.iloc[0].to_dict()
                # Parse context_data if it exists
                if pattern.get('context_data'):
                    try:
                        pattern['context_data'] = json.loads(pattern['context_data'])
                    except:
                        pattern['context_data'] = {}
                return pattern
            return None

        finally:
            conn.close()

    def generate_pattern_forecast(self, pattern_id):
        """Generate enhanced forecast for a specific pattern with confidence intervals."""
        pattern = self.get_pattern_by_id(pattern_id)
        if not pattern:
            return {'status': 'error', 'message': 'Pattern not found'}

        try:
            # Generate forecast with enhanced confidence intervals
            forecast = self.forecasting_engine.generate_forecast(
                hospital_name=pattern['hospital_name'],
                zip_code=pattern['zip_code'],
                forecast_days=7,
                days_back=30
            )

            # Add enhanced interpretation
            if forecast['status'] == 'success':
                interpretation = self.forecasting_engine.get_enhanced_forecast_interpretation(forecast)
                forecast['interpretation'] = interpretation

            # Add pattern context to forecast
            forecast['pattern_context'] = {
                'pattern_id': pattern_id,
                'pattern_type': pattern['pattern_type'],
                'pattern_date': pattern['date'],
                'current_value': pattern['current_value'],
                'percentage_change': pattern['percentage_change']
            }

            return forecast

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Forecast generation failed: {str(e)}'
            }
    
    def update_alert_settings(self, settings):
        """Update alert configuration settings."""
        self.alert_settings.update(settings)
        return True
    
    def run_pattern_detection(self):
        """Run pattern detection and return results."""
        try:
            # Check if pattern detection has run recently (within last hour)
            conn = self.get_database_connection()
            recent_patterns = pd.read_sql_query("""
                SELECT COUNT(*) as count
                FROM pattern_detections
                WHERE detection_timestamp >= datetime('now', '-1 hour')
            """, conn)
            conn.close()

            if recent_patterns.iloc[0]['count'] > 0:
                print("⏭️ Pattern detection already run recently, skipping...")
                return 0

            print("🔍 Running pattern detection...")
            detector = PatternDetector()
            data = detector.load_data()
            patterns = detector.detect_patterns(data)

            # Limit patterns to prevent overwhelming the system
            if len(patterns) > 50:
                print(f"⚠️ Too many patterns detected ({len(patterns)}), limiting to 50 most recent")
                patterns = patterns[-50:]  # Take the 50 most recent patterns

            # Generate explanations for new patterns
            new_patterns = []
            for pattern in patterns:
                explanation = detector.generate_ai_explanation(pattern)
                pattern['ai_explanation'] = explanation
                new_patterns.append(pattern)

            # Store results
            if new_patterns:
                detector.store_results(new_patterns)

            detector.close()
            return len(new_patterns)

        except Exception as e:
            print(f"Error running pattern detection: {e}")
            return 0

def create_alert_map(zip_code, pattern_data):
    """Create an interactive Folium map for the alert location."""
    try:
        # Load NYC ZIP codes GeoJSON
        geojson_path = os.path.join('static', 'nyc_zipcodes.geojson')
        with open(geojson_path, 'r') as f:
            nyc_zipcodes = json.load(f)

        # Create map centered on NYC
        nyc_center = [40.7128, -73.9352]  # NYC coordinates
        m = folium.Map(location=nyc_center, zoom_start=10)

        # Style function for ZIP codes
        def style_function(feature):
            zip_code_feature = feature['properties']['MODZCTA']
            if zip_code_feature == str(zip_code):
                # Highlight the alert ZIP code
                return {
                    'fillColor': '#ff7f0e',
                    'color': '#d62728',
                    'weight': 3,
                    'fillOpacity': 0.7,
                    'opacity': 1.0
                }
            else:
                # Default style for other ZIP codes
                return {
                    'fillColor': '#1f77b4',
                    'color': '#aec7e8',
                    'weight': 1,
                    'fillOpacity': 0.1,
                    'opacity': 0.3
                }

        # Add GeoJSON layer with styling
        folium.GeoJson(
            nyc_zipcodes,
            style_function=style_function,
            popup=folium.GeoJsonPopup(
                fields=['MODZCTA', 'label'],
                aliases=['ZIP Code:', 'Area:'],
                localize=True,
                labels=True,
                style="background-color: white;",
            ),
            tooltip=folium.GeoJsonTooltip(
                fields=['MODZCTA'],
                aliases=['ZIP Code:'],
                localize=True,
                sticky=True,
                labels=True,
                style="""
                    background-color: #F0EFEF;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """,
                max_width=800,
            )
        ).add_to(m)

        # Find the bounds of the highlighted ZIP code to fit the map
        highlighted_zip = None
        for feature in nyc_zipcodes['features']:
            if feature['properties']['MODZCTA'] == str(zip_code):
                highlighted_zip = feature
                break

        if highlighted_zip:
            # Add a marker for the alert location
            # Calculate centroid of the ZIP code polygon
            coords = highlighted_zip['geometry']['coordinates'][0]
            if highlighted_zip['geometry']['type'] == 'MultiPolygon':
                coords = highlighted_zip['geometry']['coordinates'][0][0]

            # Simple centroid calculation
            lats = [coord[1] for coord in coords]
            lons = [coord[0] for coord in coords]
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)

            # Add marker with alert information
            popup_text = f"""
            <div style="width: 300px;">
                <h5><i class="fas fa-exclamation-triangle"></i> {pattern_data['pattern_type'].replace('_', ' ').title()} Alert</h5>
                <p><strong>ZIP Code:</strong> {zip_code}</p>
                <p><strong>Hospital:</strong> {pattern_data['hospital_name']}</p>
                <p><strong>Date:</strong> {pattern_data['date']}</p>
                <p><strong>Current Visits:</strong> {pattern_data['current_value']}</p>
                <p><strong>Change:</strong> {pattern_data['percentage_change']:.1f}% from average</p>
                <p><strong>Confidence:</strong> {pattern_data['confidence_score']:.0f}%</p>
            </div>
            """

            folium.Marker(
                location=[center_lat, center_lon],
                popup=folium.Popup(popup_text, max_width=350),
                tooltip=f"Alert in ZIP {zip_code}",
                icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')
            ).add_to(m)

            # Fit map to the highlighted ZIP code area with some padding
            m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]], padding=[20, 20])

        # Return the map as HTML string
        return m._repr_html_()

    except Exception as e:
        print(f"Error creating map: {e}")
        # Return a simple fallback map
        m = folium.Map(location=[40.7128, -73.9352], zoom_start=10)
        folium.Marker(
            location=[40.7128, -73.9352],
            popup=f"Alert in ZIP {zip_code}",
            tooltip=f"ZIP {zip_code}",
            icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')
        ).add_to(m)
        return m._repr_html_()

def create_enhanced_layered_map(hospital_df, tick_df, weather_df):
    """Create an enhanced map with multiple data layers for weather, tick diseases, and hospital data."""
    try:
        # Create base map centered on NYC
        nyc_map = folium.Map(
            location=[40.7128, -73.9060],
            zoom_start=11,
            tiles='OpenStreetMap'
        )

        # Enhanced ZIP code coordinates with more locations
        zip_coords = {
            '10001': [40.7505, -73.9934],  # Manhattan
            '10451': [40.8176, -73.9482],  # Bronx
            '11101': [40.7505, -73.9365],  # Queens
            '11201': [40.6892, -73.9442],  # Brooklyn
            '10301': [40.6323, -74.0754],  # Staten Island
            # Additional tick-active ZIP codes
            '10302': [40.6178, -74.1377],  # Staten Island West
            '10303': [40.6415, -74.1134],  # Staten Island Central
            '10304': [40.5817, -74.0857],  # Staten Island East
            '10305': [40.5928, -74.0707],  # Staten Island South
            '10463': [40.8848, -73.9085],  # Bronx Riverdale
            '10471': [40.8958, -73.8958],  # Bronx Fieldston
            '10466': [40.8902, -73.8485],  # Bronx Pelham
            '10467': [40.8736, -73.8780],  # Bronx Norwood
            '11354': [40.7677, -73.8370],  # Queens Flushing
            '11355': [40.7677, -73.8370],  # Queens Whitestone
            '11356': [40.7864, -73.8370],  # Queens College Point
            '11209': [40.6221, -74.0307],  # Brooklyn Bay Ridge
            '11220': [40.6415, -74.0134],  # Brooklyn Sunset Park
            '10024': [40.7831, -73.9712],  # Manhattan Upper West Side
            '10025': [40.7957, -73.9667]   # Manhattan Morningside Heights
        }

        # Create feature groups for different layers
        hospital_layer = folium.FeatureGroup(name="🏥 Hospital ER Data", show=True)
        tick_layer = folium.FeatureGroup(name="🦟 Tick Disease Risk", show=True)
        weather_layer = folium.FeatureGroup(name="🌡️ Weather Conditions", show=True)

        # Add hospital markers to hospital layer
        for _, row in hospital_df.iterrows():
            if row['zip_code'] in zip_coords:
                coords = zip_coords[row['zip_code']]

                # Color based on respiratory visit percentage
                if row['respiratory_pct'] > 30:
                    color = 'red'
                elif row['respiratory_pct'] > 20:
                    color = 'orange'
                else:
                    color = 'green'

                folium.CircleMarker(
                    location=coords,
                    radius=max(5, min(20, row['visit_count'] / 10)),
                    popup=f"""
                    <b>{row['hospital_name']}</b><br>
                    ZIP: {row['zip_code']}<br>
                    Total Visits: {row['visit_count']}<br>
                    Respiratory: {row['respiratory_pct']:.1f}%
                    """,
                    color=color,
                    fillColor=color,
                    fillOpacity=0.7,
                    tooltip=f"{row['hospital_name']}: {row['visit_count']} visits"
                ).add_to(hospital_layer)

        # Add tick disease risk markers to tick layer
        for _, row in tick_df.iterrows():
            if row['zip_code'] in zip_coords:
                coords = zip_coords[row['zip_code']]

                # Risk level based on case count
                if row['tick_cases'] > 10:
                    risk_color = 'darkred'
                    risk_level = 'High'
                elif row['tick_cases'] > 5:
                    risk_color = 'orange'
                    risk_level = 'Medium'
                else:
                    risk_color = 'yellow'
                    risk_level = 'Low'

                folium.CircleMarker(
                    location=coords,
                    radius=max(8, min(25, row['tick_cases'] * 2)),
                    popup=f"""
                    <b>Tick Disease Risk</b><br>
                    ZIP: {row['zip_code']}<br>
                    Cases (30 days): {row['tick_cases']}<br>
                    Severe Cases: {row['severe_cases']}<br>
                    Risk Level: {risk_level}
                    """,
                    color=risk_color,
                    fillColor=risk_color,
                    fillOpacity=0.5,
                    tooltip=f"ZIP {row['zip_code']}: {row['tick_cases']} tick cases"
                ).add_to(tick_layer)

        # Add weather station markers to weather layer
        weather_coords = {
            'Central Park': [40.7829, -73.9654],
            'LaGuardia Airport': [40.7769, -73.8740],
            'JFK Airport': [40.6413, -73.7781],
            'Brooklyn': [40.6501, -73.9496],
            'Staten Island': [40.5795, -74.1502]
        }

        for _, row in weather_df.iterrows():
            if row['station_name'] in weather_coords:
                coords = weather_coords[row['station_name']]

                # Color based on tick risk score
                if row['avg_tick_risk'] > 70:
                    weather_color = 'red'
                elif row['avg_tick_risk'] > 40:
                    weather_color = 'orange'
                else:
                    weather_color = 'blue'

                folium.Marker(
                    location=coords,
                    popup=f"""
                    <b>{row['station_name']} Weather</b><br>
                    Avg Temperature: {row['avg_temp']:.1f}°F<br>
                    Avg Humidity: {row['avg_humidity']:.1f}%<br>
                    Tick Risk Score: {row['avg_tick_risk']:.0f}/100
                    """,
                    tooltip=f"{row['station_name']}: {row['avg_temp']:.1f}°F",
                    icon=folium.Icon(icon='thermometer-half', prefix='fa', color=weather_color)
                ).add_to(weather_layer)

        # Add all layers to map
        hospital_layer.add_to(nyc_map)
        tick_layer.add_to(nyc_map)
        weather_layer.add_to(nyc_map)

        # Add layer control
        folium.LayerControl().add_to(nyc_map)

        # Add enhanced legend
        legend_html = '''
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 250px; height: 180px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:12px; padding: 10px; border-radius: 5px;">
        <p><b>🗺️ NYC Health Surveillance Map</b></p>
        <p><b>Hospital ER Data:</b></p>
        <p>🔴 High Respiratory (>30%) | 🟠 Medium (20-30%) | 🟢 Low (<20%)</p>
        <p><b>Tick Disease Risk:</b></p>
        <p>🔴 High (>10 cases) | 🟠 Medium (5-10) | 🟡 Low (<5)</p>
        <p><b>Weather Stations:</b></p>
        <p>🌡️ Tick Risk: 🔴 High (>70) | 🟠 Med (40-70) | 🔵 Low (<40)</p>
        <p><i>Click layers to toggle visibility</i></p>
        </div>
        '''
        nyc_map.get_root().html.add_child(folium.Element(legend_html))

        return nyc_map._repr_html_()

    except Exception as e:
        print(f"Error creating enhanced layered map: {e}")
        return "<p>Error loading enhanced map</p>"



# Initialize dashboard manager
dashboard_manager = DashboardManager()

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')

        user = User.get_by_username(username)

        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.update_last_login()

            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout handler."""
    username = current_user.username
    logout_user()
    flash(f'You have been logged out, {username}.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page and handler."""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not username or not password or not confirm_password:
            flash('Please fill in all fields.', 'error')
            return render_template('register.html')

        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        # Check if username already exists
        if User.get_by_username(username):
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('register.html')

        # Create new user
        new_user = User(
            id=None,
            username=username,
            password_hash=None,
            created_at=datetime.now().isoformat()
        )
        new_user.set_password(password)

        if new_user.save():
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Please try again.', 'error')

    return render_template('register.html')

@app.route('/')
@login_required
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/summary')
@login_required
def api_summary():
    """API endpoint for dashboard summary data."""
    try:
        print(f"🔍 API Summary called by user: {current_user.username}")
        summary = dashboard_manager.get_dashboard_summary()
        print(f"✅ Summary generated successfully: {len(summary)} keys")
        return jsonify(summary)
    except Exception as e:
        print(f"❌ API Summary error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/hospital-data')
@login_required
def api_hospital_data():
    """API endpoint for hospital data visualization."""
    days = request.args.get('days', 30, type=int)
    data = dashboard_manager.get_hospital_data_for_chart(days)
    return jsonify(data)

@app.route('/api/patterns')
@login_required
def api_patterns():
    """API endpoint for recent patterns."""
    try:
        limit = request.args.get('limit', 10, type=int)
        patterns = dashboard_manager.get_recent_patterns(limit)

        # Ensure we return valid JSON
        if patterns is None:
            patterns = []

        return jsonify(patterns)

    except Exception as e:
        print(f"Error in api_patterns: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to load patterns', 'message': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def api_settings():
    """API endpoint for alert settings."""
    if request.method == 'POST':
        settings = request.json
        dashboard_manager.update_alert_settings(settings)
        return jsonify({'status': 'success', 'message': 'Settings updated successfully'})
    else:
        return jsonify(dashboard_manager.alert_settings)

@app.route('/api/pattern/<int:pattern_id>')
@login_required
def api_pattern_detail(pattern_id):
    """API endpoint for pattern details."""
    pattern = dashboard_manager.get_pattern_by_id(pattern_id)
    if pattern:
        return jsonify(pattern)
    else:
        return jsonify({'status': 'error', 'message': 'Pattern not found'}), 404

@app.route('/api/pattern/<int:pattern_id>/forecast')
@login_required
def api_pattern_forecast(pattern_id):
    """API endpoint for pattern-specific forecasting."""
    forecast = dashboard_manager.generate_pattern_forecast(pattern_id)
    return jsonify(forecast)

@app.route('/api/simulate-alerts', methods=['POST'])
@login_required
def api_simulate_alerts():
    """API endpoint for threshold simulation."""
    try:
        # Get simulation parameters from request
        simulation_params = request.json

        # Extract threshold values (convert percentages to decimals)
        custom_thresholds = {
            'spike_threshold': simulation_params.get('sim_spike_percentage', 30) / 100.0,
            'drop_threshold': simulation_params.get('sim_drop_percentage', 30) / 100.0,
            'consistently_high_threshold': simulation_params.get('sim_high_value_threshold', 20) / 100.0
        }

        # Get simulation period
        days_back = simulation_params.get('days_back', 30)

        # Run simulation
        detector = PatternDetector()
        simulated_alerts = detector.simulate_alerts(custom_thresholds, days_back)
        detector.close()

        return jsonify({
            'status': 'success',
            'simulation_params': {
                'spike_threshold': custom_thresholds['spike_threshold'] * 100,
                'drop_threshold': custom_thresholds['drop_threshold'] * 100,
                'consistently_high_threshold': custom_thresholds['consistently_high_threshold'] * 100,
                'days_back': days_back
            },
            'alerts_found': len(simulated_alerts),
            'simulated_alerts': simulated_alerts
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Simulation failed: {str(e)}'
        }), 500

@app.route('/api/run-detection', methods=['POST'])
@login_required
def api_run_detection():
    """API endpoint to manually trigger pattern detection."""
    patterns_found = dashboard_manager.run_pattern_detection()
    
    # Emit real-time update to connected clients
    socketio.emit('patterns_updated', {
        'patterns_found': patterns_found,
        'timestamp': datetime.now().isoformat()
    })
    
    return jsonify({
        'status': 'success',
        'patterns_found': patterns_found,
        'message': f'Pattern detection complete. Found {patterns_found} new patterns.'
    })

@app.route('/settings')
@login_required
def settings_page():
    """Settings configuration page."""
    return render_template('settings.html')

@app.route('/patterns')
@login_required
def patterns_page():
    """Patterns analysis page."""
    return render_template('patterns.html')

@app.route('/debug')
@login_required
def debug_page():
    """Debug page to test data loading."""
    try:
        summary = dashboard_manager.get_dashboard_summary()
        return f"""
        <h1>Debug Info</h1>
        <p><strong>User:</strong> {current_user.username}</p>
        <p><strong>Total Hospital Records:</strong> {summary.get('total_hospital_records', 'Error')}</p>
        <p><strong>Total Patterns:</strong> {summary.get('total_patterns_detected', 'Error')}</p>
        <p><strong>Latest Data:</strong> {summary.get('latest_data_date', 'Error')}</p>
        <p><strong>Last Update:</strong> {summary.get('last_update', 'Error')}</p>
        <hr>
        <p><a href="/">Back to Dashboard</a></p>
        <hr>
        <pre>{summary}</pre>
        """
    except Exception as e:
        return f"<h1>Debug Error</h1><p>{str(e)}</p><p><a href='/'>Back to Dashboard</a></p>"

@app.route('/map')
@login_required
def map_view():
    """Enhanced interactive map with multiple data layers"""
    try:
        conn = sqlite3.connect('public_health_data.db')

        # Get recent hospital data for map markers (use broader range since data may be older)
        hospital_query = """
            SELECT zip_code, hospital_name, COUNT(*) as visit_count,
                   AVG(CASE WHEN respiratory_visits > 0 THEN
                       (CAST(respiratory_visits AS FLOAT) / CAST(total_visits AS FLOAT)) * 100
                       ELSE 0 END) as respiratory_pct
            FROM real_hospital_data
            WHERE date >= date('now', '-30 days')
            GROUP BY zip_code, hospital_name
            ORDER BY visit_count DESC
            LIMIT 20
        """

        hospital_df = pd.read_sql_query(hospital_query, conn)

        # Get tick disease data for risk overlay (all available data)
        tick_query = """
            SELECT zip_code, total_cases as tick_cases, severe_cases
            FROM real_tick_disease_summary
            ORDER BY total_cases DESC
        """

        tick_df = pd.read_sql_query(tick_query, conn)

        # Get weather data for environmental overlay (all available data)
        weather_query = """
            SELECT station_name, AVG(temp_avg_f) as avg_temp,
                   AVG(humidity_avg) as avg_humidity,
                   AVG(tick_risk_score) as avg_tick_risk
            FROM real_weather_data
            GROUP BY station_name
        """

        weather_df = pd.read_sql_query(weather_query, conn)

        # Create enhanced layered map
        map_html = create_enhanced_layered_map(hospital_df, tick_df, weather_df)

        conn.close()

        return render_template('map.html', map_html=map_html)

    except Exception as e:
        print(f"Error in map view: {e}")
        return render_template('map.html', map_html="<p>Error loading map</p>")



@app.route('/alert/<int:alert_id>')
@login_required
def alert_detail(alert_id):
    """Alert detail page with interactive map."""
    # Get alert details
    pattern = dashboard_manager.get_pattern_by_id(alert_id)
    if not pattern:
        flash('Alert not found', 'error')
        return redirect(url_for('index'))

    # Create interactive map
    map_html = create_alert_map(pattern['zip_code'], pattern)

    return render_template('alert_detail.html',
                         pattern=pattern,
                         map_html=map_html)

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('status', {'msg': 'Connected to Public Health MVP Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

def background_data_update():
    """Background task to periodically update data and check for patterns."""
    while True:
        try:
            # Run pattern detection
            patterns_found = dashboard_manager.run_pattern_detection()
            
            if patterns_found > 0:
                # Emit update to all connected clients
                socketio.emit('patterns_updated', {
                    'patterns_found': patterns_found,
                    'timestamp': datetime.now().isoformat()
                })
            
            # Update dashboard data
            socketio.emit('dashboard_updated', {
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Background update error: {e}")
        
        time.sleep(UPDATE_INTERVAL)

if __name__ == '__main__':
    # Initialize user database
    print("🔧 Initializing authentication system...")
    init_user_db()

    # Start background update thread
    update_thread = threading.Thread(target=background_data_update, daemon=True)
    update_thread.start()

    print("🚀 Public Health MVP Dashboard Starting...")

    # Get port from environment variable (Heroku sets this)
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'

    if debug_mode:
        print("📊 Dashboard: http://localhost:5000")
        print("⚙️  Settings: http://localhost:5000/settings")
        print("🔍 Patterns: http://localhost:5000/patterns")
        print("🔐 Login: http://localhost:5000/login")
    else:
        print("🌐 Running in production mode")

    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=port)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', 
                          error_code=404,
                          error_message="The requested page could not be found."), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html',
                          error_code=500,
                          error_message="An internal server error occurred."), 500

@app.route('/api/map-data', methods=['POST'])
def get_map_data():
    try:
        filters = request.json
        
        # Initialize result variable before using it
        result = {
            'data': [],
            'status': 'success'
        }
        
        # Your existing code to populate result...
        # ...
        
        return jsonify(result)
    except Exception as e:
        print(f"Error in get_map_data: {str(e)}")
        return jsonify({
            'error': True,
            'message': 'Failed to load map data. Please try again.',
            'details': str(e)
        }), 500







