"""
FloodVoice Configuration
Centralized configuration management for the application
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'floodvoice_secret_key_2025')
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'floodvoice.db')
    
    # FloodNet API
    FLOODNET_API_URL = os.environ.get('FLOODNET_API_URL', 'https://api.floodnet.nyc/sensors')
    FLOODNET_API_KEY = os.environ.get('FLOODNET_API_KEY', None)
    FLOODNET_UPDATE_INTERVAL = int(os.environ.get('FLOODNET_UPDATE_INTERVAL', 300))  # 5 minutes
    
    # OpenRouter API (for AI insights)
    OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', None)
    OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
    AI_MODEL = 'openai/gpt-3.5-turbo'
    
    # NYC GeoClient API (for geocoding)
    NYC_GEOCLIENT_APP_ID = os.environ.get('NYC_GEOCLIENT_APP_ID', None)
    NYC_GEOCLIENT_APP_KEY = os.environ.get('NYC_GEOCLIENT_APP_KEY', None)
    
    # Social Media APIs
    TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY', None)
    TWITTER_API_SECRET = os.environ.get('TWITTER_API_SECRET', None)
    
    # Alert Thresholds
    MINOR_FLOOD_THRESHOLD = float(os.environ.get('MINOR_FLOOD_THRESHOLD', 2.0))  # inches
    MODERATE_FLOOD_THRESHOLD = float(os.environ.get('MODERATE_FLOOD_THRESHOLD', 6.0))
    MAJOR_FLOOD_THRESHOLD = float(os.environ.get('MAJOR_FLOOD_THRESHOLD', 12.0))
    
    # Correlation Settings
    MAX_CORRELATION_DISTANCE_MILES = float(os.environ.get('MAX_CORRELATION_DISTANCE_MILES', 1.0))
    CORRELATION_TIME_WINDOW_HOURS = int(os.environ.get('CORRELATION_TIME_WINDOW_HOURS', 2))
    
    # Demo Mode
    DEMO_MODE = os.environ.get('DEMO_MODE', 'True').lower() == 'true'
    USE_MOCK_DATA = os.environ.get('USE_MOCK_DATA', 'True').lower() == 'true'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    DEMO_MODE = True
    USE_MOCK_DATA = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    DEMO_MODE = False
    USE_MOCK_DATA = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env='default'):
    """Get configuration based on environment"""
    return config.get(env, config['default'])

