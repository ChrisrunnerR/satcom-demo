# Satcom Audio Transmission Demo

A Streamlit application that demonstrates satellite communication audio transmission simulation with noise and packet loss effects.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory with the following variables:

```
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google Cloud Configuration (if needed for TTS)
GOOGLE_APPLICATION_CREDENTIALS=path_to_your_google_credentials.json
```

### 3. Run the Application
```bash
streamlit run streamlit_app.py
```

## Features

- Generate text using OpenAI (GPT-4o-mini) or input custom text
- Convert text to speech using Google TTS
- Simulate satellite communication transmission with configurable noise and packet loss
- Evaluate audio quality using STOI, PESQ, and WER metrics
