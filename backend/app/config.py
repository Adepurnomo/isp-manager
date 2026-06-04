"""
ISP Manager Configuration Settings
Different configurations for development, testing, and production environments
"""

import os
from datetime import timedelta
from app.database import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_ENGINE_OPTIONS

class BaseConfig:
    """
    Base configuration with common settings for all environments.
    """
    # Database
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = SQLALCHEMY_ENGINE_OPTIONS
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    
    # Application
    APP_NAME = 'ISP Manager'
    DEBUG = False
    TESTING = False
    ENVIRONMENT = 'development'
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # APScheduler
    SCHEDULER_API_ENABLED = True
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 5}
    }
    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 1,
        'misfire_grace_time': 15*60
    }

class DevelopmentConfig(BaseConfig):
    """
    Development configuration for local development.
    """
    DEBUG = True
    TESTING = False
    ENVIRONMENT = 'development'
    LOG_LEVEL = 'DEBUG'
    SQLALCHEMY_ECHO = True

class TestingConfig(BaseConfig):
    """
    Testing configuration for automated tests.
    """
    TESTING = True
    ENVIRONMENT = 'testing'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False

class ProductionConfig(BaseConfig):
    """
    Production configuration for production deployment.
    Must be configured via environment variables.
    """
    ENVIRONMENT = 'production'
    DEBUG = False
    TESTING = False
    
    # Enforce environment variables in production
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError('JWT_SECRET_KEY environment variable must be set in production')
    
    # Database URL must be explicitly set
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError('DATABASE_URL environment variable must be set in production')
