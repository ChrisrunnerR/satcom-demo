# Deployment Guide

This guide explains how to deploy the Satcom Audio Demo to Streamlit Cloud with OpenAI integration.

## Prerequisites

1. **OpenAI API Key**: Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Google Cloud Credentials** (for TTS): If using Google TTS, you'll need service account credentials
3. **GitHub Repository**: Your code should be in a GitHub repository

## Streamlit Cloud Deployment

### 1. Connect Your Repository

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository and branch
5. Set the main file path to `streamlit_app.py`

### 2. Configure Secrets

In your Streamlit Cloud app settings, add the following secrets:

```toml
[openai]
api_key = "your_openai_api_key_here"

[gcp]
credentials = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
}
'''
```

### 3. Deploy

Click "Deploy" and wait for the build to complete.

## Local Development

### 1. Environment Setup

Create a `.env` file in your project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
streamlit run streamlit_app.py
```

## Testing

Run the test script to verify OpenAI integration:

```bash
python test_openai.py
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: Ensure your API key is correctly set in Streamlit secrets
2. **Rate Limiting**: OpenAI has rate limits; if you hit them, wait and try again
3. **Model Availability**: Some models may not be available depending on your OpenAI plan

### Support

- Check OpenAI API status: [status.openai.com](https://status.openai.com)
- Streamlit Cloud docs: [docs.streamlit.io](https://docs.streamlit.io)
- OpenAI API docs: [platform.openai.com/docs](https://platform.openai.com/docs)
