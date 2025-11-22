# GenHealth.AI Assessment API - Deployment Guide

## Current Status
The Flask API with Order CRUD operations and OCR processing is ready for deployment. All local tests pass successfully.

## ✅ Recommended: Railway Deployment
Railway is now configured with proper system dependencies for OCR processing.

### Railway Setup:
1. Go to [Railway](https://railway.app)
2. Connect your GitHub account
3. Select the `GenHealthAI-assesment` repository
4. Railway will automatically deploy using our configuration

**Files configured:**
- `nixpacks.toml` - Installs tesseract-ocr and other system dependencies
- `railway.json` - Deployment configuration
- `Procfile` - Production server command

### Environment Variables to set in Railway:
```
MONGODB_URI=mongodb+srv://your-connection-string  # Optional - uses in-memory if not set
FLASK_ENV=production
PORT=5000  # Railway sets this automatically
```

## 🚀 Alternative: Render Deployment
If Railway continues to have issues, Render is another excellent option:

1. Go to [Render](https://render.com)
2. Connect GitHub repository
3. Create a new Web Service
4. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 2 -b 0.0.0.0:$PORT run:app`

## 📱 Alternative: Vercel Deployment
For a serverless option (though less ideal for file uploads):

```bash
npm i -g vercel
vercel
```

## 🔧 Local Testing
To test locally before deployment:
```bash
python run.py
```

## 📋 API Endpoints
Once deployed, your public API will have:

- `GET /health` - Health check
- `GET /api/orders` - List all orders
- `POST /api/orders` - Create new order
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order
- `POST /api/documents/upload` - Upload and process documents
- `GET /api/patients/{id}` - Get patient data

## 🔐 Security Notes
- Environment variables are secured using `.env.template`
- No secrets are committed to the repository
- CORS is properly configured for web access
- Input validation is implemented on all endpoints

## 📊 Monitoring
The API includes basic monitoring and logging for production use.

The deployment should work within 2-3 minutes once Railway processes the build with the new configuration.