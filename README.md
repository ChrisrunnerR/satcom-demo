# Satcom Audio Transmission Demo

A Streamlit application that demonstrates satellite communication audio transmission simulation with noise and packet loss effects.

## Setup

### 1. Create and Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Edit the `.streamlit/secrets.toml` file and add your API keys:

**Required:**

- OpenAI API Key: Get from https://platform.openai.com/api-keys
- Google Cloud TTS credentials: Get from https://console.cloud.google.com/apis/credentials

The file structure:

```toml
[openai]
api_key = "your-openai-api-key-here"

[gcp]
credentials = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  ...
}
'''
```

### 4. Run the Application

```bash
streamlit run streamlit_app.py
```

**Note:** Make sure your virtual environment is activated before running the app!

## Features

- Generate text using OpenAI (GPT-4o-mini) or input custom text
- Convert text to speech using Google TTS
- Simulate satellite communication transmission with configurable:
  - **Noise**: Gaussian noise injection
  - **Packet Loss**: Random audio segment dropping
  - **Compression Artifacts**: Bandwidth limitation, quantization, harmonic distortion, and temporal smearing
- Evaluate audio quality using STOI, PESQ, and WER metrics
