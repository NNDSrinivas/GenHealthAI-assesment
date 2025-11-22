# 🎯 **ONE PUBLIC URL FOR ASSESSMENT**

## ⚡ **DEPLOY NOW - GET YOUR URL IN 5 MINUTES**

### 🔗 **Single Public URL You'll Get:**
```
https://genhealth-assessment-api.onrender.com
```

### 📋 **Quick Deploy Steps:**
1. **Go to:** [render.com](https://render.com)
2. **Sign in** with GitHub
3. **New +** → **Web Service**
4. **Select:** `NNDSrinivas/GenHealthAI-assesment`
5. **Settings:**
   - **Name:** `genhealth-assessment-api`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn -w 2 -b 0.0.0.0:$PORT run:app`
   - **Plan:** Free
6. **Click:** Create Web Service

### ✅ **Assessment Team Can Test:**
```bash
# Health Check
curl https://genhealth-assessment-api.onrender.com/health

# Orders API (CRUD)
curl https://genhealth-assessment-api.onrender.com/api/orders

# Create Order
curl -X POST https://genhealth-assessment-api.onrender.com/api/orders \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"P001","order_type":"lab_test","description":"Blood work"}'

# Document Upload
curl -X POST https://genhealth-assessment-api.onrender.com/api/documents/upload \
  -F "file=@document.docx"

# Patient Data
curl https://genhealth-assessment-api.onrender.com/api/patients
```

### 🎯 **Result:**
**ONE URL** → **All Assessment Requirements** → **24/7 Access** → **Done!**

---

**⏰ Deploy now to get your public URL in 5 minutes!**