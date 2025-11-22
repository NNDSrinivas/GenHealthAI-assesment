import os
from flask import Blueprint, jsonify

# Health check blueprint
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring and deployment."""
    return jsonify({
        'status': 'healthy',
        'service': 'Clinical Document Processing API',
        'version': '1.0.0',
        'timestamp': str(__import__('datetime').datetime.utcnow())
    }), 200

@health_bp.route('/info', methods=['GET'])
def api_info():
    """API information endpoint."""
    return jsonify({
        'name': 'Clinical Document Processing API',
        'version': '1.0.0',
        'description': 'OCR-based clinical document processing with patient data extraction',
        'endpoints': {
            'documents': '/api/documents',
            'orders': '/api/orders', 
            'patients': '/api/patients',
            'health': '/health',
            'info': '/info'
        },
        'features': [
            'OCR document processing',
            'Patient data extraction',
            'Order management',
            'Activity logging',
            'Batch processing'
        ]
    }), 200