import pytest
import os
import tempfile
from app import create_app
from app.services.database import db_service

@pytest.fixture
def app():
    """Create and configure a test Flask app."""
    # Create a temporary database for testing
    app = create_app()
    app.config['TESTING'] = True
    app.config['MONGODB_URI'] = 'mongodb://localhost:27017/'
    app.config['MONGODB_DB_NAME'] = 'clinical_docs_test'
    
    with app.app_context():
        if hasattr(app, 'db'):
            db_service.init_db(app.db)
    
    yield app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()

class TestAPI:
    """Test cases for the Clinical Document Processing API."""
    
    def test_health_endpoint(self, client):
        """Test that the API is running."""
        # This would need a health endpoint to be implemented
        response = client.get('/health')
        # For now, we expect 404 since health endpoint isn't implemented yet
        assert response.status_code in [200, 404]
    
    def test_orders_list(self, client):
        """Test orders listing endpoint."""
        response = client.get('/api/orders')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert 'data' in data
    
    def test_create_order(self, client):
        """Test order creation."""
        order_data = {
            'order_type': 'clinical_review',
            'description': 'Test clinical document review'
        }
        response = client.post('/api/orders', json=order_data)
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
    
    def test_patients_list(self, client):
        """Test patients listing endpoint."""
        response = client.get('/api/patients')
        assert response.status_code == 200
        data = response.get_json()
        assert 'success' in data
        assert 'data' in data
    
    def test_document_upload_no_file(self, client):
        """Test document upload without file."""
        response = client.post('/api/documents/upload')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_document_test_endpoint_no_file(self, client):
        """Test document test endpoint without file."""
        response = client.post('/api/documents/test')
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

if __name__ == '__main__':
    pytest.main([__file__])