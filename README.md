# Clinical Document Processing API

A REST API for clinical document processing with OCR capabilities for patient data extraction.

## Features

- CRUD operations for Order entity
- OCR document processing (PDF, PNG, JPG, TIFF)
- Patient data extraction (First name, Last name, Date of birth)
- Activity logging and monitoring
- Database persistence with MongoDB
- Production-ready deployment configuration

## API Endpoints

### Orders
- `GET /api/orders` - List all orders
- `POST /api/orders` - Create new order
- `GET /api/orders/{id}` - Get specific order
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order

### Documents
- `POST /api/documents/upload` - Upload document for OCR processing
- `GET /api/documents` - List processed documents

### Other
- `GET /health` - Health check
- `GET /api/patients` - List extracted patients
- `GET /api/activities` - View activity logs

## Installation

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run server: `python run_server.py`

## Deployment

Configured for deployment on:
- Railway
- Render  
- AWS App Runner
- Heroku

## Technology Stack

- Python 3.x
- Flask
- MongoDB
- Tesseract OCR
- Gunicorn