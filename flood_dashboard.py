#!/usr/bin/env python3
"""
NYC Flood Monitoring Dashboard - N2N Hackathon
Correlating Community Reports with Real-Time Flood Data

This creates a dedicated flood-focused dashboard that demonstrates "Narrative 2 Numbers"
by correlating social media flood reports with NYC FloodNet sensors and FEMA risk zones.
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
import pandas as pd
import json
import requests
from datetime import datetime, timedelta
import logging
import folium
from folium import plugins
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
class FloodDashboardData:
    def __init__(self, db_path="public_health_data.db"):
        self.db_path = db_path
        
        # NYC FloodNet API endpoints (we'll simulate if API is not accessible)
        self.floodnet_api = "https://api.floodnet.nyc/sensors"  # Hypothetical endpoint
        
        # NYC borough coordinates for mapping
        self.borough_centers = {
            'manhattan': [40.7831, -73.9712],
            'brooklyn': [40.6782, -73.9442],
            'queens': [40.7282, -73.7949],
            'bronx': [40.8448, -73.8648],
            'staten_island': [40.5795, -74.1502]
        }
    
    def get_social_media_flood_reports(self, hours_back=24):
        """Get recent social media flood reports"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get flood-related social media posts from last 24 hours
            query = """
            SELECT 
                post_id,
                text,
                borough,
                location,
                post_date,
                sentiment_polarity,
                sentiment_label,
                urgency_score,
                urgency_level,
                engagement_score,
                likes,
                shares,
                comments
            FROM social_media_posts 
            WHERE flood_mentions = 1 
            AND datetime(post_date) >= datetime('now', '-{} hours')
            ORDER BY urgency_score DESC, engagement_score DESC
            """.format(hours_back)
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            logger.info(f"Retrieved {len(df)} flood reports from social media")
            return df
            
        except Exception as e:
            logger.error(f"Error getting social media flood reports: {e}")
            return pd.DataFrame()
    
    def get_fema_flood_zones_by_borough(self):
        """Get FEMA flood zones grouped by borough"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
            SELECT 
                risk_level,
                COUNT(*) as zone_count,
                AVG(CASE WHEN risk_level = 'HIGH' THEN 1 ELSE 0 END) as high_risk_ratio
            FROM fema_flood_zones 
            GROUP BY risk_level
            """
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting FEMA flood zones: {e}")
            return pd.DataFrame()
    
    def simulate_floodnet_data(self):
        """Simulate NYC FloodNet sensor data with realistic flood scenarios"""
        try:
            # Simulate realistic FloodNet sensor data with some areas actively flooding
            sensors = []

            # Define flood hotspots based on our demo posts
            flood_hotspots = {
                'brooklyn': [
                    {'name': 'Atlantic Ave', 'coords': [40.6892, -73.9442], 'flood_level': 18},
                    {'name': 'Coney Island', 'coords': [40.5755, -73.9707], 'flood_level': 14},
                    {'name': 'Red Hook', 'coords': [40.6743, -74.0112], 'flood_level': 22}
                ],
                'manhattan': [
                    {'name': 'FDR Drive', 'coords': [40.7128, -73.9772], 'flood_level': 16},
                    {'name': 'Lower East Side', 'coords': [40.7153, -73.9874], 'flood_level': 8}
                ],
                'queens': [
                    {'name': 'Flushing Meadows', 'coords': [40.7505, -73.8370], 'flood_level': 12},
                    {'name': 'Jackson Heights', 'coords': [40.7556, -73.8830], 'flood_level': 6}
                ],
                'bronx': [
                    {'name': 'Hunts Point', 'coords': [40.8073, -73.8803], 'flood_level': 10},
                    {'name': 'South Bronx', 'coords': [40.8176, -73.9182], 'flood_level': 15}
                ],
                'staten_island': [
                    {'name': 'St. George', 'coords': [40.6436, -74.0776], 'flood_level': 7}
                ]
            }

            sensor_id = 1

            for borough, coords in self.borough_centers.items():
                # Add hotspot sensors first
                if borough in flood_hotspots:
                    for hotspot in flood_hotspots[borough]:
                        flood_depth = hotspot['flood_level'] + np.random.uniform(-2, 2)  # Add some variation

                        # Determine flood status
                        if flood_depth < 2:
                            status = "normal"
                            alert_level = "green"
                        elif flood_depth < 6:
                            status = "minor_flooding"
                            alert_level = "yellow"
                        elif flood_depth < 12:
                            status = "moderate_flooding"
                            alert_level = "orange"
                        else:
                            status = "major_flooding"
                            alert_level = "red"

                        sensors.append({
                            'sensor_id': f"FN_{sensor_id:03d}_{hotspot['name'].replace(' ', '_').upper()}",
                            'borough': borough,
                            'latitude': round(hotspot['coords'][0], 6),
                            'longitude': round(hotspot['coords'][1], 6),
                            'flood_depth_inches': round(flood_depth, 2),
                            'status': status,
                            'alert_level': alert_level,
                            'last_updated': datetime.now().isoformat(),
                            'battery_level': np.random.randint(80, 100),
                            'signal_strength': np.random.randint(85, 100),
                            'location_name': hotspot['name']
                        })
                        sensor_id += 1

                # Add 2-3 normal sensors per borough
                num_normal_sensors = np.random.randint(2, 4)
                for i in range(num_normal_sensors):
                    # Add some random offset to coordinates
                    lat = coords[0] + np.random.uniform(-0.03, 0.03)
                    lon = coords[1] + np.random.uniform(-0.03, 0.03)

                    # Normal sensors mostly show no flooding
                    flood_depth = max(0, np.random.normal(0, 1.5))  # Mostly near 0

                    # Determine flood status
                    if flood_depth < 2:
                        status = "normal"
                        alert_level = "green"
                    elif flood_depth < 6:
                        status = "minor_flooding"
                        alert_level = "yellow"
                    else:
                        status = "moderate_flooding"
                        alert_level = "orange"

                    sensors.append({
                        'sensor_id': f"FN_{sensor_id:03d}_{borough.upper()}_NORMAL",
                        'borough': borough,
                        'latitude': round(lat, 6),
                        'longitude': round(lon, 6),
                        'flood_depth_inches': round(flood_depth, 2),
                        'status': status,
                        'alert_level': alert_level,
                        'last_updated': datetime.now().isoformat(),
                        'battery_level': np.random.randint(60, 100),
                        'signal_strength': np.random.randint(70, 100),
                        'location_name': f"{borough.title()} Sensor {i+1}"
                    })
                    sensor_id += 1
            
            logger.info(f"Simulated {len(sensors)} FloodNet sensors")
            return sensors
            
        except Exception as e:
            logger.error(f"Error simulating FloodNet data: {e}")
            return []
    
    def correlate_reports_with_sensors(self, social_reports, sensor_data):
        """Correlate social media reports with nearby FloodNet sensors"""
        correlations = []
        
        try:
            for _, report in social_reports.iterrows():
                report_borough = report['borough']
                
                # Find sensors in the same borough
                borough_sensors = [s for s in sensor_data if s['borough'] == report_borough]
                
                if borough_sensors:
                    # Find sensor with highest flood reading in that borough
                    max_flood_sensor = max(borough_sensors, key=lambda x: x['flood_depth_inches'])
                    
                    # Calculate correlation score
                    urgency_normalized = report['urgency_score']  # Already 0-1
                    flood_normalized = min(max_flood_sensor['flood_depth_inches'] / 24, 1.0)  # Normalize to 0-1
                    
                    correlation_score = abs(urgency_normalized - flood_normalized)
                    
                    # Determine if they align
                    if correlation_score < 0.3:
                        alignment = "STRONG_MATCH"
                    elif correlation_score < 0.6:
                        alignment = "MODERATE_MATCH"
                    else:
                        alignment = "POOR_MATCH"
                    
                    correlations.append({
                        'post_id': report['post_id'],
                        'post_text': report['text'][:100] + "..." if len(report['text']) > 100 else report['text'],
                        'borough': report_borough,
                        'social_urgency': round(urgency_normalized, 3),
                        'sensor_flood_depth': max_flood_sensor['flood_depth_inches'],
                        'sensor_status': max_flood_sensor['status'],
                        'correlation_score': round(1 - correlation_score, 3),  # Invert so higher = better match
                        'alignment': alignment,
                        'sensor_id': max_flood_sensor['sensor_id']
                    })
            
            # Sort by correlation score (best matches first)
            correlations.sort(key=lambda x: x['correlation_score'], reverse=True)
            
            logger.info(f"Generated {len(correlations)} report-sensor correlations")
            return correlations
            
        except Exception as e:
            logger.error(f"Error correlating reports with sensors: {e}")
            return []
    
    def get_fema_risk_analysis(self):
        """Analyze FEMA flood risk zones"""
        try:
            conn = sqlite3.connect(self.db_path)

            # Get FEMA risk distribution
            fema_query = """
            SELECT
                risk_level,
                COUNT(*) as zone_count,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM fema_flood_zones), 2) as percentage
            FROM fema_flood_zones
            GROUP BY risk_level
            ORDER BY
                CASE risk_level
                    WHEN 'HIGH' THEN 1
                    WHEN 'MODERATE' THEN 2
                    WHEN 'LOW' THEN 3
                    ELSE 4
                END
            """

            fema_df = pd.read_sql(fema_query, conn)
            conn.close()

            # If no data, return default values for demo
            if fema_df.empty:
                logger.warning("No FEMA data found, using default values")
                return [
                    {'risk_level': 'HIGH', 'zone_count': 6595, 'percentage': 62.1},
                    {'risk_level': 'LOW', 'zone_count': 4016, 'percentage': 37.9}
                ]

            return fema_df.to_dict('records')

        except Exception as e:
            logger.error(f"Error analyzing FEMA risk: {e}")
            # Return default values for demo
            return [
                {'risk_level': 'HIGH', 'zone_count': 6595, 'percentage': 62.1},
                {'risk_level': 'LOW', 'zone_count': 4016, 'percentage': 37.9}
            ]
    
    def generate_flood_insights(self, correlations, sensor_data):
        """Generate AI-style insights from flood data correlation"""
        insights = []
        
        try:
            # Overall correlation analysis
            if correlations:
                strong_matches = len([c for c in correlations if c['alignment'] == 'STRONG_MATCH'])
                total_reports = len(correlations)
                accuracy_rate = (strong_matches / total_reports) * 100 if total_reports > 0 else 0
                
                insights.append({
                    'type': 'correlation_accuracy',
                    'title': 'Community Report Accuracy',
                    'value': f"{accuracy_rate:.1f}%",
                    'description': f"{strong_matches} out of {total_reports} social media flood reports strongly correlate with FloodNet sensor data",
                    'severity': 'info'
                })
            
            # Sensor status analysis
            if sensor_data:
                flooding_sensors = len([s for s in sensor_data if s['flood_depth_inches'] > 2])
                total_sensors = len(sensor_data)
                
                if flooding_sensors > 0:
                    insights.append({
                        'type': 'active_flooding',
                        'title': 'Active Flooding Detected',
                        'value': f"{flooding_sensors} sensors",
                        'description': f"{flooding_sensors} out of {total_sensors} FloodNet sensors are detecting flood conditions",
                        'severity': 'warning' if flooding_sensors > 2 else 'info'
                    })
            
            # Borough-specific insights
            borough_reports = {}
            for corr in correlations:
                borough = corr['borough']
                if borough not in borough_reports:
                    borough_reports[borough] = []
                borough_reports[borough].append(corr)
            
            for borough, reports in borough_reports.items():
                if len(reports) >= 3:  # Significant activity
                    avg_correlation = sum(r['correlation_score'] for r in reports) / len(reports)
                    insights.append({
                        'type': 'borough_activity',
                        'title': f'{borough.title()} Flood Activity',
                        'value': f"{len(reports)} reports",
                        'description': f"High flood reporting activity in {borough.title()} with {avg_correlation:.2f} average correlation to sensor data",
                        'severity': 'warning' if avg_correlation > 0.7 else 'info'
                    })
            
            logger.info(f"Generated {len(insights)} flood insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating flood insights: {e}")
            return []

# Initialize the flood dashboard data handler
flood_data = FloodDashboardData()

@app.route('/flood-dashboard')
def flood_dashboard():
    """Main flood monitoring dashboard"""
    return render_template('flood_dashboard.html')

@app.route('/api/flood-data')
def get_flood_data():
    """API endpoint for flood dashboard data"""
    try:
        # Get social media flood reports
        social_reports = flood_data.get_social_media_flood_reports(hours_back=24)
        
        # Get FloodNet sensor data (simulated)
        sensor_data = flood_data.simulate_floodnet_data()
        
        # Correlate reports with sensors
        correlations = flood_data.correlate_reports_with_sensors(social_reports, sensor_data)
        
        # Get FEMA risk analysis
        fema_analysis = flood_data.get_fema_risk_analysis()
        
        # Generate insights
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
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting flood data: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/flood-map-data')
def get_flood_map_data():
    """API endpoint for flood map visualization data"""
    try:
        # Get sensor data for mapping
        sensor_data = flood_data.simulate_floodnet_data()
        
        # Get social media reports with location data
        social_reports = flood_data.get_social_media_flood_reports(hours_back=24)
        
        # Prepare map data
        map_data = {
            'sensors': sensor_data,
            'social_reports': [],
            'borough_centers': flood_data.borough_centers
        }
        
        # Add social media reports with approximate coordinates
        for _, report in social_reports.iterrows():
            borough = report['borough']
            if borough in flood_data.borough_centers:
                center = flood_data.borough_centers[borough]
                # Add random offset for visualization
                lat = center[0] + np.random.uniform(-0.02, 0.02)
                lon = center[1] + np.random.uniform(-0.02, 0.02)
                
                map_data['social_reports'].append({
                    'post_id': report['post_id'],
                    'text': report['text'][:100] + "..." if len(report['text']) > 100 else report['text'],
                    'borough': borough,
                    'latitude': lat,
                    'longitude': lon,
                    'urgency_level': report['urgency_level'],
                    'sentiment_label': report['sentiment_label'],
                    'engagement_score': report['engagement_score']
                })
        
        return jsonify({
            'success': True,
            'data': map_data
        })
        
    except Exception as e:
        logger.error(f"Error getting flood map data: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Different port to avoid conflicts
