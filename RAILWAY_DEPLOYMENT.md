# Backend Deployment to Railway

## Prerequisites
- [Railway.app](https://railway.app) account
- GitHub repository (recommended for automatic deploys)
- Environment variables set up

## Steps to Deploy to Railway

### 1. Connect Railway to GitHub
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway and select your repository

### 2. Configure Environment Variables
In Railway dashboard, go to **Variables** and add:

```
OPENROUTER_API_KEYS=sk-xxx,sk-yyy
GROQ_KEYS=gsk-xxx,gsk-yyy
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
GROQ_API_BASE_URL=https://api.groq.com/openai/v1
```

### 3. Set Build Command
Railway will auto-detect Python and install `backend/requirements.txt`

### 4. Get Your Backend URL
Once deployed, Railway will assign a URL like:
```
https://your-project-backend.up.railway.app
```

### 5. Update Frontend Configuration
Update `frontend/.env.local`:
```
VITE_BACKEND_URL=https://your-project-backend.up.railway.app
```

Or update `frontend/vite.config.js` directly:
```javascript
const backendUrl = 'https://your-project-backend.up.railway.app';
```

## Local Development
For local development, the backend defaults to `localhost:8000`:

```bash
# Terminal 1: Start backend
cd d:\AmplifyWebsite
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

## Files for Railway Deployment
- `Procfile` - Tells Railway how to start the app
- `runtime.txt` - Specifies Python version
- `railway.json` - Railway configuration
- `backend/requirements.txt` - Python dependencies (auto-installed)

## Notes
- The backend requires valid API keys for GROQ and/or OpenRouter
- Railway's free tier includes monthly compute hours
- Logs available in Railway dashboard
