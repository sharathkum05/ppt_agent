# 🚀 Deployment Guide

Complete guide for deploying PPT Agent to Vercel.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally
   ```bash
   npm install -g vercel
   ```
3. **GitHub Repository**: Code should be pushed to GitHub
4. **Environment Variables**: Collect all required API keys and credentials

## 🔧 Backend Deployment (FastAPI)

### Step 1: Prepare Backend

1. **Ensure all dependencies are in requirements.txt:**
   ```bash
   pip freeze > requirements.txt
   # Or use the provided requirements.txt
   ```

2. **Verify vercel.json exists** in the root directory (already created)

3. **Update main.py** - Mangum handler should be added (already done)

### Step 2: Deploy to Vercel

1. **Login to Vercel:**
   ```bash
   vercel login
   ```

2. **Initialize Vercel project (first time only):**
   ```bash
   cd /path/to/ppt_agent
   vercel
   ```
   Follow the prompts to link your project.

3. **Deploy to production:**
   ```bash
   vercel --prod
   ```

### Step 3: Configure Environment Variables

1. **Go to Vercel Dashboard:**
   - Navigate to your project
   - Go to Settings → Environment Variables

2. **Add the following variables:**

   | Variable | Value | Environment |
   |----------|-------|-------------|
   | `ANTHROPIC_API_KEY` | Your Anthropic API key | Production, Preview, Development |
   | `GOOGLE_CREDENTIALS_PATH` | Path to credentials (or base64 encoded JSON) | Production, Preview |
   | `DEFAULT_PRESENTATION_ID` | Your Google Slides presentation ID | Production, Preview |
   | `GOOGLE_DRIVE_FOLDER_ID` | Your Google Drive folder ID | Production, Preview |
   | `FRONTEND_URL` | Your frontend URL (for CORS) | Production, Preview |
   | `AGENT_MODEL` | `claude-3-haiku-20240307` | Production, Preview |
   | `AGENT_MAX_ITERATIONS` | `20` | Production, Preview |

3. **For Google Credentials on Vercel:**
   
   Option A: Base64 encode your JSON file:
   ```bash
   cat credentials/service_account.json | base64
   ```
   Store the output as `GOOGLE_CREDENTIALS_JSON` (base64) and decode in code.
   
   Option B: Use environment variable for each credential field (more secure)

### Step 4: Verify Deployment

1. **Check deployment status** in Vercel dashboard
2. **Test health endpoint:**
   ```bash
   curl https://your-project.vercel.app/health
   ```
3. **Test API documentation:**
   Visit `https://your-project.vercel.app/docs`

## 🎨 Frontend Deployment (React)

### Step 1: Prepare Frontend

1. **Navigate to frontend directory:**
   ```bash
   cd ppt-agent-frontend
   ```

2. **Create production environment file:**
   ```bash
   # Create .env.production
   echo "VITE_API_URL=https://your-backend.vercel.app" > .env.production
   ```

3. **Verify vercel.json exists** (already created)

### Step 2: Deploy to Vercel

1. **From frontend directory:**
   ```bash
   vercel
   ```

2. **For production:**
   ```bash
   vercel --prod
   ```

### Step 3: Configure Frontend Environment Variables

In Vercel Dashboard → Frontend Project → Environment Variables:

| Variable | Value | Environment |
|----------|-------|-------------|
| `VITE_API_URL` | `https://your-backend.vercel.app` | Production, Preview |

### Step 4: Update Backend CORS

After frontend is deployed, update backend CORS settings:

1. **Go to Backend Vercel Project → Environment Variables**
2. **Update `FRONTEND_URL`** to your frontend URL:
   ```
   FRONTEND_URL=https://your-frontend.vercel.app
   ```
3. **Redeploy backend** if needed:
   ```bash
   vercel --prod
   ```

## 🔄 Continuous Deployment

### GitHub Integration

1. **Connect GitHub repository** in Vercel dashboard
2. **Configure auto-deployment:**
   - Production: Deploy from `main` branch
   - Preview: Deploy from all other branches

### Manual Deployment

For manual deployments:
```bash
# Backend
cd /path/to/ppt_agent
vercel --prod

# Frontend
cd ppt-agent-frontend
vercel --prod
```

## 🧪 Testing Deployed Services

### Test Backend

```bash
# Health check
curl https://your-backend.vercel.app/health

# Test API endpoint
curl -X POST https://your-backend.vercel.app/generate-presentation \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a 3-slide presentation about AI"}'
```

### Test Frontend

1. Visit your frontend URL
2. Test the presentation generation flow
3. Verify API calls are working

## 🐛 Troubleshooting

### Backend Issues

**Issue: Module not found errors**
- Ensure all dependencies are in `requirements.txt`
- Check Python version in Vercel settings (should be 3.10+)

**Issue: Environment variables not working**
- Verify variables are set in Vercel dashboard
- Check variable names match exactly (case-sensitive)
- Redeploy after adding new variables

**Issue: Google API errors**
- Verify service account credentials are correct
- Check that presentation ID and folder are shared with service account
- Ensure APIs are enabled in Google Cloud Console

### Frontend Issues

**Issue: API calls failing (CORS)**
- Update `FRONTEND_URL` in backend environment variables
- Check CORS configuration in `main.py`
- Verify API URL is correct in frontend `.env.production`

**Issue: Build failures**
- Check Node.js version (should be 18+)
- Verify all dependencies are installed
- Check build logs in Vercel dashboard

## 📊 Monitoring

### Vercel Analytics

1. **Enable Analytics** in Vercel dashboard
2. **Monitor deployments** and function logs
3. **Check error rates** and performance

### Logs

View logs in Vercel dashboard:
- Go to Deployments → Click on deployment → View Function Logs

## 🔐 Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Use different credentials** for production and development
3. **Rotate API keys** regularly
4. **Enable Vercel Security Headers** (already configured in frontend vercel.json)
5. **Use HTTPS only** (Vercel provides this by default)

## 🌐 Custom Domain (Optional)

1. **Add domain** in Vercel dashboard
2. **Configure DNS** records as instructed
3. **SSL certificate** will be auto-provisioned

## 📝 Post-Deployment Checklist

- [ ] Backend health check passing
- [ ] API documentation accessible
- [ ] Frontend loads correctly
- [ ] Presentation generation working
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Error handling verified
- [ ] Logs accessible
- [ ] Monitoring enabled

## 🆘 Support

If you encounter deployment issues:

1. Check Vercel deployment logs
2. Verify environment variables
3. Test locally first
4. Open an issue on GitHub with deployment logs

---

Happy Deploying! 🚀

