# 🚀 Render Deployment - Quick Start Guide

## 📋 Environment Variables to Add in Render

### Step 1: Generate Secret Key

Run this command in your terminal:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (it will be a long string of random characters).

### Step 2: Add These Variables in Render Dashboard

Go to your Render service → **Environment** tab → **Add Environment Variable**

#### ✅ Required (Minimum):

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `FLASK_SECRET_KEY` | `<paste-generated-key>` | **Required** - Use the key you generated above |
| `FLASK_DEBUG` | `False` | **Required** - Set to False for production |

#### 🔧 Optional (Recommended):

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `OLLAMA_API_URL` | `http://localhost:11434` | Change if using external Ollama |
| `UPLOAD_FOLDER` | `uploads` | Default upload directory |
| `MAX_UPLOAD_SIZE` | `10485760` | 10MB in bytes |
| `ALLOWED_EXTENSIONS` | `png,jpg,jpeg` | Comma-separated list |

#### 📝 Note:
- `PORT` variable is **automatically provided by Render** - you don't need to set it
- The app will automatically use Render's `PORT` variable

---

## 🎯 Quick Copy-Paste for Render

### Minimum Setup (Required):
```
FLASK_SECRET_KEY=<your-generated-secret-key>
FLASK_DEBUG=False
```

### Full Setup (Recommended):
```
FLASK_SECRET_KEY=<your-generated-secret-key>
FLASK_DEBUG=False
OLLAMA_API_URL=http://localhost:11434
UPLOAD_FOLDER=uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=png,jpg,jpeg
```

---

## 📝 Step-by-Step Instructions

1. **Generate Secret Key**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Go to Render Dashboard**
   - Navigate to your service
   - Click **Environment** in the sidebar

3. **Add Variables**
   - Click **Add Environment Variable**
   - Enter variable name and value
   - Click **Save Changes**

4. **Deploy**
   - Render will automatically redeploy
   - Check logs to verify deployment

---

## ⚠️ Important Notes

- ✅ **Always set `FLASK_DEBUG=False`** in production
- ✅ **Generate a unique secret key** - don't use the default
- ✅ **Never commit `.env` file** to git (already in `.gitignore`)
- ✅ **Use Render's `PORT` variable** - don't hardcode port numbers

---

## 🔍 Verify Deployment

After deployment, check:
1. ✅ App starts without errors
2. ✅ Environment variables are loaded (check logs)
3. ✅ Ollama connection works (if using Ollama)
4. ✅ File uploads work correctly

---

## 🆘 Troubleshooting

**Issue**: App crashes on startup
- **Solution**: Ensure `FLASK_SECRET_KEY` is set

**Issue**: Port binding error
- **Solution**: App now uses Render's `PORT` variable automatically

**Issue**: Can't connect to Ollama
- **Solution**: Check `OLLAMA_API_URL` is correct

---

## 📚 More Information

See `RENDER_DEPLOYMENT.md` for detailed documentation.

