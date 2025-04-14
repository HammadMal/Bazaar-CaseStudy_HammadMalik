import os
import redis
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change')
    
    # Main database URI (primary/write database)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///bazaar.db')
    
    # Read replica database URI (used for read operations)
    SQLALCHEMY_READ_REPLICA_URI = os.environ.get('READ_DATABASE_URL', None)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    RATELIMIT_STRATEGY = 'fixed-window'
    
    # Session configuration for Redis
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.from_url(os.environ.get('REDIS_URL', 'redis://redis:6379/0'))
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # RabbitMQ configuration
    RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672')
    ASYNC_OPERATIONS_ENABLED = os.environ.get('ASYNC_OPERATIONS_ENABLED', 'True').lower() == 'true'
    QUEUE_RETRY_INTERVAL = int(os.environ.get('QUEUE_RETRY_INTERVAL', 5))  # seconds
    QUEUE_MAX_RETRIES = int(os.environ.get('QUEUE_MAX_RETRIES', 3))
    
    # Query caching configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default cache timeout


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Get configuration based on environment
def get_config():
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])