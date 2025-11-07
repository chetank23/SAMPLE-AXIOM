# Render Deployment Guide - Environment Variables

This guide shows you which environment variables to configure in Render when deploying AgroLens.

## 📋 Required Environment Variables for Render

When deploying to Render, add these environment variables in your Render dashboard:

### 🔐 Required Variables

#### 1. `FLASK_SECRET_KEY` (Required)
- **Description**: Secret key for Flask session management and security
- **How to Generate**: 
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- **Example Value**: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6`
- **Important**: Generate a unique, secure key for production!

### 🔧 Optional Configuration Variables

#### 2. `OLLAMA_API_URL` (Optional)
- **Description**: URL for Ollama API endpoint
- **Default**: `http://localhost:11434`
- **For Render**: If using external Ollama service, set the full URL
- **Example**: `https://your-ollama-instance.com:11434`
- **Note**: If Ollama is running on Render, you may need to use the internal service URL

#### 3. `UPLOAD_FOLDER` (Optional)
- **Description**: Directory where uploaded images are stored
- **Default**: `uploads`
- **For Render**: Keep as `uploads` (Render handles file storage)

#### 4. `MAX_UPLOAD_SIZE` (Optional)
- **Description**: Maximum file upload size in bytes
- **Default**: `10485760` (10MB)
- **Example**: `10485760` for 10MB, `20971520` for 20MB

#### 5. `ALLOWED_EXTENSIONS` (Optional)
- **Description**: Comma-separated list of allowed file extensions
- **Default**: `png,jpg,jpeg`
- **Example**: `png,jpg,jpeg,gif`

#### 6. `FLASK_DEBUG` (Optional)
- **Description**: Enable/disable Flask debug mode
- **Default**: `True`
- **For Production**: Set to `False`
- **Values**: `True` or `False`

#### 7. `FLASK_HOST` (Optional)
- **Description**: Host address for Flask server
- **Default**: `0.0.0.0`
- **For Render**: Keep as `0.0.0.0` (Render handles this)

#### 8. `FLASK_PORT` (Optional)
- **Description**: Port number for Flask server
- **Default**: `5000`
- **For Render**: Use `$PORT` environment variable (Render provides this)
- **Important**: Render automatically sets `PORT` variable, so you may not need this

### 🌐 Optional API Keys (For Future Features)

#### 9. `OPEN_WEATHER_APIKEY` (Optional)
- **Description**: API key for OpenWeatherMap (for weather-based recommendations)
- **How to Get**: Sign up at https://openweathermap.org/api
- **Example**: `your-openweather-api-key-here`

#### 10. `HUGGINGFACE_LOGIN_TOKEN` (Optional)
- **Description**: API token for HuggingFace models
- **How to Get**: Create token at https://huggingface.co/settings/tokens
- **Example**: `hf_your-token-here`

---

## 🚀 How to Add Environment Variables in Render

### Step-by-Step Instructions:

1. **Go to Render Dashboard**
   - Navigate to your service/application

2. **Open Environment Tab**
   - Click on "Environment" in the left sidebar
   - Or go to Settings → Environment

3. **Add Environment Variables**
   - Click "Add Environment Variable"
   - Enter the variable name (e.g., `FLASK_SECRET_KEY`)
   - Enter the value
   - Click "Save Changes"

4. **Redeploy**
   - After adding variables, Render will automatically redeploy
   - Or manually trigger a redeploy

---

## 📝 Minimum Required Variables for Render

For a basic deployment, you **MUST** set at least:

```
FLASK_SECRET_KEY=<your-generated-secret-key>
FLASK_DEBUG=False
PORT=$PORT  (Render automatically provides this)
```

---

## 🔒 Security Best Practices

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Generate unique secret keys** - Don't use default values in production
3. **Use Render's environment variables** - Don't hardcode secrets in code
4. **Set `FLASK_DEBUG=False`** - Always disable debug mode in production
5. **Rotate secrets regularly** - Change secret keys periodically

---

## 🧪 Testing Your Environment Variables

After deployment, you can verify variables are loaded by:

1. Check Render logs for startup messages
2. Add a test endpoint in your app to verify (remove after testing):
   ```python
   @app.route('/env-test')
   def env_test():
       return jsonify({
           'secret_key_set': bool(os.getenv('FLASK_SECRET_KEY')),
           'debug_mode': os.getenv('FLASK_DEBUG', 'Not set')
       })
   ```

---

## 📋 Quick Copy-Paste List for Render

Copy these into Render's environment variables section:

```
FLASK_SECRET_KEY=<generate-using-python-command-above>
FLASK_DEBUG=False
OLLAMA_API_URL=http://localhost:11434
UPLOAD_FOLDER=uploads
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=png,jpg,jpeg
```

**Note**: Replace `<generate-using-python-command-above>` with your actual generated secret key!

---

## 🆘 Troubleshooting

### Issue: App crashes on startup
- **Solution**: Ensure `FLASK_SECRET_KEY` is set

### Issue: Can't connect to Ollama
- **Solution**: Check `OLLAMA_API_URL` is correct for your deployment

### Issue: File uploads fail
- **Solution**: Verify `UPLOAD_FOLDER` exists and has write permissions

### Issue: Port binding errors
- **Solution**: Use `$PORT` variable provided by Render, not hardcoded port

---

## 📚 Additional Resources

- [Render Environment Variables Documentation](https://render.com/docs/environment-variables)
- [Flask Configuration Best Practices](https://flask.palletsprojects.com/en/latest/config/)
- [Python Secrets Module](https://docs.python.org/3/library/secrets.html)

