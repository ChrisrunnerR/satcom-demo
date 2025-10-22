# FastAPI Backend for Satcom Audio Demo
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import io
import os
from datetime import datetime
from google.cloud import texttospeech
from google.oauth2 import service_account
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from utils import generate_text, simulate_transmission, evaluate_audio

# Initialize FastAPI app
app = FastAPI(
    title="Satcom Audio Transmission API",
    description="API for satellite communication audio transmission simulation",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load credentials
try:
    # For production - load from environment variable
    gcp_creds_json = os.getenv("GCP_CREDENTIALS")
    if gcp_creds_json:
        gcp_credentials = service_account.Credentials.from_service_account_info(
            json.loads(gcp_creds_json)
        )
        tts_client = texttospeech.TextToSpeechClient(credentials=gcp_credentials)
    else:
        # Fallback to default credentials
        tts_client = texttospeech.TextToSpeechClient()
except Exception as e:
    print(f"Warning: Could not initialize TTS client: {e}")
    tts_client = None

# Pydantic models for request/response validation
class TextGenerationRequest(BaseModel):
    minutes: int = 0
    seconds: int = 10
    model: str = "gpt-4o-mini"

class TextGenerationResponse(BaseModel):
    text: str
    word_count: int
    estimated_duration: float

class TransmissionRequest(BaseModel):
    noise_level: float = 0.1
    packet_loss: int = 10
    compression_level: float = 0.5

class EvaluationResponse(BaseModel):
    stoi: float
    passed: bool
    threshold: float = 0.5

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Satcom Audio Transmission API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "generate_text": "/api/generate-text",
            "generate_speech": "/api/generate-speech",
            "simulate_transmission": "/api/simulate-transmission",
            "evaluate_audio": "/api/evaluate-audio"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 1. Generate Text Endpoint
@app.post("/api/generate-text", response_model=TextGenerationResponse)
async def api_generate_text(request: TextGenerationRequest):
    """
    Generate realistic radio transmission text using OpenAI
    """
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        text = generate_text(
            minutes=request.minutes,
            seconds=request.seconds,
            api_key=openai_api_key,
            model=request.model
        )
        
        word_count = len(text.split())
        estimated_duration = (word_count / 120) * 60  # 120 words per minute
        
        return TextGenerationResponse(
            text=text,
            word_count=word_count,
            estimated_duration=estimated_duration
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

# 2. Generate Speech Endpoint
@app.post("/api/generate-speech")
async def api_generate_speech(text: str = Form(...)):
    """
    Convert text to speech using Google Cloud TTS
    Returns audio file as WAV
    """
    try:
        if not tts_client:
            raise HTTPException(status_code=500, detail="TTS client not initialized")
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Chirp3-HD-Algenib"
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=0.90
        )
        
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Return audio as streaming response
        audio_stream = io.BytesIO(response.audio_content)
        audio_stream.seek(0)
        
        return StreamingResponse(
            audio_stream,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=tts_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech generation failed: {str(e)}")

# 3. Simulate Transmission Endpoint
@app.post("/api/simulate-transmission")
async def api_simulate_transmission(
    audio_file: UploadFile = File(...),
    noise_level: float = Form(0.1),
    packet_loss: int = Form(10),
    compression_level: float = Form(0.5)
):
    """
    Simulate satcom transmission effects on audio
    Returns degraded audio file as WAV
    """
    try:
        # Read uploaded audio file
        audio_bytes = await audio_file.read()
        
        # Simulate transmission
        transmitted_audio_bytes = simulate_transmission(
            audio_bytes,
            noise_level=noise_level,
            packet_loss=packet_loss,
            compression_level=compression_level
        )
        
        # Return transmitted audio
        audio_stream = io.BytesIO(transmitted_audio_bytes)
        audio_stream.seek(0)
        
        return StreamingResponse(
            audio_stream,
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=transmitted_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transmission simulation failed: {str(e)}")

# 4. Evaluate Audio Endpoint
@app.post("/api/evaluate-audio", response_model=EvaluationResponse)
async def api_evaluate_audio(
    original_audio: UploadFile = File(...),
    transmitted_audio: UploadFile = File(...)
):
    """
    Evaluate audio quality metrics (STOI)
    """
    try:
        # Read uploaded files
        original_bytes = await original_audio.read()
        transmitted_bytes = await transmitted_audio.read()
        
        # Evaluate
        scores = evaluate_audio(original_bytes, transmitted_bytes)
        
        if "error" in scores:
            raise HTTPException(status_code=500, detail=scores["error"])
        
        stoi_score = scores.get("stoi", 0.0)
        threshold = 0.5
        
        return EvaluationResponse(
            stoi=stoi_score,
            passed=stoi_score >= threshold,
            threshold=threshold
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio evaluation failed: {str(e)}")

# Combined endpoint for full pipeline
@app.post("/api/full-pipeline")
async def api_full_pipeline(
    text: str = Form(...),
    noise_level: float = Form(0.1),
    packet_loss: int = Form(10),
    compression_level: float = Form(0.5)
):
    """
    Complete pipeline: Text → Speech → Transmission → Evaluation
    Returns all results in one response
    """
    try:
        # Step 1: Generate Speech
        if not tts_client:
            raise HTTPException(status_code=500, detail="TTS client not initialized")
        
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Chirp3-HD-Algenib"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=0.90
        )
        
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        original_audio_bytes = response.audio_content
        
        # Step 2: Simulate Transmission
        transmitted_audio_bytes = simulate_transmission(
            original_audio_bytes,
            noise_level=noise_level,
            packet_loss=packet_loss,
            compression_level=compression_level
        )
        
        # Step 3: Evaluate
        scores = evaluate_audio(original_audio_bytes, transmitted_audio_bytes)
        
        if "error" in scores:
            raise HTTPException(status_code=500, detail=scores["error"])
        
        stoi_score = scores.get("stoi", 0.0)
        threshold = 0.5
        
        return JSONResponse({
            "success": True,
            "text": text,
            "transmission_params": {
                "noise_level": noise_level,
                "packet_loss": packet_loss,
                "compression_level": compression_level
            },
            "evaluation": {
                "stoi": stoi_score,
                "passed": stoi_score >= threshold,
                "threshold": threshold
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

