#!/usr/bin/env python3
"""
Advanced Dashboard Routes for Public Health MVP
API endpoints for the advanced filtering and visualization system
"""

from flask import Blueprint, render_template, request, jsonify, Response, make_response
from flask_login import login_required, current_user
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
@login_required
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
@login_required
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
        chart_data = {
            'illness_distribution': get_illness_distribution(sqlite3.connect('public_health_data.db'), filters),
            'trend_data': get_trend_data(sqlite3.connect('public_health_data.db'), filters)
        }

        # Get table data
        table_data = get_filtered_table_data(filters)

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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def choropleth_map(illness_type):
    """Generate and serve choropleth map for specific illness type"""

    try:
        print(f"🗺️ Creating choropleth map for {illness_type}")

        # 1. RECEIVED FILTER PARAMETERS - Log exact request.args
        print(f"📥 RECEIVED FILTER PARAMETERS:")
        print(f"   request.args: {dict(request.args)}")

        # Get filter parameters from query string
        date_range = request.args.get('date_range', '30')
        borough = request.args.get('borough', '')
        zip_code = request.args.get('zip_code', '')

        print(f"   Parsed filters: date_range={date_range}, borough={borough}, zip_code={zip_code}")

        # Convert date range
        date_filter = get_date_range_filter(date_range)
        print(f"   Converted date_filter: {date_filter}")

        # 2. HEALTH DATA DATAFRAME - Check data fetching
        print(f"📊 FETCHING HEALTH DATA:")
        illness_data = choropleth_system.get_illness_data_by_zip(
            illness_type=illness_type,
            date_range=date_filter,
            borough_filter=borough if borough else None
        )

        print(f"   DataFrame type: {type(illness_data)}")
        print(f"   DataFrame length: {len(illness_data)}")
        print(f"   DataFrame empty: {illness_data.empty}")

        if not illness_data.empty:
            print(f"   DataFrame columns: {list(illness_data.columns)}")
            print(f"   DataFrame head():")
            print(illness_data.head())
        else:
            print(f"   ⚠️ DataFrame is EMPTY - no data found!")

        # KEY REFINEMENT: Data availability detection for better user experience
        # This refinement was added to solve the problem where users would see blank maps
        # without knowing if it was a loading issue or genuinely no data available.
        # By detecting data availability here and passing it via custom headers,
        # the frontend can show appropriate "No data available" messages instead of
        # leaving users confused with empty visualizations.
        data_found = not illness_data.empty
        print(f"   Data found for {illness_type}: {data_found} ({len(illness_data)} records)")

        # 3. GEOJSON STATE - Check GeoJSON before map creation
        print(f"🗺️ CHECKING GEOJSON STATE:")

        # Access the zip_boundaries from choropleth_system
        zip_boundaries = choropleth_system.zip_boundaries
        print(f"   zip_boundaries type: {type(zip_boundaries)}")

        if zip_boundaries:
            print(f"   zip_boundaries length: {len(zip_boundaries.get('features', []))}")

            # Check filtered GeoJSON (NYC filtering)
            filtered_geojson = choropleth_system.filter_nyc_zip_codes(borough=borough if borough else None, zip_code=zip_code if zip_code else None)
            print(f"   filtered_geojson type: {type(filtered_geojson)}")

            if filtered_geojson:
                print(f"   filtered_geojson length: {len(filtered_geojson.get('features', []))}")
            else:
                print(f"   ⚠️ filtered_geojson is None!")
        else:
            print(f"   ⚠️ zip_boundaries is None!")

        # Create choropleth map (ZIP code filtering handled in data queries)
        print(f"🎨 CREATING CHOROPLETH MAP:")
        choropleth_map = choropleth_system.create_choropleth_map(
            illness_type=illness_type,
            date_range=date_filter,
            borough_filter=borough if borough else None
        )

        # 4. FINAL CHECK - Verify DataFrame before Folium.Choropleth call
        print(f"✅ FINAL DATA CHECK BEFORE FOLIUM:")
        if not illness_data.empty:
            print(f"   Final DataFrame columns: {list(illness_data.columns)}")
            print(f"   Final DataFrame shape: {illness_data.shape}")
            print(f"   Final DataFrame head():")
            print(illness_data.head())

            # Check for required columns
            required_cols = ['area', 'value']
            missing_cols = [col for col in required_cols if col not in illness_data.columns]
            if missing_cols:
                print(f"   ⚠️ MISSING REQUIRED COLUMNS: {missing_cols}")
            else:
                print(f"   ✅ All required columns present: {required_cols}")
        else:
            print(f"   ⚠️ DataFrame is still EMPTY before map creation!")

        if choropleth_map:
            print(f"✅ Choropleth map created successfully for {illness_type}")

            # Save map to temporary file
            map_filename = f'temp_choropleth_{illness_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
            map_path = os.path.join('static', map_filename)
            choropleth_map.save(map_path)

            # KEY REFINEMENT: Custom header communication between backend and frontend
            # This refinement implements a clean separation of concerns where the backend
            # detects data availability and communicates it to the frontend via HTTP headers.
            # The frontend JavaScript can then read the 'X-Data-Found' header to decide
            # whether to show the map or display a "No data available" message.
            # This approach is more reliable than trying to detect empty maps in JavaScript.
            response = make_response(choropleth_map._repr_html_())
            response.headers['X-Data-Found'] = 'true' if data_found else 'false'
            response.headers['Content-Type'] = 'text/html'

            print(f"🎯 RESPONSE CREATED:")
            print(f"   Map HTML length: {len(choropleth_map._repr_html_())}")
            print(f"   X-Data-Found header: {response.headers.get('X-Data-Found')}")

            return response
        else:
            print(f"❌ Failed to create choropleth map for {illness_type}")
            print(f"   choropleth_map is None - map creation failed!")
            return jsonify({'error': 'Failed to create choropleth map - no data available'}), 500

    except Exception as e:
        print(f"❌ ERROR creating choropleth map for {illness_type}: {e}")
        import traceback
        print(f"📋 FULL TRACEBACK:")
        traceback.print_exc()
        return jsonify({'error': f'Choropleth error: {str(e)}'}), 500

@advanced_bp.route('/multi-choropleth-map')
@login_required
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
@login_required
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
@login_required
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

        # Extract filter parameters
        illness_types = filters.get('illnessTypes', [])
        date_range = filters.get('dateRange', '30')
        borough = filters.get('borough', '')
        zip_code = filters.get('zipCode', '')

        # Convert date range
        date_filter = get_date_range_filter(date_range)

        total_cases = 0
        active_alerts = 0

        # Calculate COVID cases if selected
        if 'COVID-19' in illness_types:
            # Try new COVID daily counts table first, then fall back to old data
            if borough:
                # Query specific borough from new COVID daily counts
                borough_col_map = {
                    'Bronx': 'bx_case_count',
                    'Brooklyn': 'bk_case_count',
                    'Manhattan': 'mn_case_count',
                    'Queens': 'qn_case_count',
                    'Staten Island': 'si_case_count'
                }

                if borough in borough_col_map:
                    covid_query = f"""
                        SELECT SUM({borough_col_map[borough]}) as total_covid
                        FROM covid_daily_counts
                        WHERE {borough_col_map[borough]} IS NOT NULL
                    """
                    if date_filter:
                        covid_query += f" AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'"

                    covid_result = pd.read_sql_query(covid_query, conn)
                    if not covid_result.empty and covid_result.iloc[0]['total_covid']:
                        total_cases += int(covid_result.iloc[0]['total_covid'])
                    else:
                        # Fallback to old data
                        old_borough_col_map = {
                            'Bronx': 'BX_CASE_COUNT',
                            'Brooklyn': 'BK_CASE_COUNT',
                            'Manhattan': 'MN_CASE_COUNT',
                            'Queens': 'QN_CASE_COUNT',
                            'Staten Island': 'SI_CASE_COUNT'
                        }
                        fallback_query = f"""
                            SELECT SUM({old_borough_col_map[borough]}) as total_covid
                            FROM nyc_covid_data
                            WHERE {old_borough_col_map[borough]} IS NOT NULL
                        """
                        if date_filter:
                            fallback_query += f" AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'"

                        fallback_result = pd.read_sql_query(fallback_query, conn)
                        if not fallback_result.empty and fallback_result.iloc[0]['total_covid']:
                            total_cases += int(fallback_result.iloc[0]['total_covid'])
            else:
                # Query all boroughs from new COVID daily counts
                covid_query = """
                    SELECT SUM(case_count) as total_covid
                    FROM covid_daily_counts
                    WHERE case_count IS NOT NULL
                """
                if date_filter:
                    covid_query += f" AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'"

                covid_result = pd.read_sql_query(covid_query, conn)
                if not covid_result.empty and covid_result.iloc[0]['total_covid']:
                    total_cases += int(covid_result.iloc[0]['total_covid'])
                else:
                    # Fallback to old data
                    fallback_query = """
                        SELECT SUM(CASE_COUNT) as total_covid
                        FROM nyc_covid_data
                        WHERE CASE_COUNT IS NOT NULL
                    """
                    if date_filter:
                        fallback_query += f" AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'"

                    fallback_result = pd.read_sql_query(fallback_query, conn)
                    if not fallback_result.empty and fallback_result.iloc[0]['total_covid']:
                        total_cases += int(fallback_result.iloc[0]['total_covid'])

        # Calculate Hospital ER visits if selected
        if 'Hospital ER' in illness_types:
            hospital_query = """
                SELECT SUM(respiratory_visits) as total_er
                FROM real_hospital_data
                WHERE 1=1
            """
            if date_filter:
                hospital_query += f" AND date >= '{date_filter[0]}' AND date <= '{date_filter[1]}'"
            if borough:
                hospital_query += f" AND borough = '{borough}'"
            if zip_code:
                hospital_query += f" AND zip_code = '{zip_code}'"

            hospital_result = pd.read_sql_query(hospital_query, conn)
            if not hospital_result.empty and hospital_result.iloc[0]['total_er']:
                total_cases += int(hospital_result.iloc[0]['total_er'])

        # Calculate Foodborne cases if selected
        if 'Foodborne' in illness_types:
            foodborne_query = """
                SELECT COUNT(*) as total_foodborne
                FROM restaurant_inspection_data
                WHERE is_high_risk_foodborne = 1
            """

            if date_filter:
                foodborne_query += f" AND date >= '{date_filter[0]}' AND date <= '{date_filter[1]}'"
            if borough:
                foodborne_query += f" AND borough = '{borough}'"
            if zip_code:
                foodborne_query += f" AND zip_code = '{zip_code}'"

            foodborne_result = pd.read_sql_query(foodborne_query, conn)
            if not foodborne_result.empty and foodborne_result.iloc[0]['total_foodborne']:
                total_cases += int(foodborne_result.iloc[0]['total_foodborne'])

        # Count active alerts (patterns detected recently)
        alert_query = """
            SELECT COUNT(*) as alert_count
            FROM pattern_detections
            WHERE detection_timestamp >= datetime('now', '-7 days')
        """
        if borough:
            # Extract borough from hospital_name or use zip_code mapping
            alert_query += f" AND (hospital_name LIKE '%{borough}%' OR zip_code IN (SELECT zip_code FROM real_hospital_data WHERE borough = '{borough}'))"
        if zip_code:
            alert_query += f" AND zip_code = '{zip_code}'"

        alert_result = pd.read_sql_query(alert_query, conn)
        if not alert_result.empty:
            active_alerts = int(alert_result.iloc[0]['alert_count'])

        conn.close()

        return {
            'total_cases': f"{total_cases:,}",
            'active_alerts': active_alerts,
            'data_sources': len(illness_types),
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
    """Get COVID layer data points with actual filtering"""

    try:
        # Extract filter parameters
        date_range = filters.get('dateRange', '30')
        borough = filters.get('borough', '')
        zip_code = filters.get('zipCode', '')

        # Convert date range
        date_filter = get_date_range_filter(date_range)

        # Query COVID data with filters (COVID data is borough-based, not ZIP-based)
        if borough:
            # Query specific borough
            borough_col_map = {
                'Bronx': 'BX_CASE_COUNT',
                'Brooklyn': 'BK_CASE_COUNT',
                'Manhattan': 'MN_CASE_COUNT',
                'Queens': 'QN_CASE_COUNT',
                'Staten Island': 'SI_CASE_COUNT'
            }

            if borough in borough_col_map:
                query = f"""
                    SELECT '{borough}' as borough,
                           SUM({borough_col_map[borough]}) as total_cases,
                           AVG({borough_col_map[borough]}) as avg_cases
                    FROM nyc_covid_data
                    WHERE {borough_col_map[borough]} IS NOT NULL
                """
                if date_filter:
                    query += f" AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'"
            else:
                # Invalid borough
                return []
        else:
            # Query all boroughs
            query = """
                SELECT 'Bronx' as borough, SUM(BX_CASE_COUNT) as total_cases, AVG(BX_CASE_COUNT) as avg_cases
                FROM nyc_covid_data WHERE BX_CASE_COUNT IS NOT NULL
                UNION ALL
                SELECT 'Brooklyn' as borough, SUM(BK_CASE_COUNT) as total_cases, AVG(BK_CASE_COUNT) as avg_cases
                FROM nyc_covid_data WHERE BK_CASE_COUNT IS NOT NULL
                UNION ALL
                SELECT 'Manhattan' as borough, SUM(MN_CASE_COUNT) as total_cases, AVG(MN_CASE_COUNT) as avg_cases
                FROM nyc_covid_data WHERE MN_CASE_COUNT IS NOT NULL
                UNION ALL
                SELECT 'Queens' as borough, SUM(QN_CASE_COUNT) as total_cases, AVG(QN_CASE_COUNT) as avg_cases
                FROM nyc_covid_data WHERE QN_CASE_COUNT IS NOT NULL
                UNION ALL
                SELECT 'Staten Island' as borough, SUM(SI_CASE_COUNT) as total_cases, AVG(SI_CASE_COUNT) as avg_cases
                FROM nyc_covid_data WHERE SI_CASE_COUNT IS NOT NULL
            """
            if date_filter:
                # This is more complex with UNION, so we'll filter in a subquery
                query = f"""
                SELECT * FROM (
                    SELECT 'Bronx' as borough, SUM(BX_CASE_COUNT) as total_cases, AVG(BX_CASE_COUNT) as avg_cases
                    FROM nyc_covid_data WHERE BX_CASE_COUNT IS NOT NULL AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'
                    UNION ALL
                    SELECT 'Brooklyn' as borough, SUM(BK_CASE_COUNT) as total_cases, AVG(BK_CASE_COUNT) as avg_cases
                    FROM nyc_covid_data WHERE BK_CASE_COUNT IS NOT NULL AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'
                    UNION ALL
                    SELECT 'Manhattan' as borough, SUM(MN_CASE_COUNT) as total_cases, AVG(MN_CASE_COUNT) as avg_cases
                    FROM nyc_covid_data WHERE MN_CASE_COUNT IS NOT NULL AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'
                    UNION ALL
                    SELECT 'Queens' as borough, SUM(QN_CASE_COUNT) as total_cases, AVG(QN_CASE_COUNT) as avg_cases
                    FROM nyc_covid_data WHERE QN_CASE_COUNT IS NOT NULL AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'
                    UNION ALL
                    SELECT 'Staten Island' as borough, SUM(SI_CASE_COUNT) as total_cases, AVG(SI_CASE_COUNT) as avg_cases
                    FROM nyc_covid_data WHERE SI_CASE_COUNT IS NOT NULL AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'
                ) WHERE total_cases > 0
                """

        df = pd.read_sql_query(query, conn)

        layer_data = []

        # Borough coordinates
        borough_coords = {
            'Bronx': [40.8448, -73.8648],
            'Brooklyn': [40.6782, -73.9442],
            'Manhattan': [40.7831, -73.9712],
            'Queens': [40.7282, -73.7949],
            'Staten Island': [40.5795, -74.1502]
        }

        for _, row in df.iterrows():
            borough_name = row['borough']

            # Get coordinates
            coords = borough_coords.get(borough_name, [40.7831, -73.9712])

            # Calculate marker size based on case count
            total_cases = int(row['total_cases']) if row['total_cases'] else 0
            marker_size = min(40, max(15, total_cases / 1000))  # Adjusted for borough-level data

            # Determine color intensity based on cases
            if total_cases > 50000:
                color = '#CC0000'  # Dark red
            elif total_cases > 20000:
                color = '#FF4D4D'  # Medium red
            elif total_cases > 5000:
                color = '#FF8080'  # Light red
            else:
                color = '#FFB3B3'  # Very light red

            layer_data.append({
                'lat': coords[0],
                'lng': coords[1],
                'size': marker_size,
                'color': color,
                'borderColor': '#E74C3C',
                'popup': f'''
                    <div style="width: 200px">
                        <h5 style="color: #FF6B6B">{borough_name} - COVID-19</h5>
                        <p><strong>Borough:</strong> {borough_name}</p>
                        <p><strong>Total Cases:</strong> {total_cases:,}</p>
                        <p><strong>Avg Daily:</strong> {row['avg_cases']:.1f}</p>
                    </div>
                '''
            })

        return layer_data

    except Exception as e:
        print(f"Error getting COVID layer data: {e}")
        return []

def get_flu_layer_data(conn, filters):
    """Get flu layer data points with coordinates"""
    try:
        # Extract filter parameters
        date_range = filters.get('dateRange', '30')
        borough = filters.get('borough', '')
        zip_code = filters.get('zipCode', '')

        # Convert date range
        date_filter = get_date_range_filter(date_range)

        # Query flu surveillance data
        query = """
            SELECT zip_code, borough,
                   AVG(flu_percentage) as avg_flu_rate,
                   SUM(flu_like_visits) as total_flu_visits
            FROM flu_surveillance_data
            WHERE 1=1
        """

        if date_filter:
            query += f" AND date >= '{date_filter[0]}' AND date <= '{date_filter[1]}'"
        if borough:
            query += f" AND borough = '{borough}'"
        if zip_code:
            query += f" AND zip_code = '{zip_code}'"

        query += " GROUP BY zip_code, borough"

        df = pd.read_sql_query(query, conn)

        if df.empty:
            return []

        # Add coordinates and format for map display
        layer_data = []

        # ZIP code coordinates mapping
        zip_coords = {
            '10001': [40.7505, -73.9934],  # Manhattan
            '10451': [40.8176, -73.9482],  # Bronx
            '11101': [40.7505, -73.9365],  # Queens
            '11201': [40.6892, -73.9442],  # Brooklyn
            '10301': [40.6323, -74.0754],  # Staten Island
            # Add more as needed
        }

        # Borough center coordinates as fallback
        borough_coords = {
            'Bronx': [40.8448, -73.8648],
            'Brooklyn': [40.6782, -73.9442],
            'Manhattan': [40.7831, -73.9712],
            'Queens': [40.7282, -73.7949],
            'Staten Island': [40.5795, -74.1502]
        }

        for _, row in df.iterrows():
            zip_code_str = str(row['zip_code'])
            borough_name = row['borough']

            # Get coordinates (prefer ZIP code, fallback to borough)
            coords = zip_coords.get(zip_code_str, borough_coords.get(borough_name, [40.7831, -73.9712]))

            # Calculate marker size based on flu rate
            flu_rate = row['avg_flu_rate'] if pd.notna(row['avg_flu_rate']) else 0
            marker_size = max(8, min(20, flu_rate * 2))  # Scale between 8-20

            # Color based on flu rate
            if flu_rate > 15:
                color = '#E74C3C'  # Red for high
            elif flu_rate > 10:
                color = '#F39C12'  # Orange for medium
            else:
                color = '#3498DB'  # Blue for low

            layer_data.append({
                'lat': coords[0],
                'lng': coords[1],
                'size': marker_size,
                'color': color,
                'borderColor': '#2C3E50',
                'popup': f'''
                    <div style="width: 200px">
                        <h5 style="color: #3498DB">Flu Surveillance - {borough_name}</h5>
                        <p><strong>ZIP Code:</strong> {zip_code_str}</p>
                        <p><strong>Flu Rate:</strong> {flu_rate:.1f}%</p>
                        <p><strong>Total Visits:</strong> {row['total_flu_visits']:,.0f}</p>
                    </div>
                '''
            })

        return layer_data

    except Exception as e:
        print(f"Error getting flu layer data: {e}")
        return []

def get_foodborne_layer_data(conn, filters):
    """Get foodborne illness layer data points"""
    try:
        # Extract filter parameters
        borough = filters.get('borough', '')
        zip_code = filters.get('zipCode', '')

        # Query foodborne risk data
        query = """
            SELECT zip_code, borough, foodborne_risk_score,
                   high_risk_inspections, total_inspections, risk_level
            FROM foodborne_illness_risk_summary
            WHERE 1=1
        """

        if borough:
            query += f" AND borough = '{borough}'"
        if zip_code:
            query += f" AND zip_code = '{zip_code}'"

        df = pd.read_sql_query(query, conn)
        return df.to_dict('records') if not df.empty else []

    except Exception as e:
        print(f"Error getting foodborne layer data: {e}")
        return []

def get_air_quality_layer_data(conn, filters):
    """Get air quality layer data points"""
    try:
        # Extract filter parameters
        date_range = filters.get('dateRange', '30')
        borough = filters.get('borough', '')

        # Convert date range
        date_filter = get_date_range_filter(date_range)

        # Query air quality data
        query = """
            SELECT location_name, borough, air_quality_score,
                   avg_pm25, avg_ozone, risk_level, unhealthy_percentage
            FROM air_quality_summary
            WHERE 1=1
        """

        if date_filter:
            query += f" AND data_date >= '{date_filter[0]}' AND data_date <= '{date_filter[1]}'"
        if borough:
            query += f" AND borough = '{borough}'"

        df = pd.read_sql_query(query, conn)
        return df.to_dict('records') if not df.empty else []

    except Exception as e:
        print(f"Error getting air quality layer data: {e}")
        return []

def get_hospital_layer_data(conn, filters):
    """Get hospital ER layer data points with actual filtering"""

    try:
        # Extract filter parameters
        date_range = filters.get('dateRange', '30')
        borough = filters.get('borough', '')
        zip_code = filters.get('zipCode', '')

        # Convert date range
        date_filter = get_date_range_filter(date_range)

        # Query hospital data with filters
        query = """
            SELECT zip_code, borough, hospital_name,
                   SUM(respiratory_visits) as total_visits,
                   AVG(respiratory_visits) as avg_visits
            FROM real_hospital_data
            WHERE respiratory_visits > 0
        """

        if date_filter:
            query += f" AND date >= '{date_filter[0]}' AND date <= '{date_filter[1]}'"
        if borough:
            query += f" AND borough = '{borough}'"
        if zip_code:
            query += f" AND zip_code = '{zip_code}'"

        query += " GROUP BY zip_code, hospital_name HAVING total_visits > 0"

        df = pd.read_sql_query(query, conn)

        layer_data = []

        # Hospital coordinates (sample mapping)
        hospital_coords = {
            'South Bronx Health Hub': [40.8209, -73.9244],
            'Brooklyn Medical Center': [40.6958, -73.9901],
            'Manhattan General': [40.7505, -73.9934],
            'Queens Health Network': [40.7505, -73.9401],
            'Staten Island Medical': [40.6323, -74.0796],
        }

        for _, row in df.iterrows():
            hospital_name = row['hospital_name']

            # Get coordinates
            if hospital_name in hospital_coords:
                coords = hospital_coords[hospital_name]
            else:
                # Default to borough center
                borough_coords = {
                    'Bronx': [40.8448, -73.8648],
                    'Brooklyn': [40.6782, -73.9442],
                    'Manhattan': [40.7831, -73.9712],
                    'Queens': [40.7282, -73.7949],
                    'Staten Island': [40.5795, -74.1502]
                }
                coords = borough_coords.get(row['borough'], [40.7831, -73.9712])

            # Calculate marker size based on visit count
            total_visits = int(row['total_visits'])
            marker_size = min(25, max(8, total_visits / 5))

            # Determine color intensity based on visits
            if total_visits > 100:
                color = '#8E44AD'  # Dark purple
            elif total_visits > 50:
                color = '#B19CD9'  # Medium purple
            else:
                color = '#DDA0DD'  # Light purple

            layer_data.append({
                'lat': coords[0],
                'lng': coords[1],
                'size': marker_size,
                'color': color,
                'borderColor': '#8E44AD',
                'popup': f'''
                    <div style="width: 200px">
                        <h5 style="color: #DDA0DD">{hospital_name}</h5>
                        <p><strong>Borough:</strong> {row['borough']}</p>
                        <p><strong>ZIP Code:</strong> {row['zip_code']}</p>
                        <p><strong>Total ER Visits:</strong> {total_visits:,}</p>
                        <p><strong>Avg Daily:</strong> {row['avg_visits']:.1f}</p>
                    </div>
                '''
            })

        return layer_data

    except Exception as e:
        print(f"Error getting hospital layer data: {e}")
        return []

def get_tick_disease_layer_data(conn, filters):
    """Get tick disease layer data points"""
    try:
        # Extract filter parameters
        date_range = filters.get('dateRange', '30')
        borough = filters.get('borough', '')
        zip_code = filters.get('zipCode', '')

        # Convert date range
        date_filter = get_date_range_filter(date_range)

        # Query tick disease surveillance data
        query = """
            SELECT zip_code, borough, total_cases, severe_cases,
                   disease_type, risk_level
            FROM real_tick_disease_summary
            WHERE 1=1
        """

        if date_filter:
            query += f" AND report_date >= '{date_filter[0]}' AND report_date <= '{date_filter[1]}'"
        if borough:
            query += f" AND borough = '{borough}'"
        if zip_code:
            query += f" AND zip_code = '{zip_code}'"

        df = pd.read_sql_query(query, conn)
        return df.to_dict('records') if not df.empty else []

    except Exception as e:
        print(f"Error getting tick disease layer data: {e}")
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

    try:
        conn = sqlite3.connect('public_health_data.db')

        illness_types = filters.get('illnessTypes', [])
        date_range = filters.get('dateRange', '30')
        borough = filters.get('borough', '')
        zip_code = filters.get('zipCode', '')

        date_filter = get_date_range_filter(date_range)

        table_data = []

        # Get COVID data if selected (COVID data is borough-based)
        if 'COVID-19' in illness_types:
            if borough:
                # Query specific borough
                borough_col_map = {
                    'Bronx': 'BX_CASE_COUNT',
                    'Brooklyn': 'BK_CASE_COUNT',
                    'Manhattan': 'MN_CASE_COUNT',
                    'Queens': 'QN_CASE_COUNT',
                    'Staten Island': 'SI_CASE_COUNT'
                }

                if borough in borough_col_map:
                    covid_query = f"""
                        SELECT date_of_interest as date, '{borough}' as borough, {borough_col_map[borough]} as case_count
                        FROM nyc_covid_data
                        WHERE {borough_col_map[borough]} IS NOT NULL AND {borough_col_map[borough]} > 0
                    """
                    if date_filter:
                        covid_query += f" AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'"
                    covid_query += " ORDER BY date_of_interest DESC LIMIT 25"

                    covid_result = pd.read_sql_query(covid_query, conn)

                    for _, row in covid_result.iterrows():
                        case_count = int(row['case_count']) if row['case_count'] else 0
                        risk_level = 'HIGH' if case_count > 1000 else 'MEDIUM' if case_count > 500 else 'LOW'
                        table_data.append({
                            'id': f"covid_{borough}_{row['date']}",
                            'date': row['date'],
                            'location': f"{borough}",
                            'illness_type': 'COVID-19',
                            'value': f"{case_count:,} cases",
                            'risk_level': risk_level,
                            'color': '#FF6B6B'
                        })
            else:
                # Query all boroughs - get recent data for each
                covid_query = """
                    SELECT date_of_interest as date,
                           BX_CASE_COUNT, BK_CASE_COUNT, MN_CASE_COUNT, QN_CASE_COUNT, SI_CASE_COUNT
                    FROM nyc_covid_data
                    WHERE CASE_COUNT IS NOT NULL
                """
                if date_filter:
                    covid_query += f" AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'"
                covid_query += " ORDER BY date_of_interest DESC LIMIT 10"

                covid_result = pd.read_sql_query(covid_query, conn)

                borough_names = ['Bronx', 'Brooklyn', 'Manhattan', 'Queens', 'Staten Island']
                borough_cols = ['BX_CASE_COUNT', 'BK_CASE_COUNT', 'MN_CASE_COUNT', 'QN_CASE_COUNT', 'SI_CASE_COUNT']

                for _, row in covid_result.iterrows():
                    for borough_name, col in zip(borough_names, borough_cols):
                        case_count = int(row[col]) if row[col] else 0
                        if case_count > 0:
                            risk_level = 'HIGH' if case_count > 1000 else 'MEDIUM' if case_count > 500 else 'LOW'
                            table_data.append({
                                'id': f"covid_{borough_name}_{row['date']}",
                                'date': row['date'],
                                'location': f"{borough_name}",
                                'illness_type': 'COVID-19',
                                'value': f"{case_count:,} cases",
                                'risk_level': risk_level,
                                'color': '#FF6B6B'
                            })

        # Get Hospital ER data if selected
        if 'Hospital ER' in illness_types:
            hospital_query = """
                SELECT date, borough, zip_code, hospital_name, respiratory_visits
                FROM real_hospital_data
                WHERE respiratory_visits > 0
            """
            if date_filter:
                hospital_query += f" AND date >= '{date_filter[0]}' AND date <= '{date_filter[1]}'"
            if borough:
                hospital_query += f" AND borough = '{borough}'"
            if zip_code:
                hospital_query += f" AND zip_code = '{zip_code}'"
            hospital_query += " ORDER BY date DESC LIMIT 25"

            hospital_result = pd.read_sql_query(hospital_query, conn)

            for _, row in hospital_result.iterrows():
                risk_level = 'HIGH' if row['respiratory_visits'] > 50 else 'MEDIUM' if row['respiratory_visits'] > 20 else 'LOW'
                table_data.append({
                    'id': f"hospital_{row['zip_code']}_{row['date']}",
                    'date': row['date'],
                    'location': f"{row['borough']} ({row['zip_code']})",
                    'illness_type': 'Hospital ER',
                    'value': f"{row['respiratory_visits']} visits",
                    'risk_level': risk_level,
                    'color': '#DDA0DD'
                })

        # Get Foodborne data if selected
        if 'Foodborne' in illness_types:
            foodborne_query = """
                SELECT date, borough, zip_code, restaurant_name,
                       is_high_risk_foodborne, foodborne_risk_level, grade
                FROM restaurant_inspection_data
                WHERE 1=1
            """

            if date_filter:
                foodborne_query += f" AND date >= '{date_filter[0]}' AND date <= '{date_filter[1]}'"
            if borough:
                foodborne_query += f" AND borough = '{borough}'"
            if zip_code:
                foodborne_query += f" AND zip_code = '{zip_code}'"

            foodborne_query += " ORDER BY date DESC LIMIT 20"

            foodborne_result = pd.read_sql_query(foodborne_query, conn)

            for _, row in foodborne_result.iterrows():
                risk_level = row['foodborne_risk_level'] if row['foodborne_risk_level'] else 'LOW'
                risk_indicator = '🔴 HIGH RISK' if row['is_high_risk_foodborne'] else '🟡 MEDIUM' if risk_level == 'MEDIUM' else '🟢 LOW'

                table_data.append({
                    'id': f"restaurant_{row['zip_code']}_{row['date']}_{hash(row['restaurant_name']) % 10000}",
                    'date': row['date'],
                    'location': f"{row['borough']} ({row['zip_code']})",
                    'illness_type': 'Foodborne',
                    'value': f"{row['restaurant_name'][:30]}... (Grade: {row['grade'] or 'N/A'})",
                    'risk_level': risk_level,
                    'color': '#45B7D1'
                })

        conn.close()

        # Sort by date descending
        table_data.sort(key=lambda x: x['date'], reverse=True)

        return table_data[:50]  # Limit to 50 rows

    except Exception as e:
        print(f"Error getting filtered table data: {e}")
        return []

def get_health_alerts(filters):
    """Get health alerts based on filters"""

    try:
        conn = sqlite3.connect('public_health_data.db')

        borough = filters.get('borough', '')
        zip_code = filters.get('zipCode', '')

        # Get recent pattern detections as alerts
        alert_query = """
            SELECT id, date, zip_code, hospital_name, pattern_type,
                   current_value, percentage_change, confidence_level, ai_explanation
            FROM pattern_detections
            WHERE detection_timestamp >= datetime('now', '-7 days')
            AND confidence_level IN ('HIGH', 'MEDIUM')
        """

        if borough:
            alert_query += f" AND (hospital_name LIKE '%{borough}%' OR zip_code IN (SELECT zip_code FROM real_hospital_data WHERE borough = '{borough}'))"
        if zip_code:
            alert_query += f" AND zip_code = '{zip_code}'"

        alert_query += " ORDER BY detection_timestamp DESC LIMIT 10"

        alert_result = pd.read_sql_query(alert_query, conn)

        alerts = []
        for _, row in alert_result.iterrows():
            alerts.append({
                'id': row['id'],
                'title': f"{row['pattern_type']} Alert - {row['hospital_name']}",
                'description': f"ZIP {row['zip_code']}: {row['current_value']} visits ({row['percentage_change']:+.1f}% change)",
                'risk_level': row['confidence_level'],
                'date': row['date']
            })

        conn.close()
        return alerts

    except Exception as e:
        print(f"Error getting health alerts: {e}")
        return []

def get_illness_distribution(conn, filters):
    """Get illness distribution data for charts"""
    try:
        illness_types = filters.get('illnessTypes', [])
        date_range = filters.get('dateRange', '30')
        borough = filters.get('borough', '')
        zip_code = filters.get('zipCode', '')

        date_filter = get_date_range_filter(date_range)

        labels = []
        values = []

        for illness in illness_types:
            if illness == 'COVID-19':
                if borough:
                    # Query specific borough
                    borough_col_map = {
                        'Bronx': 'BX_CASE_COUNT',
                        'Brooklyn': 'BK_CASE_COUNT',
                        'Manhattan': 'MN_CASE_COUNT',
                        'Queens': 'QN_CASE_COUNT',
                        'Staten Island': 'SI_CASE_COUNT'
                    }

                    if borough in borough_col_map:
                        query = f"SELECT SUM({borough_col_map[borough]}) as total FROM nyc_covid_data WHERE {borough_col_map[borough]} IS NOT NULL"
                        if date_filter:
                            query += f" AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'"

                        result = pd.read_sql_query(query, conn)
                        value = int(result.iloc[0]['total']) if not result.empty and result.iloc[0]['total'] else 0
                        labels.append('COVID-19')
                        values.append(value)
                else:
                    # Query all boroughs
                    query = "SELECT SUM(CASE_COUNT) as total FROM nyc_covid_data WHERE CASE_COUNT IS NOT NULL"
                    if date_filter:
                        query += f" AND date_of_interest >= '{date_filter[0]}' AND date_of_interest <= '{date_filter[1]}'"

                    result = pd.read_sql_query(query, conn)
                    value = int(result.iloc[0]['total']) if not result.empty and result.iloc[0]['total'] else 0
                    labels.append('COVID-19')
                    values.append(value)

            elif illness == 'Hospital ER':
                query = "SELECT SUM(respiratory_visits) as total FROM real_hospital_data WHERE respiratory_visits > 0"
                if date_filter:
                    query += f" AND date >= '{date_filter[0]}' AND date <= '{date_filter[1]}'"
                if borough:
                    query += f" AND borough = '{borough}'"
                if zip_code:
                    query += f" AND zip_code = '{zip_code}'"

                result = pd.read_sql_query(query, conn)
                value = int(result.iloc[0]['total']) if not result.empty and result.iloc[0]['total'] else 0
                labels.append('Hospital ER')
                values.append(value)

            elif illness == 'Foodborne':
                query = "SELECT COUNT(*) as total FROM restaurant_inspection_data WHERE is_high_risk_foodborne = 1"
                if date_filter:
                    query += f" AND date >= '{date_filter[0]}' AND date <= '{date_filter[1]}'"
                if borough:
                    query += f" AND borough = '{borough}'"
                if zip_code:
                    query += f" AND zip_code = '{zip_code}'"

                result = pd.read_sql_query(query, conn)
                value = int(result.iloc[0]['total']) if not result.empty and result.iloc[0]['total'] else 0
                labels.append('Foodborne')
                values.append(value)

        return {'labels': labels, 'values': values}

    except Exception as e:
        print(f"Error getting illness distribution: {e}")
        return {'labels': [], 'values': []}

def get_trend_data(conn, filters):
    """Get trend data for charts"""
    try:
        date_range = filters.get('dateRange', '30')
        borough = filters.get('borough', '')
        zip_code = filters.get('zipCode', '')

        # Get COVID trend data (borough-based)
        if borough:
            # Query specific borough
            borough_col_map = {
                'Bronx': 'BX_CASE_COUNT',
                'Brooklyn': 'BK_CASE_COUNT',
                'Manhattan': 'MN_CASE_COUNT',
                'Queens': 'QN_CASE_COUNT',
                'Staten Island': 'SI_CASE_COUNT'
            }

            if borough in borough_col_map:
                query = f"""
                    SELECT date_of_interest as date, {borough_col_map[borough]} as daily_cases
                    FROM nyc_covid_data
                    WHERE date_of_interest >= date('now', '-30 days')
                    AND {borough_col_map[borough]} IS NOT NULL
                    ORDER BY date_of_interest
                """
            else:
                query = "SELECT date('now') as date, 0 as daily_cases WHERE 1=0"  # Empty result
        else:
            # Query all boroughs combined
            query = """
                SELECT date_of_interest as date, CASE_COUNT as daily_cases
                FROM nyc_covid_data
                WHERE date_of_interest >= date('now', '-30 days')
                AND CASE_COUNT IS NOT NULL
                ORDER BY date_of_interest
            """

        result = pd.read_sql_query(query, conn)

        labels = result['date'].tolist() if not result.empty else []
        data = result['daily_cases'].tolist() if not result.empty else []

        return {
            'labels': labels,
            'datasets': [{
                'label': 'Daily Cases',
                'data': data,
                'borderColor': '#FF6B6B',
                'backgroundColor': 'rgba(255, 107, 107, 0.1)'
            }]
        }

    except Exception as e:
        print(f"Error getting trend data: {e}")
        return {'labels': [], 'datasets': []}
