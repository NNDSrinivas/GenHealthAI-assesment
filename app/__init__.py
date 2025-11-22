import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from pymongo import MongoClient
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

def create_app():
    """Application factory pattern for Flask app creation."""
    app = Flask(__name__)
    
    # Production Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Enable CORS with production settings
    CORS(app, 
         origins=['*'] if os.getenv('FLASK_ENV') == 'development' else [],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])
    
    # Add proxy fix for AWS load balancers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    # Setup logging
    setup_logging()
    
    # Add request/response middleware
    setup_middleware(app)
    
    # Add error handlers
    setup_error_handlers(app)
    
    # Initialize MongoDB connection
    init_database(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Add API info endpoint
    setup_api_routes(app)
    
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

def setup_middleware(app):
    """Setup request/response middleware."""
    @app.before_request
    def log_request_info():
        if request.endpoint not in ['health.health_check', 'static']:
            app.logger.info('Request: %s %s from %s', 
                          request.method, request.url, request.remote_addr)
    
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY' 
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Server'] = 'GenHealth.AI API'
        return response

def setup_error_handlers(app):
    """Setup global error handlers."""
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status': 404,
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'GenHealth.AI Clinical Document API'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error('Internal error: %s', error)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An internal error occurred. Please try again later.',
            'status': 500,
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'GenHealth.AI Clinical Document API'
        }), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            'error': 'File Too Large',
            'message': 'File size exceeds maximum allowed limit (16MB)',
            'status': 413,
            'timestamp': datetime.utcnow().isoformat()
        }), 413

def setup_api_routes(app):
    """Setup main API information routes."""
    @app.route('/')
    def api_root():
        return render_template('index.html')
    
    @app.route('/api')
    def api_info():
        return jsonify({
            'service': 'GenHealth.AI Clinical Document Processing API',
            'version': '1.0.0',
            'status': 'operational',
            'environment': os.getenv('FLASK_ENV', 'production'),
            'capabilities': {
                'document_processing': True,
                'ocr_extraction': True,
                'patient_data_extraction': True,
                'order_management': True,
                'activity_logging': True
            },
            'supported_formats': ['PDF', 'PNG', 'JPG', 'TIFF'],
            'max_file_size': '16MB',
            'timestamp': datetime.utcnow().isoformat()
        })

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