"""
FloodVoice - Community-Centered Flood Emergency Response Platform
Main Flask Application

Empowers community representatives to check on vulnerable residents during flood events
by combining real-time FloodNet sensor data with ground-level community narratives.
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import logging
import urllib.request
import urllib.error

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'floodvoice_secret_key_2025')

# Enable CORS for API endpoints
CORS(app)

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
DATABASE_PATH = 'floodvoice.db'
FLOODNET_UPDATE_INTERVAL = 300  # 5 minutes

# Import flood dashboard functionality
from flood_dashboard import FloodDashboardData

# Initialize flood data manager
flood_data = FloodDashboardData(DATABASE_PATH)

# ============================================================================
# SUPABASE CONNECTION - Josue's live data
# ============================================================================

SUPABASE_URL = "https://mbavifzuiiyewengxrpu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1iYXZpZnp1aWl5ZXdlbmd4cnB1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ5NDQ4MDUsImV4cCI6MjA4MDUyMDgwNX0.opye6RBgRQv2GisAawuNkHaymM3or2W2qMbptcJYzlc"

def fetch_from_supabase(table, order_by=None):
    """Fetch data from Josue's Supabase database"""
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    if order_by:
        url += f"&order={order_by}.desc"
    
    req = urllib.request.Request(url)
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        logger.error(f"Supabase fetch error: {e}")
        return []

@app.route('/api/residents')
def get_residents():
    """Get residents with their latest call log data"""
    try:
        residents = fetch_from_supabase("residents")
        call_logs = fetch_from_supabase("call_logs", order_by="created_at")
        
        # Match each resident to their latest call log
        latest_calls = {}
        for call in call_logs:
            rid = call.get("resident_id")
            if rid not in latest_calls:
                latest_calls[rid] = call
        
        # Build combined resident + call data
        combined = []
        for r in residents:
            call = latest_calls.get(r["id"], {})
            combined.append({
                "id": r["id"],
                "name": r.get("name", "Unknown"),
                "address": r.get("address", "N/A"),
                "language": r.get("language", "N/A"),
                "status": r.get("status", "UNKNOWN"),
                "urgency_score": call.get("sentiment_score", 0) or 0,
                "risk_label": call.get("risk_label", "N/A"),
                "summary": call.get("summary", "No call yet"),
                "last_called": call.get("created_at", "Never")[:16].replace("T", " ") if call.get("created_at") else "Never"
            })
        
        # Sort by urgency — highest first
        combined.sort(key=lambda x: x["urgency_score"], reverse=True)
        
        return jsonify({"success": True, "residents": combined})
    
    except Exception as e:
        logger.error(f"Error fetching residents: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    
# ============================================================================
# ROUTES - Web Pages
# ============================================================================

@app.route('/')
def index():
    """Main FloodVoice dashboard"""
    return render_template('flood_dashboard.html')


@app.route('/historical')
def historical():
    """Historical flood analysis view"""
    return render_template('historical.html')


@app.route('/about')
def about():
    """About FloodVoice page"""
    return render_template('about.html')


# ============================================================================
# API ROUTES - Data Endpoints
# ============================================================================

@app.route('/api/flood-data')
def get_flood_data():
    """
    Get current flood situation data
    Returns: sensor readings, community reports, correlations, insights
    """
    try:
        # Get social media flood reports (last 24 hours)
        social_reports = flood_data.get_social_media_flood_reports(hours_back=24)
        
        # Get FloodNet sensor data
        sensor_data = flood_data.simulate_floodnet_data()
        
        # Correlate reports with sensors
        correlations = flood_data.correlate_reports_with_sensors(social_reports, sensor_data)
        
        # Get FEMA risk analysis
        fema_analysis = flood_data.get_fema_risk_analysis()
        
        # Generate AI insights
        insights = flood_data.generate_flood_insights(correlations, sensor_data)
        
        return jsonify({
            'success': True,
            'data': {
                'social_reports': social_reports.to_dict('records') if not social_reports.empty else [],
                'sensor_data': sensor_data,
                'correlations': correlations,
                'fema_analysis': fema_analysis,
                'insights': insights,
                'summary': {
                    'total_reports': len(social_reports),
                    'active_sensors': len(sensor_data),
                    'correlations_found': len(correlations),
                    'flooding_detected': len([s for s in sensor_data if s['flood_depth_inches'] > 2])
                }
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting flood data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sensors')
def get_sensors():
    """Get all FloodNet sensor locations and current readings"""
    try:
        sensor_data = flood_data.simulate_floodnet_data()
        return jsonify({
            'success': True,
            'sensors': sensor_data,
            'count': len(sensor_data)
        })
    except Exception as e:
        logger.error(f"Error getting sensors: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/community-reports')
def get_community_reports():
    """Get recent community flood reports"""
    try:
        hours_back = request.args.get('hours', 24, type=int)
        reports = flood_data.get_social_media_flood_reports(hours_back=hours_back)
        
        return jsonify({
            'success': True,
            'reports': reports.to_dict('records') if not reports.empty else [],
            'count': len(reports)
        })
    except Exception as e:
        logger.error(f"Error getting community reports: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/correlations')
def get_correlations():
    """Get sensor-report correlations"""
    try:
        social_reports = flood_data.get_social_media_flood_reports(hours_back=24)
        sensor_data = flood_data.simulate_floodnet_data()
        correlations = flood_data.correlate_reports_with_sensors(social_reports, sensor_data)
        
        return jsonify({
            'success': True,
            'correlations': correlations,
            'count': len(correlations)
        })
    except Exception as e:
        logger.error(f"Error getting correlations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fema-zones')
def get_fema_zones():
    """Get FEMA flood risk zones"""
    try:
        fema_analysis = flood_data.get_fema_risk_analysis()
        return jsonify({
            'success': True,
            'fema_zones': fema_analysis
        })
    except Exception as e:
        logger.error(f"Error getting FEMA zones: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# PARTNER API - Wellness Check Integration
# ============================================================================

@app.route('/api/trigger-wellness-checks', methods=['POST'])
def trigger_wellness_checks():
    """
    Partner API endpoint to trigger wellness check campaigns
    Called when flood event is detected in vulnerable area
    """
    try:
        data = request.json
        flood_event_id = data.get('flood_event_id')
        affected_zipcodes = data.get('affected_zipcodes', [])
        severity = data.get('severity', 'moderate')
        
        # TODO: Implement wellness check campaign creation
        # For now, return mock response
        
        campaign_id = f"wc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'flood_event_id': flood_event_id,
            'affected_zipcodes': affected_zipcodes,
            'severity': severity,
            'residents_to_contact': 250,  # Mock value
            'calls_initiated': 250,
            'status': 'in_progress'
        })
        
    except Exception as e:
        logger.error(f"Error triggering wellness checks: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/wellness-check-result', methods=['POST'])
def receive_wellness_check_result():
    """
    Webhook for partner system to report call results
    """
    try:
        data = request.json
        campaign_id = data.get('campaign_id')
        resident_id = data.get('resident_id')
        call_status = data.get('status')  # completed, no_answer, needs_help
        notes = data.get('notes', '')
        
        # TODO: Store call results in database
        
        logger.info(f"Wellness check result: Campaign {campaign_id}, Resident {resident_id}, Status: {call_status}")
        
        return jsonify({
            'success': True,
            'message': 'Result recorded'
        })
        
    except Exception as e:
        logger.error(f"Error receiving wellness check result: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# WEBSOCKET EVENTS - Real-time Updates
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected to FloodVoice')
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected from FloodVoice')


@socketio.on('request_flood_update')
def handle_flood_update_request():
    """Handle request for flood data update"""
    try:
        social_reports = flood_data.get_social_media_flood_reports(hours_back=24)
        sensor_data = flood_data.simulate_floodnet_data()
        correlations = flood_data.correlate_reports_with_sensors(social_reports, sensor_data)
        
        emit('flood_update', {
            'sensor_data': sensor_data,
            'correlations': correlations[:10],  # Send top 10
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error sending flood update: {e}")
        emit('error', {'message': str(e)})


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("🌊 Starting FloodVoice - Community-Centered Flood Response Platform")
    logger.info(f"Database: {DATABASE_PATH}")
    logger.info(f"FloodNet update interval: {FLOODNET_UPDATE_INTERVAL} seconds")
    
    # Run with SocketIO
    socketio.run(
        app,
        debug=True,
        host='0.0.0.0',
        port=5000
    )

