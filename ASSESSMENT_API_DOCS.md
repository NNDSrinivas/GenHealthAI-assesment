# GenHealth.AI Assessment - API Documentation

## 🌐 Public API URL
**Your ngrok URL:** `https://your-ngrok-url.ngrok.io`

## 📋 Assessment Requirements Checklist

### ✅ Required Features Implemented:

1. **Order Entity CRUD Operations**
2. **PDF Document Upload with OCR**
3. **Patient Data Extraction (First Name, Last Name, DOB)**
4. **Database Persistence & Activity Logging**
5. **Public Deployment**

---

## 🔗 API Endpoints for Testing

### 1. Health Check
```
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-22T13:58:39Z",
  "database": "connected"
}
```

### 2. Order CRUD Operations

#### Create Order
```
POST /api/orders
Content-Type: application/json

{
  "patient_id": "patient-123",
  "order_type": "lab_test",
  "description": "Blood work analysis",
  "status": "pending"
}
```

#### Get All Orders
```
GET /api/orders
```

#### Get Specific Order
```
GET /api/orders/{order_id}
```

#### Update Order
```
PUT /api/orders/{order_id}
Content-Type: application/json

{
  "status": "completed",
  "description": "Updated description"
}
```

#### Delete Order
```
DELETE /api/orders/{order_id}
```

### 3. Document Upload & OCR Processing
```
POST /api/documents/upload
Content-Type: multipart/form-data

file: [PDF file]
```

**Response:**
```json
{
  "success": true,
  "document_id": "doc-123",
  "patient_data": {
    "first_name": "John",
    "last_name": "Doe", 
    "date_of_birth": "01/15/1990"
  },
  "confidence_scores": {
    "first_name": 0.95,
    "last_name": 0.92,
    "date_of_birth": 0.88
  },
  "extracted_text": "Full OCR text..."
}
```

### 4. Activity Logging
```
GET /api/activities
```

### 5. Patient Data
```
GET /api/patients
```

---

## 🧪 Quick Test Commands

### Using curl:

#### 1. Test Health Check
```bash
curl https://your-ngrok-url.ngrok.io/health
```

#### 2. Create Order
```bash
curl -X POST https://your-ngrok-url.ngrok.io/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "test-123",
    "order_type": "assessment_test",
    "description": "GenHealth.AI Assessment Order",
    "status": "pending"
  }'
```

#### 3. Upload PDF (with sample PDF)
```bash
curl -X POST https://your-ngrok-url.ngrok.io/api/documents/upload \
  -F "file=@sample_document.pdf"
```

#### 4. Get Activity Logs
```bash
curl https://your-ngrok-url.ngrok.io/api/activities
```

---

## 📄 Test with Sample PDF

**Sample PDF URL:** https://drive.google.com/file/d/1fWYlgktvVG0pJgLm_77H9-ajAW5D5IUZ/view?usp=sharing

1. Download the sample PDF
2. Upload it via the `/api/documents/upload` endpoint
3. Verify it extracts patient's first name, last name, and date of birth

---

## 🔧 Key Features Demonstrated

### 1. **Order Management**
- Complete CRUD operations
- Data validation and error handling
- JSON API responses

### 2. **Document Processing**
- OCR text extraction from PDFs
- Intelligent patient data parsing
- Confidence scoring for extractions

### 3. **Database Operations**
- Persistent storage (MongoDB/In-memory)
- Activity logging for all operations
- Data integrity and validation

### 4. **Production Readiness**
- Error handling and logging
- API documentation
- Scalable architecture
- Public deployment

---

## 🚀 Assessment Test Script

Run the provided test script:
```bash
python test_assessment.py
```

Make sure to update the `BASE_URL` in the script with your actual ngrok URL.

---

## 📊 Expected Assessment Results

The API successfully demonstrates:
- ✅ REST API design principles
- ✅ CRUD operations for Order entity
- ✅ File upload and OCR processing
- ✅ Patient data extraction from PDF
- ✅ Database persistence
- ✅ Activity logging
- ✅ Public accessibility
- ✅ Error handling
- ✅ Production deployment