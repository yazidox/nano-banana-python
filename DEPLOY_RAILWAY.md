# 🚂 Deploy to Railway - Step by Step Guide

## Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)

## Step 1: Push to GitHub

1. Initialize git repository (if not already done):
```bash
git init
git add .
git commit -m "Initial commit - Glasses Overlay API"
```

2. Create a new repository on GitHub and push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/glasses-overlay-api.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Railway

### Method 1: Deploy from GitHub (Recommended)

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if not already connected
5. Select your `glasses-overlay-api` repository
6. Railway will automatically detect the Dockerfile and start deployment

### Method 2: Deploy via Railway CLI

1. Install Railway CLI:
```bash
# macOS
brew install railway

# or using npm
npm install -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Create new project and deploy:
```bash
railway init
railway up
```

## Step 3: Configure Environment Variables (Optional)

Although the API key is hardcoded, you can override it in Railway:

1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add these environment variables if you want to override defaults:

```
GEMINI_API_KEY=your-api-key-here
ALLOWED_ORIGINS=https://your-frontend.com,https://another-domain.com
PORT=8000
```

## Step 4: Get Your Public URL

1. In Railway dashboard, click on your service
2. Go to "Settings" tab
3. Under "Domains", click "Generate Domain"
4. You'll get a URL like: `glasses-overlay-api-production.up.railway.app`

Your API is now live! 🎉

## Step 5: Test Your Deployed API

Test with curl:
```bash
curl -X POST "https://YOUR-APP.up.railway.app/add-glasses" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg"}'
```

## Step 6: Update Your Frontend

Update the API URL in your frontend code:

```javascript
// Change from:
const API_URL = 'http://localhost:8000';

// To:
const API_URL = 'https://YOUR-APP.up.railway.app';
```

## 📝 Important Notes

1. **Free Tier Limits**: Railway's free tier includes:
   - $5 free credits per month
   - 500 hours of usage
   - Perfect for small projects

2. **API Key Security**: For production, consider:
   - Moving the API key to environment variables
   - Adding rate limiting
   - Implementing authentication

3. **Monitoring**: Railway provides:
   - Real-time logs
   - Metrics dashboard
   - Deployment history

## 🔧 Troubleshooting

### If deployment fails:
1. Check Railway logs for errors
2. Ensure all files are committed to GitHub
3. Verify Dockerfile syntax

### If API doesn't respond:
1. Check if domain is generated in Railway settings
2. Verify PORT environment variable (Railway sets this automatically)
3. Check application logs in Railway dashboard

## 🚀 Quick Deploy Button

Add this to your GitHub README for one-click deploy:

```markdown
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/YOUR_TEMPLATE_URL)
```

## 📊 Monitoring Your API

View logs:
```bash
railway logs
```

Check deployment status:
```bash
railway status
```

## 🔄 Updating Your Deployment

Railway auto-deploys when you push to GitHub:

```bash
git add .
git commit -m "Update API"
git push origin main
```

Railway will automatically rebuild and redeploy!

---

Your API is now production-ready and accessible from anywhere! 🌍
