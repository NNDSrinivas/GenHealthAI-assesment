import os
from flask import Blueprint, jsonify, request
from app.utils.monitoring import create_detailed_health_response

# Health check blueprint
health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Advanced health check endpoint for AWS load balancers and monitoring."""
    try:
        # Basic health check for load balancers (fast response)
        if request.args.get('simple') == 'true':
            return jsonify({
                'status': 'healthy',
                'service': 'GenHealth.AI Clinical Document API',
                'timestamp': str(__import__('datetime').datetime.utcnow())
            }), 200
        
        # Detailed health check with system metrics
        health_data = create_detailed_health_response()
        
        # Return appropriate status code based on health
        status_code = 200 if health_data['status'] == 'healthy' else 503
        return jsonify(health_data), status_code
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'service': 'GenHealth.AI Clinical Document API',
            'error': str(e),
            'timestamp': str(__import__('datetime').datetime.utcnow())
        }), 503

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