# 🚀 Quick Deployment Steps

## Your Repository
📍 **GitHub URL**: `https://github.com/scmlewis/eatwise_ai`
✅ **Status**: Code pushed to `main` branch

## Deploy to Streamlit Cloud (5 minutes)

### 1. Create Streamlit Account
- Visit: https://share.streamlit.io/
- Click "Sign up" → Authenticate with GitHub
- Authorize Streamlit to access your repos

### 2. Deploy Your App
- Click "Create app"
- Select:
  - Repository: `scmlewis/eatwise_ai`
  - Branch: `main`
  - File: `app.py`
- Click "Deploy" and wait 2-3 minutes

### 3. Add Your Secrets
- Go to app Settings → Secrets
- Paste this (replace with YOUR credentials):

```toml
SUPABASE_URL = "https://fmyiyajfmmfhjmuytzex.supabase.co"
SUPABASE_KEY = "your_actual_key_here"
AZURE_OPENAI_API_KEY = "your_actual_key_here"
AZURE_OPENAI_ENDPOINT = "https://hkust.azure-api.net/"
AZURE_OPENAI_API_VERSION = "2023-05-15"
AZURE_OPENAI_DEPLOYMENT = "gpt-4o"
```

### 4. Test Your App
- Your app will be live at: https://eatwise-ai.streamlit.app/ (or custom URL)
- Login and test all features

## 📋 Files Included
✅ `app.py` - Main Streamlit app
✅ `requirements.txt` - All Python dependencies
✅ `.gitignore` - Excludes sensitive files
✅ `.streamlit/config.toml` - Streamlit configuration
✅ `DEPLOYMENT.md` - Full deployment guide
✅ Complete code for all modules

## 🔐 Important Notes
⚠️ **Never commit `.env` file** (it's protected by .gitignore)
✅ **Use Streamlit Cloud Secrets** instead
✅ **All code is safely on GitHub**
✅ **Production ready** (just needs secrets)

## Helpful Links
- Streamlit Cloud: https://share.streamlit.io/
- Streamlit Docs: https://docs.streamlit.io/
- Supabase Dashboard: https://supabase.com/dashboard

---
**Ready to deploy!** 🎉
