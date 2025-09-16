import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import structlog

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object('app.config.Config')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=["http://localhost:3000"])
    
    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Register blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app
