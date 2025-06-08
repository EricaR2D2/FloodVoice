import pandas as pd
import numpy as np
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3

# Suppress statsmodels warnings for cleaner output
warnings.filterwarnings('ignore')

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.holtwinters import ExponentialSmoothing, SimpleExpSmoothing
    STATSMODELS_AVAILABLE = True
    print("✅ statsmodels loaded successfully")
except ImportError as e:
    STATSMODELS_AVAILABLE = False
    print(f"Warning: statsmodels not available ({e}). Using simple forecasting methods.")

class ForecastingEngine:
    """
    Advanced forecasting engine for public health time series data.
    Supports multiple forecasting models with automatic model selection.
    """
    
    def __init__(self, db_path: str = "public_health_data.db"):
        self.db_path = db_path
        self.forecast_horizon = 7  # Default 7-day forecast
        self.confidence_level = 0.95
        self.min_data_points = 7  # Minimum data points needed for forecasting
        
    def get_historical_data(self, hospital_name: str, zip_code: str, days_back: int = 30) -> pd.DataFrame:
        """Fetch historical data for a specific hospital and ZIP code."""
        conn = sqlite3.connect(self.db_path)

        try:
            # First try exact match
            query = """
                SELECT date, er_visits_respiratory, hospital_name, zip_code
                FROM hospital_data
                WHERE hospital_name = ? AND zip_code = ?
                ORDER BY date
            """

            df = pd.read_sql_query(query, conn, params=[hospital_name, zip_code])

            # If no exact match, try just ZIP code
            if len(df) == 0:
                query = """
                    SELECT date, er_visits_respiratory, hospital_name, zip_code
                    FROM hospital_data
                    WHERE zip_code = ?
                    ORDER BY date
                """
                df = pd.read_sql_query(query, conn, params=[zip_code])

            df['date'] = pd.to_datetime(df['date'])

            # Filter by days_back if we have data
            if len(df) > 0 and days_back:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                df = df[df['date'] >= cutoff_date]

            return df

        finally:
            conn.close()
    
    def generate_forecast(self, hospital_name: str, zip_code: str, 
                         forecast_days: int = 7, days_back: int = 30) -> Dict:
        """
        Generate forecast for a specific hospital and ZIP code.
        
        Args:
            hospital_name: Name of the hospital
            zip_code: ZIP code area
            forecast_days: Number of days to forecast
            days_back: Number of historical days to use
            
        Returns:
            Dictionary containing forecast results
        """
        try:
            # Get historical data
            historical_data = self.get_historical_data(hospital_name, zip_code, days_back)
            
            if len(historical_data) < self.min_data_points:
                return self._create_error_response(
                    f"Insufficient data: only {len(historical_data)} data points available"
                )
            
            # Prepare time series
            ts_data = historical_data.set_index('date')['er_visits_respiratory']
            
            # Try multiple forecasting models
            models_to_try = []
            
            if STATSMODELS_AVAILABLE:
                models_to_try.extend([
                    ('arima', self._fit_arima),
                    ('exponential_smoothing', self._fit_exponential_smoothing),
                    ('simple_exponential', self._fit_simple_exponential)
                ])
            
            # Always include simple methods as fallback
            models_to_try.extend([
                ('linear_trend', self._fit_linear_trend),
                ('moving_average', self._fit_moving_average)
            ])
            
            best_forecast = None
            best_score = float('inf')
            
            for model_name, model_func in models_to_try:
                try:
                    forecast_result = model_func(ts_data, forecast_days)
                    
                    # Use AIC if available, otherwise use MSE
                    score = forecast_result.get('aic', forecast_result.get('mse', float('inf')))
                    
                    if score < best_score:
                        best_score = score
                        best_forecast = forecast_result
                        best_forecast['model_used'] = model_name
                        
                except Exception as e:
                    print(f"Model {model_name} failed: {str(e)}")
                    continue
            
            if best_forecast is None:
                return self._create_error_response("All forecasting models failed")
            
            # Add metadata
            best_forecast.update({
                'hospital_name': hospital_name,
                'zip_code': zip_code,
                'historical_data_points': len(historical_data),
                'forecast_generated_at': datetime.now().isoformat(),
                'confidence_level': self.confidence_level
            })
            
            return best_forecast
            
        except Exception as e:
            return self._create_error_response(f"Forecasting error: {str(e)}")
    
    def _fit_arima(self, ts_data: pd.Series, forecast_days: int) -> Dict:
        """Fit ARIMA model and generate forecast with robust confidence intervals."""
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels not available")

        # Auto ARIMA with enhanced parameter selection
        best_aic = float('inf')
        best_model = None
        best_order = None

        # Try different ARIMA parameters with more comprehensive search
        for p in range(4):  # Increased range
            for d in range(3):  # Increased range
                for q in range(4):  # Increased range
                    try:
                        model = ARIMA(ts_data, order=(p, d, q))
                        fitted_model = model.fit()

                        # Additional model validation
                        if fitted_model.aic < best_aic and not np.isnan(fitted_model.aic):
                            best_aic = fitted_model.aic
                            best_model = fitted_model
                            best_order = (p, d, q)
                    except:
                        continue

        if best_model is None:
            raise ValueError("Could not fit ARIMA model")

        # Generate forecast with enhanced confidence intervals
        forecast_result = best_model.get_forecast(steps=forecast_days)
        forecast = forecast_result.predicted_mean
        forecast_ci = forecast_result.conf_int(alpha=1-self.confidence_level)

        # Calculate prediction intervals (wider than confidence intervals)
        prediction_intervals = forecast_result.prediction_intervals(alpha=1-self.confidence_level)

        # Create forecast dates
        last_date = ts_data.index[-1]
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

        # Calculate additional metrics
        residuals = best_model.resid
        residual_std = np.std(residuals)

        return {
            'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
            'values': forecast.tolist(),
            'lower_bound': forecast_ci.iloc[:, 0].tolist(),
            'upper_bound': forecast_ci.iloc[:, 1].tolist(),
            'prediction_lower': prediction_intervals.iloc[:, 0].tolist(),
            'prediction_upper': prediction_intervals.iloc[:, 1].tolist(),
            'aic': best_model.aic,
            'bic': best_model.bic,
            'model_params': f'ARIMA{best_order}',
            'residual_std': residual_std,
            'confidence_level': self.confidence_level,
            'status': 'success'
        }
    
    def _fit_exponential_smoothing(self, ts_data: pd.Series, forecast_days: int) -> Dict:
        """Fit Exponential Smoothing model with enhanced confidence intervals."""
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels not available")

        try:
            # Try multiple exponential smoothing configurations
            models_to_try = [
                {'trend': 'add', 'seasonal': None, 'name': 'Holt Linear'},
                {'trend': 'mul', 'seasonal': None, 'name': 'Holt Multiplicative'},
                {'trend': None, 'seasonal': None, 'name': 'Simple Exponential'}
            ]

            best_model = None
            best_aic = float('inf')
            best_config = None

            for config in models_to_try:
                try:
                    model = ExponentialSmoothing(ts_data,
                                               trend=config['trend'],
                                               seasonal=config['seasonal'])
                    fitted_model = model.fit()

                    if fitted_model.aic < best_aic and not np.isnan(fitted_model.aic):
                        best_aic = fitted_model.aic
                        best_model = fitted_model
                        best_config = config
                except:
                    continue

            if best_model is None:
                raise ValueError("Could not fit any exponential smoothing model")

            # Generate forecast
            forecast = best_model.forecast(steps=forecast_days)

            # Enhanced confidence intervals using residual analysis
            residuals = best_model.resid
            residuals_std = np.std(residuals)

            # Calculate confidence intervals with proper scaling
            z_score = 1.96  # 95% confidence level
            margin = z_score * residuals_std

            # For prediction intervals, account for forecast uncertainty
            prediction_margin = z_score * residuals_std * np.sqrt(1 + np.arange(1, forecast_days + 1) / len(ts_data))

            # Create forecast dates
            last_date = ts_data.index[-1]
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

            return {
                'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
                'values': forecast.tolist(),
                'lower_bound': (forecast - margin).tolist(),
                'upper_bound': (forecast + margin).tolist(),
                'prediction_lower': (forecast - prediction_margin).tolist(),
                'prediction_upper': (forecast + prediction_margin).tolist(),
                'aic': best_model.aic,
                'bic': getattr(best_model, 'bic', None),
                'model_params': best_config['name'],
                'residual_std': residuals_std,
                'confidence_level': self.confidence_level,
                'status': 'success'
            }

        except Exception as e:
            # Fallback to simple exponential smoothing
            return self._fit_simple_exponential(ts_data, forecast_days)
    
    def _fit_simple_exponential(self, ts_data: pd.Series, forecast_days: int) -> Dict:
        """Fit Simple Exponential Smoothing model with enhanced confidence intervals."""
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels not available")

        model = SimpleExpSmoothing(ts_data)
        fitted_model = model.fit()

        # Generate forecast
        forecast = fitted_model.forecast(steps=forecast_days)

        # Enhanced confidence intervals for simple exponential smoothing
        residuals = fitted_model.resid
        residuals_std = np.std(residuals)

        # Calculate confidence intervals
        z_score = 1.96  # 95% confidence level
        margin = z_score * residuals_std

        # For prediction intervals, account for increasing uncertainty over time
        prediction_margins = [z_score * residuals_std * np.sqrt(1 + i / len(ts_data))
                             for i in range(1, forecast_days + 1)]

        # Create forecast dates
        last_date = ts_data.index[-1]
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

        # Simple ES gives constant forecast, but we'll create arrays for consistency
        forecast_values = [forecast] * forecast_days

        return {
            'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
            'values': forecast_values,
            'lower_bound': [forecast - margin] * forecast_days,
            'upper_bound': [forecast + margin] * forecast_days,
            'prediction_lower': [forecast - margin for margin in prediction_margins],
            'prediction_upper': [forecast + margin for margin in prediction_margins],
            'aic': fitted_model.aic,
            'bic': getattr(fitted_model, 'bic', None),
            'model_params': 'Simple Exponential Smoothing',
            'residual_std': residuals_std,
            'confidence_level': self.confidence_level,
            'status': 'success'
        }
    
    def _fit_linear_trend(self, ts_data: pd.Series, forecast_days: int) -> Dict:
        """Fit linear trend model with enhanced confidence intervals."""
        # Convert dates to numeric for regression
        x = np.arange(len(ts_data))
        y = ts_data.values

        # Simple linear regression
        coeffs = np.polyfit(x, y, 1)
        trend_line = np.poly1d(coeffs)

        # Calculate MSE and other metrics
        predicted = trend_line(x)
        residuals = y - predicted
        mse = np.mean(residuals ** 2)
        residual_std = np.std(residuals)

        # Generate forecast
        future_x = np.arange(len(ts_data), len(ts_data) + forecast_days)
        forecast_values = trend_line(future_x)

        # Enhanced confidence intervals for linear regression
        n = len(ts_data)
        x_mean = np.mean(x)
        sxx = np.sum((x - x_mean) ** 2)

        # Calculate standard errors for each forecast point
        z_score = 1.96  # 95% confidence level
        confidence_margins = []
        prediction_margins = []

        for i, future_point in enumerate(future_x):
            # Standard error for confidence interval (mean prediction)
            se_conf = residual_std * np.sqrt(1/n + (future_point - x_mean)**2 / sxx)
            confidence_margins.append(z_score * se_conf)

            # Standard error for prediction interval (individual prediction)
            se_pred = residual_std * np.sqrt(1 + 1/n + (future_point - x_mean)**2 / sxx)
            prediction_margins.append(z_score * se_pred)

        # Create forecast dates
        last_date = ts_data.index[-1]
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

        return {
            'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
            'values': forecast_values.tolist(),
            'lower_bound': (forecast_values - np.array(confidence_margins)).tolist(),
            'upper_bound': (forecast_values + np.array(confidence_margins)).tolist(),
            'prediction_lower': (forecast_values - np.array(prediction_margins)).tolist(),
            'prediction_upper': (forecast_values + np.array(prediction_margins)).tolist(),
            'mse': mse,
            'residual_std': residual_std,
            'model_params': f'Linear trend: y = {coeffs[0]:.3f}x + {coeffs[1]:.1f}',
            'confidence_level': self.confidence_level,
            'r_squared': 1 - (np.sum(residuals**2) / np.sum((y - np.mean(y))**2)),
            'status': 'success'
        }
    
    def _fit_moving_average(self, ts_data: pd.Series, forecast_days: int) -> Dict:
        """Fit moving average model with enhanced confidence intervals."""
        # Use adaptive window size based on data length
        window = min(7, max(3, len(ts_data) // 4))
        ma_value = ts_data.tail(window).mean()

        # Calculate enhanced statistics
        recent_data = ts_data.tail(window)
        std_value = recent_data.std()

        # Calculate confidence intervals
        z_score = 1.96  # 95% confidence level

        # For moving average, confidence interval accounts for sample size
        confidence_margin = z_score * std_value / np.sqrt(window)

        # Prediction intervals are wider and account for increasing uncertainty
        prediction_margins = [z_score * std_value * np.sqrt(1 + 1/window + i/(window*2))
                             for i in range(1, forecast_days + 1)]

        # Create forecast dates
        last_date = ts_data.index[-1]
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]

        # Calculate additional metrics
        mse = std_value ** 2

        return {
            'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
            'values': [ma_value] * forecast_days,
            'lower_bound': [ma_value - confidence_margin] * forecast_days,
            'upper_bound': [ma_value + confidence_margin] * forecast_days,
            'prediction_lower': [ma_value - margin for margin in prediction_margins],
            'prediction_upper': [ma_value + margin for margin in prediction_margins],
            'mse': mse,
            'residual_std': std_value,
            'model_params': f'{window}-day moving average',
            'confidence_level': self.confidence_level,
            'status': 'success'
        }
    
    def _create_error_response(self, error_message: str) -> Dict:
        """Create standardized error response."""
        return {
            'status': 'error',
            'error_message': error_message,
            'dates': [],
            'values': [],
            'lower_bound': [],
            'upper_bound': [],
            'model_used': 'none'
        }
    
    def get_forecast_summary(self, forecast_result: Dict) -> str:
        """Generate human-readable forecast summary."""
        if forecast_result['status'] == 'error':
            return f"Forecast unavailable: {forecast_result['error_message']}"

        values = forecast_result['values']
        if not values:
            return "No forecast data available"

        avg_forecast = np.mean(values)
        trend = "stable"

        if len(values) > 1:
            if values[-1] > values[0] * 1.1:
                trend = "increasing"
            elif values[-1] < values[0] * 0.9:
                trend = "decreasing"

        model_used = forecast_result.get('model_used', 'unknown')

        return (f"7-day forecast shows {trend} pattern with average of "
                f"{avg_forecast:.1f} visits (model: {model_used})")

    def get_enhanced_forecast_interpretation(self, forecast_result: Dict) -> Dict:
        """Generate enhanced forecast interpretation with confidence intervals."""
        if forecast_result['status'] == 'error':
            return {
                'summary': f"Forecast unavailable: {forecast_result['error_message']}",
                'confidence_interpretation': "No confidence intervals available",
                'risk_assessment': "Unable to assess risk",
                'recommendations': []
            }

        values = forecast_result['values']
        lower_bounds = forecast_result.get('lower_bound', [])
        upper_bounds = forecast_result.get('upper_bound', [])

        if not values:
            return {
                'summary': "No forecast data available",
                'confidence_interpretation': "No confidence intervals available",
                'risk_assessment': "Unable to assess risk",
                'recommendations': []
            }

        # Calculate key metrics
        avg_forecast = np.mean(values)
        min_forecast = min(values)
        max_forecast = max(values)

        # Confidence interval analysis
        if lower_bounds and upper_bounds:
            avg_lower = np.mean(lower_bounds)
            avg_upper = np.mean(upper_bounds)
            avg_width = avg_upper - avg_lower

            confidence_interpretation = (
                f"The system predicts a likely range of {avg_lower:.1f} to {avg_upper:.1f} visits "
                f"over the next 7 days (95% confidence). The average uncertainty is ±{avg_width/2:.1f} visits."
            )

            # Risk assessment based on confidence intervals
            if avg_width > avg_forecast * 0.5:  # High uncertainty
                risk_level = "HIGH"
                risk_explanation = "Wide confidence intervals indicate high uncertainty in predictions."
            elif avg_width > avg_forecast * 0.25:  # Medium uncertainty
                risk_level = "MEDIUM"
                risk_explanation = "Moderate confidence intervals suggest reasonable prediction reliability."
            else:  # Low uncertainty
                risk_level = "LOW"
                risk_explanation = "Narrow confidence intervals indicate high prediction confidence."
        else:
            confidence_interpretation = "Confidence intervals not available for this model."
            risk_level = "UNKNOWN"
            risk_explanation = "Cannot assess prediction uncertainty."

        # Trend analysis
        if len(values) > 1:
            if values[-1] > values[0] * 1.1:
                trend = "increasing"
                trend_concern = "Monitor for potential capacity issues"
            elif values[-1] < values[0] * 0.9:
                trend = "decreasing"
                trend_concern = "Positive trend - reduced healthcare burden"
            else:
                trend = "stable"
                trend_concern = "Consistent demand expected"
        else:
            trend = "stable"
            trend_concern = "Single-point forecast"

        # Generate recommendations
        recommendations = []

        if trend == "increasing":
            recommendations.extend([
                "Consider increasing staffing levels",
                "Monitor resource availability",
                "Prepare for potential surge capacity needs"
            ])
        elif trend == "decreasing":
            recommendations.extend([
                "Opportunity for resource reallocation",
                "Continue monitoring for trend reversal",
                "Maintain baseline preparedness"
            ])
        else:
            recommendations.extend([
                "Maintain current staffing levels",
                "Continue routine monitoring",
                "Prepare for potential variations within confidence intervals"
            ])

        if risk_level == "HIGH":
            recommendations.append("Increase monitoring frequency due to high uncertainty")

        return {
            'summary': f"7-day forecast: {avg_forecast:.1f} average visits ({trend} trend)",
            'confidence_interpretation': confidence_interpretation,
            'risk_assessment': f"{risk_level} uncertainty - {risk_explanation}",
            'trend_analysis': f"{trend.title()} trend - {trend_concern}",
            'recommendations': recommendations,
            'key_metrics': {
                'average_forecast': avg_forecast,
                'min_forecast': min_forecast,
                'max_forecast': max_forecast,
                'trend': trend,
                'risk_level': risk_level
            }
        }


# Test function
def test_forecasting_engine():
    """Test the forecasting engine with sample data."""
    engine = ForecastingEngine()

    # Test with existing hospital data
    forecast = engine.generate_forecast(
        hospital_name="South Bronx Health Hub",
        zip_code="10455",
        forecast_days=7,
        days_back=None  # Use all available data
    )

    print("Forecast Test Results:")
    print(f"Status: {forecast['status']}")
    if forecast['status'] == 'success':
        print(f"Model used: {forecast['model_used']}")
        print(f"Forecast values: {[round(v, 1) for v in forecast['values']]}")
        print(f"Summary: {engine.get_forecast_summary(forecast)}")
        print(f"Historical data points: {forecast['historical_data_points']}")
    else:
        print(f"Error: {forecast['error_message']}")

if __name__ == "__main__":
    test_forecasting_engine()
