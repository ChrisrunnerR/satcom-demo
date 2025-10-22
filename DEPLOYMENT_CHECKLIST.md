# 🚀 Deployment Checklist for Streamlit Cloud

## ✅ Pre-Deployment Checklist

### Local Files Ready
- [x] `streamlit_app.py` - Main application file
- [x] `requirements.txt` - Python dependencies
- [x] `packages.txt` - System packages (ffmpeg)
- [x] `.gitignore` - Properly configured
- [x] `README.md` - Project documentation
- [x] `utils/` folder - Helper functions
- [x] `.streamlit/config.toml` - Streamlit configuration

### Git Repository
- [ ] GitHub repository is connected to Streamlit Cloud
- [ ] All files are committed and pushed to GitHub
- [ ] Repository is accessible (public or Streamlit has access)

### API Keys & Credentials Required

#### 1. OpenAI API Key (REQUIRED)
- [ ] Have OpenAI account
- [ ] API key created at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- [ ] Key copied and saved securely
- [ ] Key format: `sk-proj-...` or `sk-...`

#### 2. Google Cloud TTS Credentials (REQUIRED)
- [ ] Google Cloud account created
- [ ] New project created in GCP
- [ ] Cloud Text-to-Speech API enabled
- [ ] Service account created
- [ ] JSON key downloaded
- [ ] JSON key contents copied

## 🔧 Deployment Steps

### Step 1: Go to Streamlit Cloud
1. [ ] Navigate to [share.streamlit.io](https://share.streamlit.io)
2. [ ] Sign in with GitHub (already done ✅)

### Step 2: Create New App
1. [ ] Click "New app" button
2. [ ] Fill in app details:
   - Repository: Select your `satcom-demo` repo
   - Branch: `main` (or your active branch)
   - Main file path: `streamlit_app.py`
   - App URL: Choose a custom URL (optional)

### Step 3: Configure Advanced Settings
1. [ ] Click "Advanced settings" before deploying
2. [ ] Python version: 3.11 (recommended) or 3.10
3. [ ] Configure secrets (see next step)

### Step 4: Add Secrets
1. [ ] Open the file `STREAMLIT_CLOUD_SECRETS.txt` in this project
2. [ ] Replace placeholders with your actual credentials:
   - `sk-proj-PASTE_YOUR_OPENAI_API_KEY_HERE` → Your OpenAI API key
   - Replace entire GCP JSON with your service account JSON
3. [ ] Copy the complete configured content
4. [ ] Paste into Streamlit Cloud "Secrets" text box
5. [ ] Verify formatting:
   - Triple quotes `'''` around GCP credentials
   - No syntax errors
   - All quotes and commas preserved

### Step 5: Deploy
1. [ ] Click "Deploy" button
2. [ ] Wait for build to complete (2-5 minutes)
3. [ ] Watch the deployment logs for any errors

### Step 6: Verify Deployment
1. [ ] App loads successfully
2. [ ] No error messages about API keys
3. [ ] Test each feature:
   - [ ] Custom text input works
   - [ ] OpenAI text generation works
   - [ ] Speech generation works (Google TTS)
   - [ ] Transmission simulation works
   - [ ] Audio evaluation works

## 🐛 Troubleshooting

### Common Issues

**Build fails with "Module not found"**
- Check that all dependencies are in `requirements.txt`
- Verify `packages.txt` has `ffmpeg`

**"OpenAI API key not found in Streamlit secrets"**
- Verify secrets format: `[openai]` section with `api_key = "..."`
- Check for typos in section name
- Ensure quotes around the key

**Google Cloud TTS errors**
- Verify Cloud Text-to-Speech API is enabled in GCP
- Check service account has correct permissions
- Ensure JSON is properly formatted with triple quotes
- Verify no trailing commas in JSON

**App is very slow**
- First load: Downloads Whisper model (~140MB) - normal
- Check deployment logs for issues
- Consider using smaller Whisper model ("tiny" or "small")

**Rate limiting errors**
- OpenAI: Check your API usage limits
- Google TTS: Free tier is 0-1M characters/month

## 📊 Post-Deployment

### Monitor Your App
- [ ] Check app analytics in Streamlit Cloud dashboard
- [ ] Monitor API usage in OpenAI dashboard
- [ ] Monitor API usage in Google Cloud console

### Share Your App
- [ ] App URL: `https://[your-app-name].streamlit.app`
- [ ] Test from different devices
- [ ] Share with team/users

### Maintenance
- [ ] Set up billing alerts (OpenAI & GCP)
- [ ] Regular updates: Push to GitHub auto-deploys
- [ ] Monitor error logs in Streamlit Cloud

## 💰 Cost Estimates

**Free Tier Limits:**
- Streamlit Cloud: 1 free public app
- OpenAI: Pay-as-you-go (~$0.0001-0.002 per text generation)
- Google TTS: 0-1M characters free/month (~4M words)

**Expected Monthly Cost (Light Usage):**
- ~$0-5 for OpenAI (100-1000 generations)
- ~$0-10 for Google TTS (if over free tier)
- $0 for Streamlit Cloud (free tier)

## 📝 Next Steps After Deployment

1. **Test thoroughly** - Try all features with various inputs
2. **Set billing alerts** - Prevent unexpected charges
3. **Document usage** - Add instructions for your users
4. **Monitor performance** - Check logs regularly
5. **Plan scaling** - Upgrade Streamlit plan if needed

## 🆘 Need Help?

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **OpenAI Docs**: [platform.openai.com/docs](https://platform.openai.com/docs)
- **Google Cloud TTS**: [cloud.google.com/text-to-speech/docs](https://cloud.google.com/text-to-speech/docs)
- **Community**: [discuss.streamlit.io](https://discuss.streamlit.io)

---

**Ready to deploy?** Follow the checklist above step-by-step! 🚀

