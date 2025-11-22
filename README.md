# Clinical Document Processing API

A production-ready Flask REST API for processing clinical documents using OCR technology. Extracts structured patient data from unstructured documents (PDFs, images, DOCX files) and provides CRUD operations for order management.

## Features

- **Document Processing**: OCR-based extraction using Tesseract for multiple file formats (.pdf, .tiff, .png, .docx)
- **Patient Data Extraction**: Automated extraction of patient information (name, DOB) from clinical documents
- **Order Management**: Full CRUD operations for order entities
- **MongoDB Integration**: Scalable NoSQL database for document and patient data storage
- **Activity Logging**: Comprehensive logging for audit trails and monitoring
- **Batch Processing**: Support for processing large volumes of documents
- **RESTful API**: Clean API design with comprehensive documentation
- **Production Ready**: Error handling, validation, and deployment configuration

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Tesseract OCR**
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu
   sudo apt-get install tesseract-ocr
   ```

3. **Setup MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Update connection string in `.env` file

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run Application**
   ```bash
   python run.py
   ```

## API Endpoints

### Documents
- `POST /api/documents/upload` - Upload and process document
- `GET /api/documents/{id}` - Get processed document
- `POST /api/documents/batch` - Batch process multiple documents

### Orders
- `GET /api/orders` - List all orders
- `POST /api/orders` - Create new order
- `GET /api/orders/{id}` - Get specific order
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order

### Patients
- `GET /api/patients` - List patients
- `GET /api/patients/{id}` - Get patient details

## Architecture

```
app/
├── models/          # Data models (Patient, Order, Document)
├── routes/          # API route handlers
├── services/        # Business logic (OCR, document processing)
├── utils/           # Helper functions and utilities
└── __init__.py      # Flask application factory
```

## Testing

```bash
pytest tests/
```

## Deployment

The application is containerized and ready for deployment on platforms like Heroku, AWS, or Google Cloud.

```bash
docker build -t clinical-doc-api .
docker run -p 5000:5000 clinical-doc-api
```

## Technology Stack

- **Backend**: Flask, Python 3.9+
- **Database**: MongoDB
- **OCR**: Tesseract OCR Engine
- **Document Processing**: PDF2Image, python-docx, OpenCV
- **Testing**: pytest
- **Deployment**: Docker, Gunicorn