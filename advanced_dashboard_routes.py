#!/usr/bin/env python3
"""
Advanced Dashboard Routes for Public Health MVP
API endpoints for the advanced filtering and visualization system
"""

from flask import Blueprint, render_template, request, jsonify, Response
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import json
import os
from advanced_map_system import AdvancedMapSystem
from choropleth_map_system import ChoroplethMapSystem

# Create blueprint
advanced_bp = Blueprint('advanced', __name__)

# Initialize map systems
map_system = AdvancedMapSystem()
choropleth_system = ChoroplethMapSystem()

@advanced_bp.route('/advanced-dashboard')
def advanced_dashboard():
    """Render the advanced dashboard page"""
    
    try:
        # Get summary statistics
        conn = sqlite3.connect('public_health_data.db')
        
        # Get total cases across all data sources
        covid_total = pd.read_sql_query("SELECT SUM(CASE_COUNT) as total FROM nyc_covid_data WHERE CASE_COUNT IS NOT NULL", conn).iloc[0]['total'] or 0
        flu_total = pd.read_sql_query("SELECT SUM(flu_like_visits) as total FROM flu_surveillance_data", conn).iloc[0]['total'] or 0
        hospital_total = pd.read_sql_query("SELECT SUM(total_visits) as total FROM real_hospital_data", conn).iloc[0]['total'] or 0
        
        total_cases = int(covid_total + flu_total + hospital_total)
        
        # Get active alerts count (patterns detected in last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        active_alerts = pd.read_sql_query(f"SELECT COUNT(*) as count FROM pattern_detections WHERE detection_timestamp >= '{week_ago}'", conn).iloc[0]['count'] or 0
        
        # Get last updated date
        last_updated = pd.read_sql_query("SELECT MAX(date_of_interest) as latest FROM nyc_covid_data", conn).iloc[0]['latest']
        
        conn.close()
        
        return render_template('advanced_dashboard.html',
                             total_cases=f"{total_cases:,}",
                             active_alerts=active_alerts,
                             data_sources=7,
                             last_updated=last_updated)
    
    except Exception as e:
        print(f"Error loading advanced dashboard: {e}")
        return render_template('advanced_dashboard.html',
                             total_cases="0",
                             active_alerts=0,
                             data_sources=7,
                             last_updated="Unknown")

@advanced_bp.route('/api/map-data', methods=['POST'])
def get_map_data():
    """Get filtered map data for all illness types"""
    
    try:
        filters = request.get_json()
        
        # Extract filter parameters
        illness_types = filters.get('illnessTypes', [])
        date_range = filters.get('dateRange', '30')
        borough = filters.get('borough', '')
        zip_code = filters.get('zipCode', '')
        risk_levels = filters.get('riskLevels', [])
        
        # Convert date range to actual dates
        date_filter = get_date_range_filter(date_range)
        
        # Get map data using the advanced map system
        map_data = map_system.export_map_data(
            illness_filters=illness_types,
            date_range=date_filter,
            borough_filter=borough if borough else None
        )
        
        # Get statistics
        stats = get_filtered_statistics(filters)
        
        # Get chart data
        chart_data = get_chart_data(filters)
        
        # Get table data
        table_data = get_table_data(filters)
        
        # Check for alerts
        alerts = get_health_alerts(filters)
        
        return jsonify({
            'success': True,
            'map_data': map_data,
            'stats': stats,
            'chart_data': chart_data,
            'table_data': table_data,
            'alerts': alerts
        })
    
    except Exception as e:
        print(f"Error getting map data: {e}")
        return jsonify({'success': False, 'error': str(e)})

@advanced_bp.route('/api/map-layer/<illness_type>', methods=['POST'])
def get_map_layer(illness_type):
    """Get specific illness type layer data"""
    
    try:
        filters = request.get_json()
        
        # Get layer data based on illness type
        layer_data = []
        
        conn = sqlite3.connect('public_health_data.db')
        
        if illness_type == 'COVID-19':
            layer_data = get_covid_layer_data(conn, filters)
        elif illness_type == 'Flu':
            layer_data = get_flu_layer_data(conn, filters)
        elif illness_type == 'Foodborne':
            layer_data = get_foodborne_layer_data(conn, filters)
        elif illness_type == 'Air Quality':
            layer_data = get_air_quality_layer_data(conn, filters)
        elif illness_type == 'Hospital ER':
            layer_data = get_hospital_layer_data(conn, filters)
        elif illness_type == 'Tick Disease':
            layer_data = get_tick_disease_layer_data(conn, filters)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'layer_data': layer_data
        })
    
    except Exception as e:
        print(f"Error getting {illness_type} layer: {e}")
        return jsonify({'success': False, 'error': str(e)})

@advanced_bp.route('/api/chart-data', methods=['POST'])
def get_chart_data():
    """Get chart data for filtered results"""
    
    try:
        filters = request.get_json()
        
        conn = sqlite3.connect('public_health_data.db')
        
        # Get illness distribution data
        illness_distribution = get_illness_distribution(conn, filters)
        
        # Get trend data
        trend_data = get_trend_data(conn, filters)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'illness_distribution': illness_distribution,
            'trend_data': trend_data
        })
    
    except Exception as e:
        print(f"Error getting chart data: {e}")
        return jsonify({'success': False, 'error': str(e)})

@advanced_bp.route('/api/table-data', methods=['POST'])
def get_table_data():
    """Get table data for filtered results"""
    
    try:
        filters = request.get_json()
        table_data = get_filtered_table_data(filters)
        
        return jsonify({
            'success': True,
            'table_data': table_data
        })
    
    except Exception as e:
        print(f"Error getting table data: {e}")
        return jsonify({'success': False, 'error': str(e)})

@advanced_bp.route('/api/export/map-data')
def export_map_data():
    """Export map data as JSON"""
    
    try:
        # Get current filters from session or use defaults
        filters = {
            'illnessTypes': ['COVID-19', 'Flu', 'Foodborne', 'Air Quality', 'Hospital ER', 'Tick Disease'],
            'dateRange': '30',
            'borough': '',
            'zipCode': '',
            'riskLevels': ['LOW', 'MEDIUM', 'HIGH', 'HAZARDOUS']
        }
        
        # Get map data
        date_filter = get_date_range_filter(filters['dateRange'])
        map_data = map_system.export_map_data(
            illness_filters=filters['illnessTypes'],
            date_range=date_filter,
            borough_filter=filters['borough'] if filters['borough'] else None
        )
        
        # Create response
        response = Response(
            json.dumps(map_data, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=nyc_health_map_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'}
        )
        
        return response
    
    except Exception as e:
        print(f"Error exporting map data: {e}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/choropleth-map/<illness_type>')
def choropleth_map(illness_type):
    """Generate and serve choropleth map for specific illness type"""

    try:
        # Get filter parameters from query string
        date_range = request.args.get('date_range', '30')
        borough = request.args.get('borough', '')

        # Convert date range
        date_filter = get_date_range_filter(date_range)

        # Create choropleth map
        choropleth_map = choropleth_system.create_choropleth_map(
            illness_type=illness_type,
            date_range=date_filter,
            borough_filter=borough if borough else None
        )

        if choropleth_map:
            # Save map to temporary file
            map_filename = f'temp_choropleth_{illness_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            map_path = os.path.join('static', map_filename)
            choropleth_map.save(map_path)

            # Return map HTML
            return choropleth_map._repr_html_()
        else:
            return jsonify({'error': 'Failed to create choropleth map'}), 500

    except Exception as e:
        print(f"Error creating choropleth map: {e}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/multi-choropleth-map')
def multi_choropleth_map():
    """Generate and serve multi-illness choropleth map"""

    try:
        # Get filter parameters
        illness_types = request.args.getlist('illness_types')
        if not illness_types:
            illness_types = ['COVID-19', 'Flu', 'Foodborne', 'Air Quality']

        date_range = request.args.get('date_range', '30')
        borough = request.args.get('borough', '')

        # Convert date range
        date_filter = get_date_range_filter(date_range)

        # Create multi-illness choropleth map
        multi_map = choropleth_system.create_multi_illness_choropleth(
            illness_types=illness_types,
            date_range=date_filter,
            borough_filter=borough if borough else None
        )

        if multi_map:
            # Return map HTML
            return multi_map._repr_html_()
        else:
            return jsonify({'error': 'Failed to create multi-choropleth map'}), 500

    except Exception as e:
        print(f"Error creating multi-choropleth map: {e}")
        return jsonify({'error': str(e)}), 500

@advanced_bp.route('/api/choropleth-data/<illness_type>')
def get_choropleth_data(illness_type):
    """Get choropleth data for specific illness type"""

    try:
        # Get filter parameters
        date_range = request.args.get('date_range', '30')
        borough = request.args.get('borough', '')

        # Convert date range
        date_filter = get_date_range_filter(date_range)

        # Get choropleth data
        choropleth_data = choropleth_system.export_choropleth_data(
            illness_type=illness_type,
            date_range=date_filter,
            borough_filter=borough if borough else None
        )

        return jsonify({
            'success': True,
            'choropleth_data': choropleth_data
        })

    except Exception as e:
        print(f"Error getting choropleth data: {e}")
        return jsonify({'success': False, 'error': str(e)})

@advanced_bp.route('/api/export/table-data')
def export_table_data():
    """Export table data as CSV"""
    
    try:
        # Get current filters from session or use defaults
        filters = {
            'illnessTypes': ['COVID-19', 'Flu', 'Foodborne', 'Air Quality', 'Hospital ER', 'Tick Disease'],
            'dateRange': '30',
            'borough': '',
            'zipCode': '',
            'riskLevels': ['LOW', 'MEDIUM', 'HIGH', 'HAZARDOUS']
        }
        
        # Get table data
        table_data = get_filtered_table_data(filters)
        
        # Convert to DataFrame and CSV
        df = pd.DataFrame(table_data)
        csv_data = df.to_csv(index=False)
        
        # Create response
        response = Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=nyc_health_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        
        return response
    
    except Exception as e:
        print(f"Error exporting table data: {e}")
        return jsonify({'error': str(e)}), 500

# Helper functions

def get_date_range_filter(date_range):
    """Convert date range string to actual date range"""
    
    if date_range == 'all':
        return None
    
    try:
        days = int(date_range)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        return [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
    except:
        return None

def get_filtered_statistics(filters):
    """Get statistics for filtered data"""
    
    try:
        conn = sqlite3.connect('public_health_data.db')
        
        # Calculate filtered statistics
        total_cases = 0
        active_alerts = 0
        
        # Add logic to calculate based on filters
        # This is a simplified version
        
        conn.close()
        
        return {
            'total_cases': f"{total_cases:,}",
            'active_alerts': active_alerts,
            'data_sources': len(filters.get('illnessTypes', [])),
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
    
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {
            'total_cases': '0',
            'active_alerts': 0,
            'data_sources': 0,
            'last_updated': 'Unknown'
        }

def get_covid_layer_data(conn, filters):
    """Get COVID layer data points"""
    
    # Simplified implementation - you would expand this
    layer_data = []
    
    # Borough coordinates
    borough_coords = {
        'Bronx': [40.8448, -73.8648],
        'Brooklyn': [40.6782, -73.9442],
        'Manhattan': [40.7831, -73.9712],
        'Queens': [40.7282, -73.7949],
        'Staten Island': [40.5795, -74.1502]
    }
    
    for borough, coords in borough_coords.items():
        layer_data.append({
            'lat': coords[0],
            'lng': coords[1],
            'size': 15,
            'color': '#FF6B6B',
            'borderColor': '#E74C3C',
            'popup': f'<h5>{borough} - COVID-19</h5><p>Sample data point</p>'
        })
    
    return layer_data

def get_flu_layer_data(conn, filters):
    """Get flu layer data points"""
    # Implementation similar to COVID but for flu data
    return []

def get_foodborne_layer_data(conn, filters):
    """Get foodborne illness layer data points"""
    # Implementation for foodborne data
    return []

def get_air_quality_layer_data(conn, filters):
    """Get air quality layer data points"""
    # Implementation for air quality data
    return []

def get_hospital_layer_data(conn, filters):
    """Get hospital ER layer data points"""
    # Implementation for hospital data
    return []

def get_tick_disease_layer_data(conn, filters):
    """Get tick disease layer data points"""
    # Implementation for tick disease data
    return []

def get_illness_distribution(conn, filters):
    """Get illness distribution for pie chart"""
    
    return {
        'values': [100, 80, 60, 40, 30, 20]  # Sample data
    }

def get_trend_data(conn, filters):
    """Get trend data for line chart"""
    
    return {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'datasets': [{
            'label': 'COVID-19',
            'data': [10, 20, 15, 25, 30, 20],
            'borderColor': '#FF6B6B',
            'backgroundColor': 'rgba(255, 107, 107, 0.1)'
        }]
    }

def get_filtered_table_data(filters):
    """Get filtered data for the table"""
    
    # Sample data - you would implement actual filtering
    return [
        {
            'id': '1',
            'date': '2025-06-15',
            'location': 'Manhattan',
            'illness_type': 'COVID-19',
            'value': '150 cases',
            'risk_level': 'MEDIUM',
            'color': '#FF6B6B'
        }
    ]

def get_health_alerts(filters):
    """Get health alerts based on filters"""
    
    # Sample alerts - you would implement actual alert detection
    return [
        {
            'title': 'Flu Spike Detected',
            'description': 'Unusual increase in flu cases in Queens area'
        }
    ]
