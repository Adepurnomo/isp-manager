"""
ISP Manager Flask Application Factory
Initializes Flask app with all extensions and blueprints
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
scheduler = BackgroundScheduler(daemon=True)

logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """
    Application factory function.
    Creates and configures the Flask application with all extensions.
    
    Args:
        config_name: Configuration environment (development, production, testing)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'production':
        from app.config import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        from app.config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from app.config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    with app.app_context():
        from app.routes.auth import auth_bp
        from app.routes.customers import customers_bp
        from app.routes.invoices import invoices_bp
        from app.routes.payments import payments_bp
        from app.routes.routers import routers_bp
        from app.routes.services import services_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(customers_bp)
        app.register_blueprint(invoices_bp)
        app.register_blueprint(payments_bp)
        app.register_blueprint(routers_bp)
        app.register_blueprint(services_bp)
        
        # Create tables
        db.create_all()
        
        # Start scheduler if not already running
        if not scheduler.running:
            from app.jobs.billing_jobs import schedule_billing_jobs
            schedule_billing_jobs()
            scheduler.start()
    
    # Add CLI commands
    add_cli_commands(app)
    
    logger.info(f"Flask app created with config: {config_name}")
    return app

def add_cli_commands(app):
    """
    Register Flask CLI commands for database and admin management.
    """
    import click
    from app.models.users import User
    from app.models.tenants import Tenant
    
    @app.cli.command('create-admin')
    @click.option('--email', prompt='Admin email', type=str)
    @click.option('--password', prompt='Admin password', hide_input=True, confirmation_prompt=True, type=str)
    @click.option('--tenant-name', prompt='Tenant name', type=str)
    def create_admin(email, password, tenant_name):
        """Create a super admin user and tenant."""
        try:
            # Create tenant
            tenant = Tenant(
                name=tenant_name,
                code=tenant_name.lower().replace(' ', '_'),
                is_active=True
            )
            db.session.add(tenant)
            db.session.commit()
            
            # Create admin user
            admin = User(
                email=email,
                first_name='Admin',
                last_name='User',
                tenant_id=tenant.id,
                role='super_admin',
                is_active=True
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            
            click.echo(f"✓ Admin user created: {email}")
            click.echo(f"✓ Tenant created: {tenant_name}")
        except Exception as e:
            db.session.rollback()
            click.echo(f"✗ Error: {str(e)}", err=True)
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize database with migrations."""
        try:
            db.create_all()
            click.echo("✓ Database initialized")
        except Exception as e:
            click.echo(f"✗ Error: {str(e)}", err=True)
