# EatWise - Deployment Guide

## 🚀 Streamlit Cloud Deployment

Follow these steps to deploy EatWise to Streamlit Cloud:

### Step 1: Prepare Your Repository

✅ **Already Done:**
- GitHub repository created: `https://github.com/scmlewis/eatwise_ai`
- Code pushed to main branch
- `requirements.txt` includes all dependencies
- `.gitignore` configured to exclude sensitive files

### Step 2: Create Streamlit Cloud Account

1. Go to **https://share.streamlit.io/**
2. Click **Sign up** and authenticate with GitHub
3. Authorize Streamlit to access your GitHub repositories

### Step 3: Deploy the App

1. Click **"Create app"** on Streamlit Cloud dashboard
2. Select:
   - **Repository**: `scmlewis/eatwise_ai`
   - **Branch**: `main`
   - **Main file path**: `app.py`

3. Click **Deploy**

Streamlit will automatically deploy your app and provide a public URL like:
- `https://eatwise-ai.streamlit.app/`

### Step 4: Configure Secrets in Streamlit Cloud

⚠️ **IMPORTANT**: Your `.env` file is in `.gitignore`, so it won't be pushed to GitHub. You must set secrets in Streamlit Cloud:

1. In Streamlit Cloud dashboard, click your app
2. Click **"⋮"** → **Settings**
3. Click **Secrets** tab
4. Paste your secrets as TOML format:

```toml
# Supabase
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_anon_key"

# Azure OpenAI
AZURE_OPENAI_API_KEY = "your_azure_openai_key"
AZURE_OPENAI_ENDPOINT = "https://hkust.azure-api.net/"
AZURE_OPENAI_API_VERSION = "2023-05-15"
AZURE_OPENAI_DEPLOYMENT = "gpt-4o"
```

5. Click **Save**

### Step 5: Verify Deployment

1. Wait for Streamlit to finish deploying (usually 2-3 minutes)
2. Access your app at the provided URL
3. Login with your test account (scmlewis@gmail.com)
4. Test all features:
   - ✅ Login/Authentication
   - ✅ Dashboard loads
   - ✅ Log Meal (text and photo)
   - ✅ Analytics displays charts
   - ✅ Insights generate recommendations
   - ✅ Profile creation/update works

## 🔧 Troubleshooting Deployment

### App Shows "Forbidden" Error
- Check that secrets are properly configured in Streamlit Cloud
- Verify SUPABASE_KEY has correct permissions
- RLS should be disabled for development (already done)

### "ModuleNotFoundError" Errors
- Streamlit Cloud didn't install dependencies correctly
- Push a new commit (even empty):
  ```bash
  git commit --allow-empty -m "Trigger redeploy"
  git push
  ```

### App Loads But Features Don't Work
- Check Streamlit Cloud logs: **"⋮"** → **Manage app** → **Logs**
- Common issues:
  - Missing secrets
  - Supabase RLS policies blocking access
  - Azure OpenAI endpoint misconfiguration

### Slow App Load Time
- First load takes longer (cold start)
- Subsequent loads are faster
- Streamlit Cloud caches Python packages

## 📊 Monitoring Your Deployment

In Streamlit Cloud:
- **Logs**: Real-time error messages and prints
- **Settings**: Update secrets or source code settings
- **Activity**: View deployment history and analytics
- **Manage App**: Deploy new versions or restart

## 🆘 Support Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **GitHub Issues**: Use for bugs and feature requests

## 🔐 Security Notes

- **Never commit `.env` file** (it's in `.gitignore`)
- **Always use Streamlit Cloud Secrets** for sensitive data
- **Monitor your API usage** (OpenAI and Supabase)
- **Rotate API keys** periodically
- **Enable RLS in production** (currently disabled for dev)

## 💡 Tips for Production

1. **Enable Row Level Security (RLS)**
   - Currently disabled for easier testing
   - Enable in Supabase for production:
     ```sql
     ALTER TABLE users ENABLE ROW LEVEL SECURITY;
     ALTER TABLE meals ENABLE ROW LEVEL SECURITY;
     ALTER TABLE health_profiles ENABLE ROW LEVEL SECURITY;
     ALTER TABLE food_history ENABLE ROW LEVEL SECURITY;
     ```

2. **Set Up Custom Domain** (Optional)
   - Streamlit Cloud supports custom domains
   - Settings → Domain → Configure

3. **Monitor API Costs**
   - Check OpenAI usage: https://platform.openai.com/account/usage
   - Set up Supabase alerts: Supabase Dashboard → Settings → Billing

4. **Performance Optimization**
   - Use `@st.cache_data` for expensive operations
   - Already implemented for:
     - Database queries
     - User profile loading
     - Health profile fetching

## 📈 Post-Deployment Checklist

- [ ] App deployed and accessible
- [ ] All secrets configured in Streamlit Cloud
- [ ] Test login works
- [ ] Test meal logging (text and photo)
- [ ] Analytics charts display
- [ ] Insights page generates recommendations
- [ ] Profile creation/update works
- [ ] Check deployment logs for errors
- [ ] Share app URL with users

---

**Deployment Date**: November 18, 2025
**App Status**: Ready for Streamlit Cloud

For questions, check the main README.md or GitHub Issues.
