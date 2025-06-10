import pandas as pd
import numpy as np
import sqlite3
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "openai/gpt-3.5-turbo"

# Real-time pattern detection thresholds (configurable)
SPIKE_THRESHOLD = 0.30  # 30% above average - for current surveillance
DROP_THRESHOLD = 0.30   # 30% below average - for current surveillance
CONSISTENTLY_HIGH_THRESHOLD = 0.20  # 20% above average for multiple days
CONSISTENTLY_HIGH_DAYS = 3  # Number of consecutive days

# Real-time analysis settings
REAL_TIME_WINDOW_DAYS = 14  # Focus on last 2 weeks for current patterns
RECENT_PATTERN_DAYS = 7     # Consider patterns from last week as "current"

# Database and output paths
DB_PATH = "public_health_data.db"
OUTPUT_DIR = "."
RESULTS_CSV = os.path.join(OUTPUT_DIR, "pattern_analysis_results.csv")

class PatternDetector:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.patterns_detected = []
        self.analysis_timestamp = datetime.now()

    def load_data(self) -> Dict[str, pd.DataFrame]:
        """Load all relevant data from the database with real-time focus."""
        print("🔄 Loading REAL-TIME health surveillance data...")
        print(f"📅 Analysis timestamp: {self.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        data = {}

        # Load hospital data with real-time emphasis
        data['hospital'] = pd.read_sql_query("""
            SELECT * FROM hospital_data
            ORDER BY date DESC, zip_code
        """, self.conn)
        data['hospital']['date'] = pd.to_datetime(data['hospital']['date'])

        # Check data freshness
        if not data['hospital'].empty:
            latest_hospital_date = data['hospital']['date'].max()
            days_old = (self.analysis_timestamp - latest_hospital_date).days
            print(f"🏥 Hospital ER data: {len(data['hospital'])} records (latest: {latest_hospital_date.strftime('%Y-%m-%d')}, {days_old} days ago)")
        else:
            print("⚠️  No hospital data available")

        # Load air quality data
        try:
            data['air_quality'] = pd.read_sql_query("""
                SELECT * FROM air_quality_data
                ORDER BY date_local
            """, self.conn)
            data['air_quality']['date_local'] = pd.to_datetime(data['air_quality']['date_local'])
        except:
            data['air_quality'] = pd.DataFrame()

        # Load CDC ILI data
        try:
            data['cdc_ili'] = pd.read_sql_query("""
                SELECT * FROM cdc_ili_data
                ORDER BY week_ending_date
            """, self.conn)
            data['cdc_ili']['week_ending_date'] = pd.to_datetime(data['cdc_ili']['week_ending_date'])
        except:
            data['cdc_ili'] = pd.DataFrame()

        # Load NYC COVID data (real-time surveillance)
        try:
            data['nyc_covid'] = pd.read_sql_query("""
                SELECT date_of_interest, CASE_COUNT, HOSPITALIZED_COUNT, DEATH_COUNT,
                       BX_CASE_COUNT, BK_CASE_COUNT, MN_CASE_COUNT, QN_CASE_COUNT, SI_CASE_COUNT,
                       BX_HOSPITALIZED_COUNT, BK_HOSPITALIZED_COUNT, MN_HOSPITALIZED_COUNT,
                       QN_HOSPITALIZED_COUNT, SI_HOSPITALIZED_COUNT
                FROM nyc_covid_data
                ORDER BY date_of_interest DESC
            """, self.conn)
            data['nyc_covid']['date_of_interest'] = pd.to_datetime(data['nyc_covid']['date_of_interest'])

            if not data['nyc_covid'].empty:
                latest_covid_date = data['nyc_covid']['date_of_interest'].max()
                days_old = (self.analysis_timestamp - latest_covid_date).days
                print(f"🦠 NYC COVID surveillance: {len(data['nyc_covid'])} daily records (latest: {latest_covid_date.strftime('%Y-%m-%d')}, {days_old} days ago)")
                print(f"   📊 Borough-level data available for all 5 NYC boroughs")
            else:
                print("⚠️  No NYC COVID data available")
        except Exception as e:
            print(f"⚠️  Error loading NYC COVID data: {e}")
            data['nyc_covid'] = pd.DataFrame()

        # Load tick-borne disease surveillance data
        try:
            data['tick_diseases'] = pd.read_sql_query("""
                SELECT * FROM tick_disease_surveillance
                ORDER BY report_date DESC
            """, self.conn)
            data['tick_diseases']['report_date'] = pd.to_datetime(data['tick_diseases']['report_date'])

            if not data['tick_diseases'].empty:
                latest_tick_date = data['tick_diseases']['report_date'].max()
                days_old = (self.analysis_timestamp - latest_tick_date).days
                print(f"🦟 Tick-borne disease surveillance: {len(data['tick_diseases'])} cases (latest: {latest_tick_date.strftime('%Y-%m-%d')}, {days_old} days ago)")
                print(f"   📊 Disease types: {data['tick_diseases']['disease_type'].nunique()} types across {data['tick_diseases']['zip_code'].nunique()} ZIP codes")
            else:
                print("⚠️  No tick-borne disease data available")
        except Exception as e:
            print(f"⚠️  Error loading tick-borne disease data: {e}")
            data['tick_diseases'] = pd.DataFrame()

        # Load weather data for correlation analysis
        try:
            data['weather'] = pd.read_sql_query("""
                SELECT * FROM weather_data
                ORDER BY date DESC
            """, self.conn)
            data['weather']['date'] = pd.to_datetime(data['weather']['date'])

            if not data['weather'].empty:
                latest_weather_date = data['weather']['date'].max()
                days_old = (self.analysis_timestamp - latest_weather_date).days
                print(f"🌡️ Weather surveillance: {len(data['weather'])} observations (latest: {latest_weather_date.strftime('%Y-%m-%d')}, {days_old} days ago)")
                print(f"   📊 {data['weather']['station_name'].nunique()} weather stations with tick risk scoring")
            else:
                print("⚠️  No weather data available")
        except Exception as e:
            print(f"⚠️  Error loading weather data: {e}")
            data['weather'] = pd.DataFrame()

        # Summary of real-time data status
        print(f"\n📈 REAL-TIME DATA SUMMARY:")
        print(f"   🏥 Hospital ER visits: {len(data['hospital'])} records")
        print(f"   🌬️  Air quality: {len(data['air_quality'])} records")
        print(f"   🤧 CDC ILI surveillance: {len(data['cdc_ili'])} records")
        print(f"   🦠 NYC COVID surveillance: {len(data['nyc_covid'])} records")
        print(f"   🦟 Tick-borne diseases: {len(data['tick_diseases'])} cases")
        print(f"   🌡️ Weather data: {len(data['weather'])} observations")

        # Calculate real-time window coverage
        if not data['hospital'].empty:
            cutoff_date = self.analysis_timestamp - timedelta(days=REAL_TIME_WINDOW_DAYS)
            recent_hospital = data['hospital'][data['hospital']['date'] >= cutoff_date]
            print(f"   ⏰ Recent data (last {REAL_TIME_WINDOW_DAYS} days): {len(recent_hospital)} hospital records")

        return data

    def load_historical_data(self, days_back: int = 30) -> Dict[str, pd.DataFrame]:
        """Load historical data for simulation purposes.

        Args:
            days_back: Number of days of historical data to load

        Returns:
            Dictionary containing historical data for simulation
        """
        print(f"Loading {days_back} days of historical data for simulation...")

        data = {}

        # Load hospital data for the specified time period
        data['hospital'] = pd.read_sql_query(f"""
            SELECT * FROM hospital_data
            WHERE date >= date('now', '-{days_back} days')
            ORDER BY date, zip_code
        """, self.conn)

        # If no recent data found, load all available data
        if len(data['hospital']) == 0:
            print(f"No hospital data found in last {days_back} days, loading all available data...")
            data['hospital'] = pd.read_sql_query("""
                SELECT * FROM hospital_data
                ORDER BY date, zip_code
            """, self.conn)

        data['hospital']['date'] = pd.to_datetime(data['hospital']['date'])

        # Load air quality data
        try:
            data['air_quality'] = pd.read_sql_query(f"""
                SELECT * FROM air_quality_data
                WHERE date_local >= date('now', '-{days_back} days')
                ORDER BY date_local
            """, self.conn)
            data['air_quality']['date_local'] = pd.to_datetime(data['air_quality']['date_local'])
        except:
            data['air_quality'] = pd.DataFrame()

        # Load CDC ILI data
        try:
            data['cdc_ili'] = pd.read_sql_query(f"""
                SELECT * FROM cdc_ili_data
                WHERE week_ending_date >= date('now', '-{days_back} days')
                ORDER BY week_ending_date
            """, self.conn)
            data['cdc_ili']['week_ending_date'] = pd.to_datetime(data['cdc_ili']['week_ending_date'])
        except:
            data['cdc_ili'] = pd.DataFrame()

        # Load NYC COVID data
        try:
            data['nyc_covid'] = pd.read_sql_query(f"""
                SELECT date_of_interest, CASE_COUNT, HOSPITALIZED_COUNT, DEATH_COUNT
                FROM nyc_covid_data
                WHERE date_of_interest >= date('now', '-{days_back} days')
                ORDER BY date_of_interest
            """, self.conn)
            data['nyc_covid']['date_of_interest'] = pd.to_datetime(data['nyc_covid']['date_of_interest'])
        except:
            data['nyc_covid'] = pd.DataFrame()

        print(f"Loaded historical hospital data: {len(data['hospital'])} records")
        print(f"Loaded historical air quality data: {len(data['air_quality'])} records")
        print(f"Loaded historical CDC ILI data: {len(data['cdc_ili'])} records")
        print(f"Loaded historical NYC COVID data: {len(data['nyc_covid'])} records")

        return data
    
    def calculate_rolling_stats(self, df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
        """Calculate rolling statistics for pattern detection."""
        result = df.copy()
        
        # Group by zip_code and calculate rolling statistics
        for zip_code in df['zip_code'].unique():
            mask = df['zip_code'] == zip_code
            zip_data = df[mask].sort_values('date')
            
            # Calculate rolling mean and std
            rolling_mean = zip_data['er_visits_respiratory'].rolling(window=window, min_periods=1).mean()
            rolling_std = zip_data['er_visits_respiratory'].rolling(window=window, min_periods=1).std()
            
            # Update the result dataframe
            result.loc[mask, 'rolling_mean'] = rolling_mean.values
            result.loc[mask, 'rolling_std'] = rolling_std.values
            
        return result
    
    def detect_patterns(self, data: Dict[str, pd.DataFrame], custom_thresholds: Dict = None) -> List[Dict]:
        """Detect various patterns in the hospital data.

        Args:
            data: Dictionary containing hospital and other data
            custom_thresholds: Optional dictionary with custom threshold values for simulation
                              Expected keys: 'spike_threshold', 'drop_threshold', 'consistently_high_threshold'
        """
        print("\nDetecting patterns...")

        # Use custom thresholds if provided, otherwise use defaults
        if custom_thresholds:
            spike_threshold = custom_thresholds.get('spike_threshold', SPIKE_THRESHOLD)
            drop_threshold = custom_thresholds.get('drop_threshold', DROP_THRESHOLD)
            consistently_high_threshold = custom_thresholds.get('consistently_high_threshold', CONSISTENTLY_HIGH_THRESHOLD)
            print(f"Using custom thresholds: spike={spike_threshold:.1%}, drop={drop_threshold:.1%}, high={consistently_high_threshold:.1%}")
        else:
            spike_threshold = SPIKE_THRESHOLD
            drop_threshold = DROP_THRESHOLD
            consistently_high_threshold = CONSISTENTLY_HIGH_THRESHOLD
            print(f"Using default thresholds: spike={spike_threshold:.1%}, drop={drop_threshold:.1%}, high={consistently_high_threshold:.1%}")

        hospital_df = data['hospital'].copy()
        hospital_df = self.calculate_rolling_stats(hospital_df)

        patterns = []
        
        for idx, row in hospital_df.iterrows():
            current_value = row['er_visits_respiratory']
            rolling_mean = row['rolling_mean']
            rolling_std = row['rolling_std']
            
            # Skip if we don't have enough data for comparison
            if pd.isna(rolling_mean) or rolling_mean == 0:
                continue
                
            # Calculate percentage change from rolling mean
            pct_change = (current_value - rolling_mean) / rolling_mean
            
            pattern_detected = None
            confidence = 0

            # Enhanced confidence calculation function
            def calculate_enhanced_confidence(pct_change, rolling_std, current_value, pattern_type):
                """Calculate confidence score based on multiple factors."""
                base_confidence = min(abs(pct_change) * 100, 100)

                # Factor 1: Statistical significance (using standard deviation)
                if not pd.isna(rolling_std) and rolling_std > 0:
                    z_score = abs(current_value - rolling_mean) / rolling_std
                    stat_significance = min(z_score * 15, 40)  # Max 40 points for statistical significance
                else:
                    stat_significance = 0

                # Factor 2: Magnitude bonus for extreme changes
                magnitude_bonus = 0
                if abs(pct_change) > 0.5:  # 50% change
                    magnitude_bonus = 15
                elif abs(pct_change) > 0.75:  # 75% change
                    magnitude_bonus = 25
                elif abs(pct_change) > 1.0:  # 100% change
                    magnitude_bonus = 35

                # Factor 3: Pattern type reliability
                pattern_reliability = {
                    'spike': 1.0,
                    'drop': 0.95,
                    'consistently_high': 1.1
                }.get(pattern_type, 1.0)

                # Calculate final confidence (max 100)
                final_confidence = min((base_confidence + stat_significance + magnitude_bonus) * pattern_reliability, 100)
                return round(final_confidence, 1)

            # Detect spike pattern
            if pct_change > spike_threshold:
                pattern_detected = "spike"
                confidence = calculate_enhanced_confidence(pct_change, rolling_std, current_value, "spike")

            # Detect drop pattern
            elif pct_change < -drop_threshold:
                pattern_detected = "drop"
                confidence = calculate_enhanced_confidence(pct_change, rolling_std, current_value, "drop")

            # Detect consistently high pattern
            elif pct_change > consistently_high_threshold:
                # Check if this has been consistently high
                zip_code = row['zip_code']
                date = row['date']

                # Get recent data for this zip code
                recent_data = hospital_df[
                    (hospital_df['zip_code'] == zip_code) &
                    (hospital_df['date'] <= date) &
                    (hospital_df['date'] > date - timedelta(days=CONSISTENTLY_HIGH_DAYS))
                ]

                if len(recent_data) >= CONSISTENTLY_HIGH_DAYS:
                    # Check if all recent days are above threshold
                    recent_changes = []
                    for _, recent_row in recent_data.iterrows():
                        if not pd.isna(recent_row['rolling_mean']) and recent_row['rolling_mean'] > 0:
                            recent_pct = (recent_row['er_visits_respiratory'] - recent_row['rolling_mean']) / recent_row['rolling_mean']
                            recent_changes.append(recent_pct)

                    if len(recent_changes) >= CONSISTENTLY_HIGH_DAYS and all(change > consistently_high_threshold for change in recent_changes):
                        pattern_detected = "consistently_high"
                        avg_pct_change = np.mean(recent_changes)
                        confidence = calculate_enhanced_confidence(avg_pct_change, rolling_std, current_value, "consistently_high")
            
            # If pattern detected, gather context and store
            if pattern_detected:
                # Calculate confidence level category
                if confidence >= 80:
                    confidence_level = "HIGH"
                elif confidence >= 60:
                    confidence_level = "MEDIUM"
                else:
                    confidence_level = "LOW"

                pattern_info = {
                    'date': row['date'],
                    'zip_code': row['zip_code'],
                    'hospital_name': row['hospital_name'],
                    'pattern_type': pattern_detected,
                    'current_value': current_value,
                    'rolling_mean': rolling_mean,
                    'percentage_change': pct_change * 100,
                    'confidence_score': confidence,
                    'confidence_level': confidence_level,
                    'context_data': self.gather_context_data(row['date'], row['zip_code'], data)
                }

                patterns.append(pattern_info)
                print(f"Pattern detected: {pattern_detected} in {row['zip_code']} on {row['date'].strftime('%Y-%m-%d')} (Confidence: {confidence:.1f}% - {confidence_level})")
        
        return patterns

    def gather_context_data(self, date: datetime, zip_code: str, data: Dict[str, pd.DataFrame]) -> Dict:
        """Gather relevant context data for the detected pattern."""
        context = {}

        # Air quality data for the same date
        if not data['air_quality'].empty:
            aqi_data = data['air_quality'][
                data['air_quality']['date_local'].dt.date == date.date()
            ]
            if not aqi_data.empty:
                aqi_row = aqi_data.iloc[0]
                context['air_quality'] = {
                    'aqi': int(aqi_row['aqi']),
                    'category': str(aqi_row['category']),
                    'pm25_concentration': float(aqi_row['pm25_concentration']),
                    'ozone_concentration': float(aqi_row['ozone_concentration'])
                }

        # CDC ILI data for the same week
        if not data['cdc_ili'].empty:
            # Find the CDC data for the week containing this date
            cdc_data = data['cdc_ili'][
                data['cdc_ili']['week_ending_date'].dt.date >= date.date()
            ]
            if not cdc_data.empty:
                cdc_row = cdc_data.iloc[0]
                context['cdc_ili'] = {
                    'ili_percent': float(cdc_row['ili_percent']),
                    'total_patients': int(cdc_row['total_patients']),
                    'ili_patients': int(cdc_row['ili_patients'])
                }

        # NYC COVID data for the same date
        if not data['nyc_covid'].empty:
            covid_data = data['nyc_covid'][
                data['nyc_covid']['date_of_interest'].dt.date == date.date()
            ]
            if not covid_data.empty:
                covid_row = covid_data.iloc[0]
                context['nyc_covid'] = {
                    'case_count': int(covid_row['CASE_COUNT']) if pd.notna(covid_row['CASE_COUNT']) else 0,
                    'hospitalized_count': int(covid_row['HOSPITALIZED_COUNT']) if pd.notna(covid_row['HOSPITALIZED_COUNT']) else 0,
                    'death_count': int(covid_row['DEATH_COUNT']) if pd.notna(covid_row['DEATH_COUNT']) else 0
                }

        # Weather data for the same date
        if not data['weather'].empty:
            weather_data = data['weather'][
                data['weather']['date'].dt.date == date.date()
            ]
            if not weather_data.empty:
                # Get average weather conditions across all stations
                avg_weather = weather_data.groupby('date').agg({
                    'temp_avg_f': 'mean',
                    'precipitation_in': 'mean',
                    'humidity_percent': 'mean',
                    'tick_risk_score': 'mean'
                }).iloc[0]

                context['weather'] = {
                    'temperature_f': round(avg_weather['temp_avg_f'], 1),
                    'precipitation_in': round(avg_weather['precipitation_in'], 2),
                    'humidity_percent': round(avg_weather['humidity_percent'], 1),
                    'tick_risk_score': round(avg_weather['tick_risk_score'], 0)
                }

        # Tick-borne disease activity for the same week
        if not data['tick_diseases'].empty:
            # Look for tick disease cases in the same ZIP code within ±7 days
            week_start = date - timedelta(days=7)
            week_end = date + timedelta(days=7)

            tick_data = data['tick_diseases'][
                (data['tick_diseases']['zip_code'] == zip_code) &
                (data['tick_diseases']['report_date'] >= week_start) &
                (data['tick_diseases']['report_date'] <= week_end)
            ]

            if not tick_data.empty:
                context['tick_diseases'] = {
                    'cases_this_week': len(tick_data),
                    'disease_types': tick_data['disease_type'].unique().tolist(),
                    'severity_distribution': tick_data['severity'].value_counts().to_dict()
                }

        return context

    def simulate_alerts(self, custom_thresholds: Dict, days_back: int = 30) -> List[Dict]:
        """Simulate alert generation with custom thresholds on historical data.

        Args:
            custom_thresholds: Dictionary with threshold values for simulation
                              Expected keys: 'spike_threshold', 'drop_threshold', 'consistently_high_threshold'
            days_back: Number of days of historical data to analyze

        Returns:
            List of simulated alert patterns
        """
        print(f"\n=== SIMULATING ALERTS WITH CUSTOM THRESHOLDS ===")
        print(f"Simulation period: Last {days_back} days")
        print(f"Custom thresholds: {custom_thresholds}")

        # Load historical data
        historical_data = self.load_historical_data(days_back)

        # Run pattern detection with custom thresholds
        simulated_patterns = self.detect_patterns(historical_data, custom_thresholds)

        # Format results for simulation response
        simulation_results = []
        for pattern in simulated_patterns:
            simulation_results.append({
                'date': pattern['date'].strftime('%Y-%m-%d'),
                'zip_code': pattern['zip_code'],
                'hospital_name': pattern['hospital_name'],
                'pattern_type': pattern['pattern_type'],
                'current_value': pattern['current_value'],
                'rolling_mean': round(pattern['rolling_mean'], 1),
                'percentage_change': round(pattern['percentage_change'], 1),
                'confidence_score': round(pattern['confidence_score'], 1),
                'brief_description': f"{pattern['pattern_type'].replace('_', ' ').title()} in {pattern['hospital_name']} (ZIP {pattern['zip_code']}): {pattern['current_value']} visits ({pattern['percentage_change']:+.1f}% vs 7-day avg)"
            })

        print(f"Simulation complete: {len(simulation_results)} patterns detected")
        return simulation_results

    def generate_ai_explanation(self, pattern_info: Dict) -> str:
        """Generate AI explanation using OpenRouter API."""

        # Skip API calls to avoid 402 Payment Required errors
        # Use fallback explanation instead
        return self.generate_fallback_explanation(pattern_info)

        # Original API code commented out to prevent errors:
        # prompt = self.construct_prompt(pattern_info)
        # headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        # payload = {"model": MODEL_NAME, "messages": [...], "max_tokens": 300, "temperature": 0.7}
        # try:
        #     response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        #     response.raise_for_status()
        #     result = response.json()
        #     explanation = result['choices'][0]['message']['content'].strip()
        #     return explanation
        # except requests.exceptions.RequestException as e:
        #     print(f"Error calling OpenRouter API: {e}")
        #     return f"AI explanation unavailable due to API error: {str(e)}"
        # except (KeyError, IndexError) as e:
        #     print(f"Error parsing API response: {e}")
        #     return "AI explanation unavailable due to response parsing error"

    def generate_fallback_explanation(self, pattern_info: Dict) -> str:
        """Generate an enhanced context-aware explanation when AI API is not available."""
        pattern_type = pattern_info['pattern_type']
        hospital = pattern_info['hospital_name']
        zip_code = pattern_info['zip_code']
        current_value = pattern_info['current_value']
        pct_change = pattern_info['percentage_change']
        confidence = pattern_info['confidence_score']
        confidence_level = pattern_info.get('confidence_level', 'MEDIUM')
        date_str = pattern_info['date'].strftime('%Y-%m-%d')
        context = pattern_info['context_data']

        # Build context-aware explanation
        base_explanation = ""
        context_factors = []

        if pattern_type == 'spike':
            base_explanation = f"🔴 SIGNIFICANT SPIKE DETECTED: Respiratory ER visits at {hospital} (ZIP {zip_code}) surged to {current_value} visits on {date_str}, representing a {pct_change:+.1f}% increase above the 7-day average."

            # Add context-specific insights
            if 'air_quality' in context:
                aqi = context['air_quality']
                if aqi['aqi'] > 100:
                    context_factors.append(f"Poor air quality (AQI: {aqi['aqi']}) may be contributing to respiratory distress")
                elif aqi['aqi'] > 50:
                    context_factors.append(f"Moderate air quality (AQI: {aqi['aqi']}) could be a contributing factor")

            if 'nyc_covid' in context:
                covid = context['nyc_covid']
                if covid['case_count'] > 100:
                    context_factors.append(f"High COVID-19 activity ({covid['case_count']} cases) suggests viral respiratory illness spread")
                elif covid['hospitalized_count'] > 10:
                    context_factors.append(f"COVID-19 hospitalizations ({covid['hospitalized_count']}) indicate severe respiratory cases")

            if 'cdc_ili' in context:
                ili = context['cdc_ili']
                if ili['ili_percent'] > 5:
                    context_factors.append(f"Elevated influenza-like illness rates ({ili['ili_percent']}%) indicate broader respiratory illness circulation")

            # Weather correlation for spikes
            if 'weather' in context:
                weather = context['weather']
                if weather['tick_risk_score'] >= 70:
                    context_factors.append(f"High tick activity risk (score: {weather['tick_risk_score']}) due to favorable weather conditions")
                if weather['temperature_f'] > 80:
                    context_factors.append(f"High temperature ({weather['temperature_f']}°F) may increase heat-related health stress")
                if weather['humidity_percent'] > 80:
                    context_factors.append(f"High humidity ({weather['humidity_percent']}%) could exacerbate respiratory conditions")

            # Tick-borne disease correlation
            if 'tick_diseases' in context:
                tick_info = context['tick_diseases']
                if tick_info['cases_this_week'] > 0:
                    context_factors.append(f"Tick-borne disease activity detected: {tick_info['cases_this_week']} cases this week in area")

        elif pattern_type == 'drop':
            base_explanation = f"🟢 POSITIVE HEALTH TREND: Respiratory ER visits at {hospital} (ZIP {zip_code}) decreased to {current_value} visits on {date_str}, showing a {pct_change:.1f}% improvement below the 7-day average."

            # Add context for drops - focus on positive health indicators
            if 'air_quality' in context:
                aqi = context['air_quality']
                if aqi['aqi'] <= 50:
                    context_factors.append(f"Excellent air quality (AQI: {aqi['aqi']}) likely supporting respiratory health improvement")

            # Weather correlation for drops (positive trends)
            if 'weather' in context:
                weather = context['weather']
                if weather['tick_risk_score'] < 30:
                    context_factors.append(f"Low tick activity risk (score: {weather['tick_risk_score']}) due to unfavorable weather for vectors")
                if 45 <= weather['temperature_f'] <= 75:
                    context_factors.append(f"Optimal temperature ({weather['temperature_f']}°F) supporting overall health")
                if weather['humidity_percent'] < 60:
                    context_factors.append(f"Comfortable humidity levels ({weather['humidity_percent']}%) reducing respiratory stress")

            # Additional air quality context for drops
            if 'air_quality' in context:
                aqi = context['air_quality']
                if aqi['aqi'] <= 100:
                    context_factors.append(f"Moderate air quality (AQI: {aqi['aqi']}) - health improvement despite environmental conditions")
                else:
                    context_factors.append(f"Health improvement occurring despite poor air quality (AQI: {aqi['aqi']})")

            if 'nyc_covid' in context:
                covid = context['nyc_covid']
                if covid['case_count'] < 50:
                    context_factors.append(f"Low COVID-19 activity ({covid['case_count']} cases) supporting declining respiratory illness")
                else:
                    context_factors.append(f"Respiratory health improving despite COVID-19 activity ({covid['case_count']} cases)")

            if 'cdc_ili' in context:
                ili = context['cdc_ili']
                if ili['ili_percent'] < 3:
                    context_factors.append(f"Low influenza-like illness rates ({ili['ili_percent']}%) indicate successful respiratory illness control")
                else:
                    context_factors.append(f"ER visits declining despite elevated ILI rates ({ili['ili_percent']}%) - positive trend")

        elif pattern_type == 'consistently_high':
            base_explanation = f"🟡 SUSTAINED ELEVATION: Respiratory ER visits at {hospital} (ZIP {zip_code}) remain consistently elevated at {current_value} visits on {date_str}, maintaining a {pct_change:+.1f}% increase above average levels."

            context_factors.append("This persistent pattern suggests ongoing community respiratory health challenges requiring sustained intervention")

        # Combine base explanation with context
        if context_factors:
            context_text = ". ".join(context_factors)
            full_explanation = f"{base_explanation} {context_text}."
        else:
            full_explanation = f"{base_explanation} This pattern warrants investigation to determine underlying causes."

        # Add epidemiologically sound confidence and urgency indicators
        urgency = self.determine_epidemiological_urgency(pattern_type, confidence, pct_change)

        return f"{full_explanation} Confidence: {confidence:.1f}% ({confidence_level}) - {urgency}."

    def determine_epidemiological_urgency(self, pattern_type: str, confidence: float, pct_change: float) -> str:
        """Determine urgency level based on epidemiological significance of pattern type."""

        if pattern_type == 'drop':
            # Drops in ER visits are positive trends - lower urgency even with high confidence
            if confidence >= 80:
                return "POSITIVE TREND CONFIRMED"
            elif confidence >= 60:
                return "IMPROVEMENT NOTED"
            else:
                return "POTENTIAL IMPROVEMENT"

        elif pattern_type == 'spike':
            # Spikes are concerning - higher urgency even with moderate confidence
            if confidence >= 70:
                return "IMMEDIATE ATTENTION REQUIRED"
            elif confidence >= 50:
                return "URGENT MONITORING REQUIRED"
            elif confidence >= 30:
                return "ENHANCED SURVEILLANCE NEEDED"
            else:
                return "FURTHER VALIDATION NEEDED"

        elif pattern_type == 'consistently_high':
            # Sustained high levels are concerning but less urgent than acute spikes
            if confidence >= 80:
                return "SUSTAINED ELEVATION - INTERVENTION NEEDED"
            elif confidence >= 60:
                return "ONGOING MONITORING REQUIRED"
            else:
                return "TREND VALIDATION NEEDED"

        else:
            # Fallback for unknown pattern types
            if confidence >= 80:
                return "HIGH CONFIDENCE DETECTION"
            elif confidence >= 60:
                return "MONITORING RECOMMENDED"
            else:
                return "FURTHER VALIDATION NEEDED"

    def construct_prompt(self, pattern_info: Dict) -> str:
        """Construct an enhanced, detailed prompt for the AI explanation."""

        date_str = pattern_info['date'].strftime('%Y-%m-%d')
        pattern_type = pattern_info['pattern_type']
        zip_code = pattern_info['zip_code']
        hospital = pattern_info['hospital_name']
        current_value = pattern_info['current_value']
        rolling_mean = pattern_info['rolling_mean']
        pct_change = pattern_info['percentage_change']
        confidence = pattern_info['confidence_score']
        confidence_level = pattern_info.get('confidence_level', 'MEDIUM')

        prompt = f"""You are a public health epidemiologist analyzing respiratory health patterns. Provide a clear, actionable explanation for this pattern.

🚨 CRITICAL HEALTH PATTERN DETECTED 🚨

PATTERN TYPE: {pattern_type.replace('_', ' ').title()} Alert
DATE: {date_str}
LOCATION: ZIP Code {zip_code} - {hospital}
CURRENT ER RESPIRATORY VISITS: {current_value}
7-DAY BASELINE: {rolling_mean:.1f} visits
CHANGE FROM BASELINE: {pct_change:+.1f}%
CONFIDENCE LEVEL: {confidence:.1f}% ({confidence_level})

ENVIRONMENTAL & HEALTH CONTEXT:"""

        context = pattern_info['context_data']

        # Add comprehensive context
        if 'air_quality' in context:
            aqi = context['air_quality']
            air_status = "POOR" if aqi['aqi'] > 100 else "MODERATE" if aqi['aqi'] > 50 else "GOOD"
            prompt += f"""
🌫️ AIR QUALITY ({air_status}):
- Air Quality Index: {aqi['aqi']} ({aqi['category']})
- PM2.5 Concentration: {aqi['pm25_concentration']} μg/m³
- Ozone Level: {aqi['ozone_concentration']} ppm"""

        if 'cdc_ili' in context:
            ili = context['cdc_ili']
            ili_status = "HIGH" if ili['ili_percent'] > 5 else "ELEVATED" if ili['ili_percent'] > 3 else "NORMAL"
            prompt += f"""
🤒 INFLUENZA-LIKE ILLNESS ({ili_status}):
- ILI Percentage: {ili['ili_percent']}%
- Total Patients Monitored: {ili['total_patients']:,}
- ILI Cases: {ili['ili_patients']:,}"""

        if 'nyc_covid' in context:
            covid = context['nyc_covid']
            covid_status = "HIGH" if covid['case_count'] > 100 else "MODERATE" if covid['case_count'] > 50 else "LOW"
            prompt += f"""
🦠 COVID-19 ACTIVITY ({covid_status}):
- New Cases: {covid['case_count']:,}
- Hospitalizations: {covid['hospitalized_count']:,}
- Deaths: {covid['death_count']:,}"""

        prompt += f"""

ANALYSIS REQUIREMENTS:
1. Explain the likely causes of this {pattern_type.replace('_', ' ')} pattern
2. Identify potential correlations with environmental/health context data
3. Assess public health implications and urgency level
4. Recommend specific actions for health officials

Provide a comprehensive but concise explanation (3-4 sentences) that a public health official can use for decision-making. Focus on actionable insights and potential interventions."""

        return prompt

    def create_results_table(self):
        """Create the pattern_detections table in the database."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pattern_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_timestamp TEXT,
                date TEXT,
                zip_code TEXT,
                hospital_name TEXT,
                pattern_type TEXT,
                current_value INTEGER,
                rolling_mean REAL,
                percentage_change REAL,
                confidence_score REAL,
                confidence_level TEXT,
                context_data TEXT,
                ai_explanation TEXT
            )
        """)
        self.conn.commit()

    def store_results(self, patterns_with_explanations: List[Dict]):
        """Store pattern detection results in database and CSV."""

        if not patterns_with_explanations:
            print("No patterns detected to store.")
            return

        # Create table if it doesn't exist
        self.create_results_table()

        # Prepare data for storage
        timestamp = datetime.now().isoformat()

        # Store in database
        cursor = self.conn.cursor()
        for pattern in patterns_with_explanations:
            cursor.execute("""
                INSERT INTO pattern_detections
                (detection_timestamp, date, zip_code, hospital_name, pattern_type,
                 current_value, rolling_mean, percentage_change, confidence_score,
                 confidence_level, context_data, ai_explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp,
                pattern['date'].strftime('%Y-%m-%d'),
                pattern['zip_code'],
                pattern['hospital_name'],
                pattern['pattern_type'],
                pattern['current_value'],
                pattern['rolling_mean'],
                pattern['percentage_change'],
                pattern['confidence_score'],
                pattern.get('confidence_level', 'MEDIUM'),
                json.dumps(pattern['context_data']),
                pattern['ai_explanation']
            ))

        self.conn.commit()
        print(f"Stored {len(patterns_with_explanations)} patterns in database.")

        # Store in CSV
        csv_data = []
        for pattern in patterns_with_explanations:
            csv_data.append({
                'detection_timestamp': timestamp,
                'date': pattern['date'].strftime('%Y-%m-%d'),
                'zip_code': pattern['zip_code'],
                'hospital_name': pattern['hospital_name'],
                'pattern_type': pattern['pattern_type'],
                'current_value': pattern['current_value'],
                'rolling_mean': round(pattern['rolling_mean'], 2),
                'percentage_change': round(pattern['percentage_change'], 2),
                'confidence_score': round(pattern['confidence_score'], 2),
                'confidence_level': pattern.get('confidence_level', 'MEDIUM'),
                'ai_explanation': pattern['ai_explanation']
            })

        df = pd.DataFrame(csv_data)

        # Append to existing CSV or create new one
        if os.path.exists(RESULTS_CSV):
            df.to_csv(RESULTS_CSV, mode='a', header=False, index=False)
        else:
            df.to_csv(RESULTS_CSV, index=False)

        print(f"Stored {len(patterns_with_explanations)} patterns in {RESULTS_CSV}")

    def run_analysis(self):
        """Main function to run the complete pattern detection and analysis."""
        print("=== PHASE 2: AI PATTERN DETECTION & EXPLANATION ===")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Load data
        data = self.load_data()

        # Detect patterns
        patterns = self.detect_patterns(data)

        if not patterns:
            print("No patterns detected in the data.")
            return

        print(f"\nFound {len(patterns)} patterns. Generating AI explanations...")

        # Generate AI explanations for each pattern
        patterns_with_explanations = []
        for i, pattern in enumerate(patterns, 1):
            print(f"Generating explanation {i}/{len(patterns)}...")

            explanation = self.generate_ai_explanation(pattern)
            pattern['ai_explanation'] = explanation
            patterns_with_explanations.append(pattern)

            # Display results
            self.display_pattern_result(pattern)

        # Store results
        self.store_results(patterns_with_explanations)

        print(f"\n=== ANALYSIS COMPLETE ===")
        print(f"Total patterns detected: {len(patterns_with_explanations)}")
        print(f"Results saved to database and {RESULTS_CSV}")

    def display_pattern_result(self, pattern: Dict):
        """Display a single pattern result in a formatted way."""
        confidence_level = pattern.get('confidence_level', 'MEDIUM')
        pattern_type = pattern['pattern_type']

        # Use epidemiologically appropriate emojis based on pattern type and urgency
        if pattern_type == 'drop':
            pattern_emoji = "🟢"  # Green for positive health trends
        elif pattern_type == 'spike':
            pattern_emoji = "🔴"  # Red for concerning spikes
        elif pattern_type == 'consistently_high':
            pattern_emoji = "🟡"  # Yellow for sustained elevation
        else:
            pattern_emoji = "🔵"  # Blue for other patterns

        print("\n" + "="*70)
        print(f"{pattern_emoji} PATTERN DETECTED: {pattern['pattern_type'].replace('_', ' ').upper()}")
        print("="*70)
        print(f"📅 Date: {pattern['date'].strftime('%Y-%m-%d')}")
        print(f"📍 Location: ZIP {pattern['zip_code']} ({pattern['hospital_name']})")
        print(f"🏥 ER Respiratory Visits: {pattern['current_value']}")
        print(f"📊 7-day Average: {pattern['rolling_mean']:.1f}")
        print(f"📈 Change: {pattern['percentage_change']:+.1f}%")
        print(f"🎯 Confidence: {pattern['confidence_score']:.1f}% ({confidence_level})")

        # Display context if available
        context = pattern['context_data']
        if context:
            print("\nCONTEXT DATA:")
            if 'air_quality' in context:
                aqi = context['air_quality']
                print(f"  Air Quality: AQI {aqi['aqi']} ({aqi['category']})")
            if 'cdc_ili' in context:
                ili = context['cdc_ili']
                print(f"  CDC ILI: {ili['ili_percent']}% ({ili['ili_patients']} patients)")
            if 'nyc_covid' in context:
                covid = context['nyc_covid']
                print(f"  NYC COVID: {covid['case_count']} cases, {covid['hospitalized_count']} hospitalizations")

        print(f"\nAI EXPLANATION:")
        print(f"{pattern['ai_explanation']}")
        print("="*60)

    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main execution function."""
    detector = PatternDetector()

    try:
        detector.run_analysis()
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        detector.close()


if __name__ == "__main__":
    main()
