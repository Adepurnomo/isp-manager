"""
ISP Manager Database Configuration
Handles database connection and session management for Flask-SQLAlchemy
"""

import os
from datetime import datetime, timedelta
from decimal import Decimal

# Database URL - supports MySQL/MariaDB with pymysql driver
SQLALCHEMY_DATABASE_URI = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root:password@localhost:3306/isp_manager'
)

# SQLAlchemy configuration
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False') == 'True'
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'echo_pool': False,
    'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20))
}
