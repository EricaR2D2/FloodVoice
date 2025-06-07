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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'public_health_mvp_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

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
UPDATE_INTERVAL = 300  # 5 minutes for demo (would be real-time in production)

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
            print("📊 Getting counts...")
            # Get total records count
            hospital_count_df = pd.read_sql_query("SELECT COUNT(*) as count FROM hospital_data", conn)
            hospital_count = int(hospital_count_df.iloc[0]['count'])

            pattern_count_df = pd.read_sql_query("SELECT COUNT(*) as count FROM pattern_detections", conn)
            pattern_count = int(pattern_count_df.iloc[0]['count'])
            print(f"✅ Counts - Hospital: {hospital_count}, Patterns: {pattern_count}")

            print("📊 Getting latest data...")
            # Get latest data timestamp
            latest_data_df = pd.read_sql_query("""
                SELECT MAX(date) as latest_date FROM hospital_data
            """, conn)
            latest_data = latest_data_df.iloc[0]['latest_date']
            print(f"✅ Latest data: {latest_data}")

            print("📊 Getting recent patterns...")
            # Get recent patterns (last 7 days)
            recent_patterns = pd.read_sql_query("""
                SELECT pattern_type, COUNT(*) as count
                FROM pattern_detections
                WHERE date >= date('now', '-7 days')
                GROUP BY pattern_type
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
            result = {
                'total_hospital_records': hospital_count,
                'total_patterns_detected': pattern_count,
                'latest_data_date': latest_data,
                'recent_patterns': recent_patterns.to_dict('records') if not recent_patterns.empty else [],
                'data_sources': data_sources,
                'last_update': datetime.now().isoformat()
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
    
    def get_hospital_data_for_chart(self, days=30):
        """Get hospital data for time series visualization."""
        conn = self.get_database_connection()
        
        try:
            query = """
                SELECT date, zip_code, hospital_name, er_visits_respiratory
                FROM hospital_data 
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
                ORDER BY detection_timestamp DESC
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
        """Generate forecast for a specific pattern."""
        pattern = self.get_pattern_by_id(pattern_id)
        if not pattern:
            return {'status': 'error', 'message': 'Pattern not found'}

        try:
            forecast = self.forecasting_engine.generate_forecast(
                hospital_name=pattern['hospital_name'],
                zip_code=pattern['zip_code'],
                forecast_days=7,
                days_back=30
            )

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
            detector = PatternDetector()
            data = detector.load_data()
            patterns = detector.detect_patterns(data)
            
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

def create_overview_map(patterns):
    """Create an overview map showing all recent alert locations."""
    try:
        # Load NYC ZIP codes GeoJSON
        geojson_path = os.path.join('static', 'nyc_zipcodes.geojson')
        with open(geojson_path, 'r') as f:
            nyc_zipcodes = json.load(f)

        # Create map centered on NYC
        nyc_center = [40.7128, -73.9352]  # NYC coordinates
        m = folium.Map(location=nyc_center, zoom_start=10)

        # Get unique ZIP codes with patterns
        zip_patterns = {}
        for pattern in patterns:
            zip_code = str(pattern['zip_code'])
            if zip_code not in zip_patterns:
                zip_patterns[zip_code] = []
            zip_patterns[zip_code].append(pattern)

        # Style function for ZIP codes
        def style_function(feature):
            zip_code_feature = feature['properties']['MODZCTA']
            if zip_code_feature in zip_patterns:
                # Highlight ZIP codes with alerts
                pattern_count = len(zip_patterns[zip_code_feature])
                if pattern_count >= 3:
                    color = '#d62728'  # Red for high activity
                    fillColor = '#ff7f0e'
                elif pattern_count >= 2:
                    color = '#ff7f0e'  # Orange for medium activity
                    fillColor = '#ffbb78'
                else:
                    color = '#2ca02c'  # Green for low activity
                    fillColor = '#98df8a'

                return {
                    'fillColor': fillColor,
                    'color': color,
                    'weight': 2,
                    'fillOpacity': 0.6,
                    'opacity': 1.0
                }
            else:
                # Default style for ZIP codes without alerts
                return {
                    'fillColor': '#1f77b4',
                    'color': '#aec7e8',
                    'weight': 1,
                    'fillOpacity': 0.1,
                    'opacity': 0.3
                }

        # Add ZIP code boundaries
        folium.GeoJson(
            nyc_zipcodes,
            style_function=style_function,
            tooltip=folium.features.GeoJsonTooltip(
                fields=['MODZCTA'],
                aliases=['ZIP Code:'],
                localize=True
            )
        ).add_to(m)

        # Add markers for each pattern
        for zip_code, zip_patterns_list in zip_patterns.items():
            # Find the center of the ZIP code
            zip_feature = None
            for feature in nyc_zipcodes['features']:
                if feature['properties']['MODZCTA'] == zip_code:
                    zip_feature = feature
                    break

            if zip_feature and zip_feature['geometry']['type'] == 'Polygon':
                # Calculate centroid
                coords = zip_feature['geometry']['coordinates'][0]
                lats = [coord[1] for coord in coords]
                lons = [coord[0] for coord in coords]
                center_lat = sum(lats) / len(lats)
                center_lon = sum(lons) / len(lons)

                # Create popup content
                popup_content = f"<b>ZIP Code {zip_code}</b><br>"
                popup_content += f"<b>{len(zip_patterns_list)} Recent Alerts</b><br><br>"

                for pattern in zip_patterns_list[:3]:  # Show up to 3 patterns
                    popup_content += f"• {pattern['pattern_type'].replace('_', ' ').title()}<br>"
                    popup_content += f"  {pattern['hospital_name']}<br>"
                    popup_content += f"  {pattern['date']}<br><br>"

                if len(zip_patterns_list) > 3:
                    popup_content += f"... and {len(zip_patterns_list) - 3} more"

                # Choose marker color based on pattern types
                spike_count = sum(1 for p in zip_patterns_list if p['pattern_type'] == 'spike')
                if spike_count > 0:
                    marker_color = 'red'
                    icon = 'arrow-up'
                else:
                    marker_color = 'orange'
                    icon = 'exclamation-triangle'

                folium.Marker(
                    location=[center_lat, center_lon],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=f"{len(zip_patterns_list)} alerts in ZIP {zip_code}",
                    icon=folium.Icon(color=marker_color, icon=icon, prefix='fa')
                ).add_to(m)

        # Add legend
        legend_html = '''
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 200px; height: 120px;
                    background-color: white; border:2px solid grey; z-index:9999;
                    font-size:14px; padding: 10px">
        <p><b>Alert Activity</b></p>
        <p><i class="fa fa-circle" style="color:#d62728"></i> High (3+ alerts)</p>
        <p><i class="fa fa-circle" style="color:#ff7f0e"></i> Medium (2 alerts)</p>
        <p><i class="fa fa-circle" style="color:#2ca02c"></i> Low (1 alert)</p>
        <p><i class="fa fa-circle" style="color:#1f77b4"></i> No alerts</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))

        return m._repr_html_()

    except Exception as e:
        print(f"Error creating overview map: {e}")
        # Return simple fallback map
        m = folium.Map(location=[40.7128, -73.9352], zoom_start=10)
        folium.Marker(
            location=[40.7128, -73.9352],
            popup="NYC Public Health Dashboard",
            tooltip="NYC Overview",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
        return m._repr_html_()

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

@app.route('/api/dashboard-map')
@login_required
def api_dashboard_map():
    """API endpoint for dashboard overview map."""
    try:
        # Get recent patterns for map
        patterns = dashboard_manager.get_recent_patterns(10)

        if not patterns:
            # Create empty map if no patterns
            return create_overview_map([])

        # Create overview map with all recent patterns
        map_html = create_overview_map(patterns)
        return map_html

    except Exception as e:
        print(f"Error creating dashboard map: {e}")
        return create_overview_map([])

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
    print("📊 Dashboard: http://localhost:5000")
    print("⚙️  Settings: http://localhost:5000/settings")
    print("🔍 Patterns: http://localhost:5000/patterns")
    print("🔐 Login: http://localhost:5000/login")

    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
