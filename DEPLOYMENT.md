# GenHealthAI - Secure Deployment Guide

## 🔐 Environment Variables & Secrets

### For Cloud Deployment (Railway/Render/Heroku)

**Required Environment Variables:**

```bash
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-production-secret-key-here
PORT=$PORT  # Automatically provided by cloud platforms
```

**Optional Environment Variables:**

```bash
MONGODB_URI=your-mongodb-connection-string
MONGODB_DB_NAME=clinical_docs
LOG_LEVEL=INFO
MAX_CONTENT_LENGTH=16777216
```

## 🚀 Railway Deployment

1. Go to [railway.app](https://railway.app)
2. Connect your GitHub account
3. Click "Deploy from GitHub repo"
4. Select `NNDSrinivas/GenHealthAI`
5. Add environment variables in Railway dashboard:
   - `SECRET_KEY`: Generate a secure secret key
   - `FLASK_ENV`: `production`
   - `FLASK_DEBUG`: `False`

## 🌐 Render Deployment

1. Go to [render.com](https://render.com)
2. Create new "Web Service"
3. Connect GitHub repository
4. Set environment variables in Render dashboard

## ⚡ Heroku Deployment

1. Install Heroku CLI
2. `heroku create genhealth-ai-api`
3. Set config vars: `heroku config:set SECRET_KEY=your-secret-key`
4. `git push heroku main`

## 🔒 Security Best Practices

✅ **Never commit .env files**
✅ **Use platform-specific environment variables**
✅ **Generate strong SECRET_KEY for production**
✅ **Set FLASK_DEBUG=False in production**
✅ **Use HTTPS URLs only**

## 📋 API Endpoints

Once deployed, your API will be available at:
- `GET /health` - Health check
- `POST /api/orders` - Create order
- `GET /api/orders` - List orders
- `POST /api/documents/upload` - Upload document with OCR