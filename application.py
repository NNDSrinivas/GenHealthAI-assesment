#!/usr/bin/env python3
"""
Production WSGI Application Entry Point
Clinical Document Processing API
"""

import os
import sys
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from werkzeug.middleware.proxy_fix import ProxyFix
from app import create_app

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

# Create application instance
application = create_app()

# Add proxy fix for AWS load balancers
application.wsgi_app = ProxyFix(
    application.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)

# AWS health check endpoint
@application.route('/health')
def health_check():
    """AWS health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'GenHealth.AI Clinical Document API',
        'version': '1.0.0',
        'environment': 'production'
    }, 200

if __name__ == '__main__':
    # For local development and Railway deployment
    port = int(os.environ.get('PORT', 8000))
    application.run(host='0.0.0.0', port=port, debug=False)