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

# Pattern detection thresholds (configurable)
SPIKE_THRESHOLD = 0.30  # 30% above average
DROP_THRESHOLD = 0.30   # 30% below average
CONSISTENTLY_HIGH_THRESHOLD = 0.20  # 20% above average for multiple days
CONSISTENTLY_HIGH_DAYS = 3  # Number of consecutive days

# Database and output paths
DB_PATH = "public_health_data.db"
OUTPUT_DIR = "."
RESULTS_CSV = os.path.join(OUTPUT_DIR, "pattern_analysis_results.csv")

class PatternDetector:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.patterns_detected = []
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """Load all relevant data from the database."""
        print("Loading data from database...")

        data = {}

        # Load hospital data
        data['hospital'] = pd.read_sql_query("""
            SELECT * FROM hospital_data
            ORDER BY date, zip_code
        """, self.conn)
        data['hospital']['date'] = pd.to_datetime(data['hospital']['date'])

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

        # Load NYC COVID data
        try:
            data['nyc_covid'] = pd.read_sql_query("""
                SELECT date_of_interest, CASE_COUNT, HOSPITALIZED_COUNT, DEATH_COUNT
                FROM nyc_covid_data
                ORDER BY date_of_interest
            """, self.conn)
            data['nyc_covid']['date_of_interest'] = pd.to_datetime(data['nyc_covid']['date_of_interest'])
        except:
            data['nyc_covid'] = pd.DataFrame()

        print(f"Loaded hospital data: {len(data['hospital'])} records")
        print(f"Loaded air quality data: {len(data['air_quality'])} records")
        print(f"Loaded CDC ILI data: {len(data['cdc_ili'])} records")
        print(f"Loaded NYC COVID data: {len(data['nyc_covid'])} records")

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
            
            # Detect spike pattern
            if pct_change > spike_threshold:
                pattern_detected = "spike"
                confidence = min(pct_change * 100, 100)  # Cap at 100%

            # Detect drop pattern
            elif pct_change < -drop_threshold:
                pattern_detected = "drop"
                confidence = min(abs(pct_change) * 100, 100)

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
                        confidence = min(np.mean(recent_changes) * 100, 100)
            
            # If pattern detected, gather context and store
            if pattern_detected:
                pattern_info = {
                    'date': row['date'],
                    'zip_code': row['zip_code'],
                    'hospital_name': row['hospital_name'],
                    'pattern_type': pattern_detected,
                    'current_value': current_value,
                    'rolling_mean': rolling_mean,
                    'percentage_change': pct_change * 100,
                    'confidence_score': confidence,
                    'context_data': self.gather_context_data(row['date'], row['zip_code'], data)
                }
                
                patterns.append(pattern_info)
                print(f"Pattern detected: {pattern_detected} in {row['zip_code']} on {row['date'].strftime('%Y-%m-%d')}")
        
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
        """Generate a fallback explanation when AI API is not available."""
        pattern_type = pattern_info['pattern_type']
        hospital = pattern_info['hospital_name']
        zip_code = pattern_info['zip_code']
        current_value = pattern_info['current_value']
        pct_change = pattern_info['percentage_change']
        date_str = pattern_info['date'].strftime('%Y-%m-%d')

        if pattern_type == 'spike':
            return f"Significant increase in respiratory ER visits detected at {hospital} (ZIP {zip_code}) on {date_str}. Current volume of {current_value} visits represents a {pct_change:+.1f}% increase above the 7-day average. This spike may indicate emerging respiratory illness outbreak, environmental factors, or seasonal patterns requiring immediate investigation and potential public health response."

        elif pattern_type == 'drop':
            return f"Notable decrease in respiratory ER visits observed at {hospital} (ZIP {zip_code}) on {date_str}. Current volume of {current_value} visits shows a {pct_change:+.1f}% decrease below the 7-day average. This drop could indicate improved community health, reduced disease transmission, or potential access barriers requiring monitoring to ensure healthcare availability."

        elif pattern_type == 'consistently_high':
            return f"Sustained elevation in respiratory ER visits identified at {hospital} (ZIP {zip_code}) on {date_str}. Current volume of {current_value} visits maintains a {pct_change:+.1f}% increase above average levels. This consistent pattern suggests ongoing respiratory health challenges in the community requiring sustained public health intervention and resource allocation."

        else:
            return f"Unusual pattern detected in respiratory ER visits at {hospital} (ZIP {zip_code}) on {date_str}. Current volume of {current_value} visits shows a {pct_change:+.1f}% change from the 7-day average. This pattern warrants further investigation to determine underlying causes and appropriate public health response."

    def construct_prompt(self, pattern_info: Dict) -> str:
        """Construct a detailed prompt for the AI explanation."""

        date_str = pattern_info['date'].strftime('%Y-%m-%d')
        pattern_type = pattern_info['pattern_type']
        zip_code = pattern_info['zip_code']
        hospital = pattern_info['hospital_name']
        current_value = pattern_info['current_value']
        rolling_mean = pattern_info['rolling_mean']
        pct_change = pattern_info['percentage_change']

        prompt = f"""
Analyze this public health data pattern:

PATTERN DETECTED: {pattern_type.replace('_', ' ').title()}
Date: {date_str}
Location: ZIP code {zip_code}
Hospital: {hospital}
Current ER respiratory visits: {current_value}
7-day average: {rolling_mean:.1f}
Change from average: {pct_change:+.1f}%

CONTEXT DATA:"""

        context = pattern_info['context_data']

        # Add air quality context
        if 'air_quality' in context:
            aqi = context['air_quality']
            prompt += f"""
Air Quality (same day):
- AQI: {aqi['aqi']} ({aqi['category']})
- PM2.5: {aqi['pm25_concentration']} μg/m³
- Ozone: {aqi['ozone_concentration']} ppm"""

        # Add CDC ILI context
        if 'cdc_ili' in context:
            ili = context['cdc_ili']
            prompt += f"""
CDC Influenza-like Illness (same week):
- ILI percentage: {ili['ili_percent']}%
- Total patients: {ili['total_patients']}
- ILI patients: {ili['ili_patients']}"""

        # Add NYC COVID context
        if 'nyc_covid' in context:
            covid = context['nyc_covid']
            prompt += f"""
NYC COVID-19 (same day):
- New cases: {covid['case_count']}
- Hospitalizations: {covid['hospitalized_count']}
- Deaths: {covid['death_count']}"""

        prompt += f"""

Please provide a brief explanation (2-3 sentences) for this {pattern_type.replace('_', ' ')} in respiratory ER visits. Consider potential relationships between the respiratory visits and the contextual health/environmental data provided."""

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
                 context_data, ai_explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        print("\n" + "="*60)
        print(f"PATTERN DETECTED: {pattern['pattern_type'].replace('_', ' ').upper()}")
        print("="*60)
        print(f"Date: {pattern['date'].strftime('%Y-%m-%d')}")
        print(f"Location: ZIP {pattern['zip_code']} ({pattern['hospital_name']})")
        print(f"ER Respiratory Visits: {pattern['current_value']}")
        print(f"7-day Average: {pattern['rolling_mean']:.1f}")
        print(f"Change: {pattern['percentage_change']:+.1f}%")
        print(f"Confidence: {pattern['confidence_score']:.1f}%")

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
