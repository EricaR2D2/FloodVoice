from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
import threading
import time
from phase2_pattern_detection import PatternDetector
from forecasting_engine import ForecastingEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'public_health_mvp_secret_key_2024'
socketio = SocketIO(app, cors_allowed_origins="*")

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
        conn = self.get_database_connection()
        
        try:
            # Get total records count
            hospital_count = pd.read_sql_query("SELECT COUNT(*) as count FROM hospital_data", conn).iloc[0]['count']
            pattern_count = pd.read_sql_query("SELECT COUNT(*) as count FROM pattern_detections", conn).iloc[0]['count']
            
            # Get latest data timestamp
            latest_data = pd.read_sql_query("""
                SELECT MAX(date) as latest_date FROM hospital_data
            """, conn).iloc[0]['latest_date']
            
            # Get recent patterns (last 7 days)
            recent_patterns = pd.read_sql_query("""
                SELECT pattern_type, COUNT(*) as count 
                FROM pattern_detections 
                WHERE date >= date('now', '-7 days')
                GROUP BY pattern_type
            """, conn)
            
            # Get data source status
            data_sources = {
                'hospital_data': hospital_count > 0,
                'air_quality_data': pd.read_sql_query("SELECT COUNT(*) as count FROM air_quality_data", conn).iloc[0]['count'] > 0,
                'cdc_ili_data': pd.read_sql_query("SELECT COUNT(*) as count FROM cdc_ili_data", conn).iloc[0]['count'] > 0,
                'nyc_covid_data': pd.read_sql_query("SELECT COUNT(*) as count FROM nyc_covid_data", conn).iloc[0]['count'] > 0
            }
            
            return {
                'total_hospital_records': hospital_count,
                'total_patterns_detected': pattern_count,
                'latest_data_date': latest_data,
                'recent_patterns': recent_patterns.to_dict('records') if not recent_patterns.empty else [],
                'data_sources': data_sources,
                'last_update': datetime.now().isoformat()
            }
            
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
            return df.to_dict('records')

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

# Initialize dashboard manager
dashboard_manager = DashboardManager()

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/summary')
def api_summary():
    """API endpoint for dashboard summary data."""
    summary = dashboard_manager.get_dashboard_summary()
    return jsonify(summary)

@app.route('/api/hospital-data')
def api_hospital_data():
    """API endpoint for hospital data visualization."""
    days = request.args.get('days', 30, type=int)
    data = dashboard_manager.get_hospital_data_for_chart(days)
    return jsonify(data)

@app.route('/api/patterns')
def api_patterns():
    """API endpoint for recent patterns."""
    limit = request.args.get('limit', 10, type=int)
    patterns = dashboard_manager.get_recent_patterns(limit)
    return jsonify(patterns)

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """API endpoint for alert settings."""
    if request.method == 'POST':
        settings = request.json
        dashboard_manager.update_alert_settings(settings)
        return jsonify({'status': 'success', 'message': 'Settings updated successfully'})
    else:
        return jsonify(dashboard_manager.alert_settings)

@app.route('/api/pattern/<int:pattern_id>')
def api_pattern_detail(pattern_id):
    """API endpoint for pattern details."""
    pattern = dashboard_manager.get_pattern_by_id(pattern_id)
    if pattern:
        return jsonify(pattern)
    else:
        return jsonify({'status': 'error', 'message': 'Pattern not found'}), 404

@app.route('/api/pattern/<int:pattern_id>/forecast')
def api_pattern_forecast(pattern_id):
    """API endpoint for pattern-specific forecasting."""
    forecast = dashboard_manager.generate_pattern_forecast(pattern_id)
    return jsonify(forecast)

@app.route('/api/run-detection', methods=['POST'])
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
def settings_page():
    """Settings configuration page."""
    return render_template('settings.html')

@app.route('/patterns')
def patterns_page():
    """Patterns analysis page."""
    return render_template('patterns.html')

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
    # Start background update thread
    update_thread = threading.Thread(target=background_data_update, daemon=True)
    update_thread.start()
    
    print("🚀 Public Health MVP Dashboard Starting...")
    print("📊 Dashboard: http://localhost:5000")
    print("⚙️  Settings: http://localhost:5000/settings")
    print("🔍 Patterns: http://localhost:5000/patterns")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
