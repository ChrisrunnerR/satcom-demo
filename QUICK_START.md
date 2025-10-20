# Quick Start: Deploy to Streamlit Cloud

## 🚀 Step-by-Step Deployment Guide

### Step 1: Get Your API Keys

#### OpenAI API Key (Required)
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)
5. Save it somewhere safe - you won't see it again!

#### Google Cloud TTS Credentials (Required for Text-to-Speech)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable the Cloud Text-to-Speech API
4. Create a service account:
   - Go to IAM & Admin → Service Accounts
   - Click "Create Service Account"
   - Name it "satcom-tts"
   - Grant role: "Cloud Text-to-Speech User"
5. Create a JSON key:
   - Click on your new service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key" → "JSON"
   - Download the JSON file
6. Open the JSON file - you'll need its contents for Streamlit secrets

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account (already done ✅)

2. **Create New App**
   - Click "New app" button
   - Select your repository: `satcom-demo`
   - Select branch: `main` (or your current branch)
   - Main file path: `streamlit_app.py`
   - Click "Advanced settings" before deploying

3. **Configure Secrets**
   - In the "Secrets" section, paste the following format:
   
   ```toml
   [openai]
   api_key = "YOUR_OPENAI_API_KEY_HERE"
   
   [gcp]
   credentials = '''
   {
     "type": "service_account",
     "project_id": "your-project-id",
     "private_key_id": "your-key-id",
     "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_KEY\n-----END PRIVATE KEY-----\n",
     "client_email": "your-sa@your-project.iam.gserviceaccount.com",
     "client_id": "123456789",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
   }
   '''
   ```
   
   - Replace `YOUR_OPENAI_API_KEY_HERE` with your actual OpenAI API key
   - Replace the entire JSON object in `credentials` with your Google Cloud JSON key contents
   - **Important**: Keep the triple quotes `'''` around the JSON

4. **Deploy!**
   - Click "Deploy" button
   - Wait 2-5 minutes for the build to complete
   - Your app will be live at: `https://[your-app-name].streamlit.app`

### Step 3: Test Your Deployment

Once deployed, test these features:
1. ✏️ **Custom Text** - Enter text and generate speech
2. 🤖 **OpenAI Generation** - Generate radio transmission text
3. 🔊 **Speech Generation** - Convert text to audio
4. 📡 **Transmission** - Simulate satcom degradation
5. 📈 **Evaluation** - Check audio quality metrics

### Troubleshooting

**Error: "OpenAI API key not found"**
- Check that your secret is named exactly `[openai]` with `api_key = "..."`
- Make sure there are no extra spaces or quotes

**Error: "Google Cloud credentials error"**
- Verify the JSON is properly formatted
- Ensure the triple quotes `'''` are present
- Check that you enabled the Text-to-Speech API in Google Cloud

**Error: "Module not found"**
- Streamlit Cloud should auto-install from `requirements.txt`
- If issues persist, check the deployment logs

**App is slow to load**
- First load downloads Whisper model (~140MB) - this is normal
- Subsequent loads will be faster

### 💰 Cost Estimate

- **Streamlit Cloud**: Free tier available (1 app, public)
- **OpenAI API**: ~$0.0001-0.002 per request (very cheap for testing)
- **Google Cloud TTS**: Free tier: 0-1M characters/month

### 🎉 You're Live!

Once deployed, you can:
- Share the URL with anyone
- Use it from any device
- Update by pushing to GitHub (auto-deploys)

Need help? Check the full [DEPLOYMENT.md](DEPLOYMENT.md) guide.

