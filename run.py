import os
from app import create_app
from app.services.database import db_service

def initialize_database():
    """Initialize database with the Flask app context."""
    app = create_app()
    
    with app.app_context():
        # Initialize database service with the app's database
        if hasattr(app, 'db'):
            db_service.init_db(app.db)
            print("Database initialized successfully")
        else:
            print("Warning: Database connection not established")

if __name__ == '__main__':
    app = create_app()
    
    # Run the application
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 5002))
    
    print(f"Starting Clinical Document Processing API on port {port}")
    print(f"Debug mode: {debug_mode}")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /info - API information")
    print("  POST /api/documents/upload - Upload document for processing")
    print("  POST /api/documents/test - Test OCR extraction")
    print("  GET  /api/documents/<id> - Get document details")
    print("  GET  /api/orders - List orders")
    print("  POST /api/orders - Create new order")
    print("  GET  /api/patients - List patients")
    print("  GET  /api/patients/<id> - Get patient details")
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)