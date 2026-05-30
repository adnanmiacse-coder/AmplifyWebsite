# Railway Backend Deployment Checklist

## Before Deploying to Railway

- [ ] Backend runs locally: `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
- [ ] Backend responds to health check: `curl http://localhost:8000/api/config`
- [ ] `Procfile` exists and is correct
- [ ] `runtime.txt` specifies Python version
- [ ] `nixpacks.toml` is configured
- [ ] `backend/requirements.txt` is up to date
- [ ] `.railwayignore` prevents PHP detection
- [ ] All changes committed to Git

## Deploying

1. **Create new Railway project** (Python, not Laravel)
2. **Connect to GitHub** and select your repo
3. **Delete Laravel service** if auto-detected
4. **Add environment variables**:
   - OPENROUTER_API_KEYS
   - GROQ_KEYS
5. **Wait for build to complete** (watch logs)
6. **Copy Railway URL** from deployment

## After Deployment

- [ ] Check Railway logs for errors
- [ ] Test: `curl https://your-railway-backend/api/config`
- [ ] Update frontend with new backend URL
- [ ] Test frontend → backend communication
- [ ] Check for CORS errors in browser console

## Common Issues

| Issue | Fix |
|-------|-----|
| "Stopping Container" immediately | Laravel service still enabled - delete it |
| Port binding error | Should auto-work with `${PORT:-8000}` |
| API keys error | Add to Railway Variables, redeploy |
| 502 Bad Gateway | Check Railway logs for startup errors |
| CORS errors | Make sure frontend proxy routes are correct |
