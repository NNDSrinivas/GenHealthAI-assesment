import os
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern for Flask app creation."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    
    # Enable CORS for all routes
    CORS(app)
    
    # Setup logging
    setup_logging()
    
    # Initialize MongoDB connection
    init_database(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

def setup_logging():
    """Configure application logging."""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def init_database(app):
    """Initialize MongoDB connection."""
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGODB_DB_NAME', 'clinical_docs')
    
    try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.admin.command('ismaster')
        
        app.mongo_client = client
        app.db = client[db_name]
        
        logging.info(f"Successfully connected to MongoDB: {db_name}")
        
    except Exception as e:
        logging.warning(f"MongoDB connection failed: {str(e)}. Running without database.")
        # Create a mock database for demonstration
        app.mongo_client = None
        app.db = None

def register_blueprints(app):
    """Register application blueprints."""
    from app.routes.orders import orders_bp
    from app.routes.documents import documents_bp
    from app.routes.patients import patients_bp
    from app.routes.health import health_bp
    
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(documents_bp, url_prefix='/api/documents')
    app.register_blueprint(patients_bp, url_prefix='/api/patients')
    app.register_blueprint(health_bp)
    
    # Initialize database service after MongoDB connection attempt
    from app.services.database import db_service
    if hasattr(app, 'db') and app.db is not None:
        db_service.init_db(app.db)
    else:
        # Use in-memory database for testing
        from app.services.memory_db import memory_db
        # Replace db_service methods with memory_db methods
        for attr in dir(memory_db):
            if not attr.startswith('_') and callable(getattr(memory_db, attr)):
                setattr(db_service, attr, getattr(memory_db, attr))
        logging.info("Using in-memory database for testing")