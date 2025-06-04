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
        """Fit ARIMA model and generate forecast."""
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels not available")
        
        # Auto ARIMA with simple parameter selection
        best_aic = float('inf')
        best_model = None
        
        # Try different ARIMA parameters
        for p in range(3):
            for d in range(2):
                for q in range(3):
                    try:
                        model = ARIMA(ts_data, order=(p, d, q))
                        fitted_model = model.fit()
                        
                        if fitted_model.aic < best_aic:
                            best_aic = fitted_model.aic
                            best_model = fitted_model
                    except:
                        continue
        
        if best_model is None:
            raise ValueError("Could not fit ARIMA model")
        
        # Generate forecast
        forecast = best_model.forecast(steps=forecast_days)
        forecast_ci = best_model.get_forecast(steps=forecast_days).conf_int()
        
        # Create forecast dates
        last_date = ts_data.index[-1]
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
            'values': forecast.tolist(),
            'lower_bound': forecast_ci.iloc[:, 0].tolist(),
            'upper_bound': forecast_ci.iloc[:, 1].tolist(),
            'aic': best_model.aic,
            'model_params': str(best_model.model.order),
            'status': 'success'
        }
    
    def _fit_exponential_smoothing(self, ts_data: pd.Series, forecast_days: int) -> Dict:
        """Fit Exponential Smoothing model and generate forecast."""
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels not available")
        
        try:
            # Try Holt-Winters exponential smoothing
            model = ExponentialSmoothing(ts_data, trend='add', seasonal=None)
            fitted_model = model.fit()
            
            # Generate forecast
            forecast = fitted_model.forecast(steps=forecast_days)
            
            # Simple confidence intervals (±1.96 * std of residuals)
            residuals_std = np.std(fitted_model.resid)
            margin = 1.96 * residuals_std
            
            # Create forecast dates
            last_date = ts_data.index[-1]
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
            
            return {
                'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
                'values': forecast.tolist(),
                'lower_bound': (forecast - margin).tolist(),
                'upper_bound': (forecast + margin).tolist(),
                'aic': fitted_model.aic,
                'model_params': 'Exponential Smoothing with trend',
                'status': 'success'
            }
            
        except Exception as e:
            # Fallback to simple exponential smoothing
            return self._fit_simple_exponential(ts_data, forecast_days)
    
    def _fit_simple_exponential(self, ts_data: pd.Series, forecast_days: int) -> Dict:
        """Fit Simple Exponential Smoothing model."""
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels not available")
        
        model = SimpleExpSmoothing(ts_data)
        fitted_model = model.fit()
        
        # Generate forecast
        forecast = fitted_model.forecast(steps=forecast_days)
        
        # Simple confidence intervals
        residuals_std = np.std(fitted_model.resid)
        margin = 1.96 * residuals_std
        
        # Create forecast dates
        last_date = ts_data.index[-1]
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
            'values': [forecast] * forecast_days,  # Simple ES gives constant forecast
            'lower_bound': [forecast - margin] * forecast_days,
            'upper_bound': [forecast + margin] * forecast_days,
            'aic': fitted_model.aic,
            'model_params': 'Simple Exponential Smoothing',
            'status': 'success'
        }
    
    def _fit_linear_trend(self, ts_data: pd.Series, forecast_days: int) -> Dict:
        """Fit simple linear trend model."""
        # Convert dates to numeric for regression
        x = np.arange(len(ts_data))
        y = ts_data.values
        
        # Simple linear regression
        coeffs = np.polyfit(x, y, 1)
        trend_line = np.poly1d(coeffs)
        
        # Calculate MSE
        predicted = trend_line(x)
        mse = np.mean((y - predicted) ** 2)
        
        # Generate forecast
        future_x = np.arange(len(ts_data), len(ts_data) + forecast_days)
        forecast_values = trend_line(future_x)
        
        # Simple confidence intervals based on residual standard error
        residuals = y - predicted
        residual_std = np.std(residuals)
        margin = 1.96 * residual_std
        
        # Create forecast dates
        last_date = ts_data.index[-1]
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
            'values': forecast_values.tolist(),
            'lower_bound': (forecast_values - margin).tolist(),
            'upper_bound': (forecast_values + margin).tolist(),
            'mse': mse,
            'model_params': f'Linear trend: y = {coeffs[0]:.2f}x + {coeffs[1]:.2f}',
            'status': 'success'
        }
    
    def _fit_moving_average(self, ts_data: pd.Series, forecast_days: int) -> Dict:
        """Fit simple moving average model."""
        # Use last 7 days for moving average
        window = min(7, len(ts_data))
        ma_value = ts_data.tail(window).mean()
        
        # Calculate standard deviation for confidence intervals
        std_value = ts_data.tail(window).std()
        margin = 1.96 * std_value
        
        # Create forecast dates
        last_date = ts_data.index[-1]
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_days)]
        
        return {
            'dates': [d.strftime('%Y-%m-%d') for d in forecast_dates],
            'values': [ma_value] * forecast_days,
            'lower_bound': [ma_value - margin] * forecast_days,
            'upper_bound': [ma_value + margin] * forecast_days,
            'mse': std_value ** 2,
            'model_params': f'{window}-day moving average',
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
