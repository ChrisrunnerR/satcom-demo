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

# =============================================================================
# TWILIO VOICE INTEGRATION - Ground Station VOIP Calls
# =============================================================================

try:
    from utils.twilio_handler import twilio_handler
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("Warning: Twilio integration not available")

# Pydantic models for Twilio endpoints
class MakeCallRequest(BaseModel):
    to_number: str
    callback_url: Optional[str] = None

class SendTextRequest(BaseModel):
    call_sid: Optional[str] = None
    text: str
    voice: str = "Polly.Joanna"

class SendAudioRequest(BaseModel):
    call_sid: Optional[str] = None
    audio_url: str = "http://com.twilio.sounds.music.s3.amazonaws.com/ClockworkWaltz.mp3"

# Twilio Voice Endpoints
@app.post("/api/call/make")
async def make_outgoing_call(request: MakeCallRequest):
    """
    Make outgoing call to Air Side (Satellite)
    
    Example:
    ```json
    {
        "to_number": "+19788384309",
        "callback_url": "https://satcom-project-eqqi5.ondigitalocean.app"
    }
    ```
    
    This will call from Ground Control (+1-415-299-7283) to Satellite (+1-978-838-4309)
    """
    if not TWILIO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Twilio integration not configured")
    
    # Use app URL as callback if not provided
    callback_url = request.callback_url or str(os.getenv("APP_URL", "http://localhost:8000"))
    
    result = twilio_handler.make_call(request.to_number, callback_url)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@app.post("/api/call/answer")
async def answer_incoming_call(
    CallSid: str = Form("CA1234567890abcdef1234567890abcdef"),
    From: str = Form("+14152997283"),
    To: str = Form("+19788384309")
):
    """
    Webhook endpoint - Called by Twilio when incoming call received
    Returns TwiML to control call behavior
    
    ⚠️ NOTE: This is automatically called by Twilio when someone calls +1-978-838-4309
    You don't need to call this manually - it's already working!
    
    When you called +1-978-838-4309 and heard "Ground station connected" - THIS endpoint handled it!
    
    Default values shown are examples for testing only.
    
    Example call flow:
    1. Someone dials +1-978-838-4309
    2. Twilio automatically POSTs here with:
       - CallSid: Unique call identifier (auto-generated)
       - From: Caller's phone number (e.g., +14152997283)
       - To: Your Twilio number (+19788384309)
    3. This endpoint returns TwiML telling Twilio what to say/do
    """
    if not TWILIO_AVAILABLE:
        return "<Response><Say>Service unavailable</Say><Hangup/></Response>"
    
    request_data = {
        "CallSid": CallSid,
        "From": From,
        "To": To
    }
    
    twiml = twilio_handler.answer_incoming_call(request_data)
    
    return StreamingResponse(
        io.BytesIO(twiml.encode()),
        media_type="application/xml"
    )

@app.post("/api/call/play-audio")
async def play_audio_callback():
    """
    Callback endpoint for playing audio during active call
    Returns TwiML to play audio file
    """
    if not TWILIO_AVAILABLE:
        return StreamingResponse(
            io.BytesIO(b'<Response><Say>Service unavailable</Say><Hangup/></Response>'),
            media_type="application/xml"
        )
    
    # Get the pending audio URL from the handler
    audio_url = twilio_handler.pending_audio_url or "https://demo.twilio.com/welcome/audio"
    
    # Generate TwiML to play audio and keep call alive
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>{audio_url}</Play>
    <Pause length="60"/>
</Response>'''
    
    return StreamingResponse(
        io.BytesIO(twiml.encode()),
        media_type="application/xml"
    )

@app.post("/api/call/send-audio")
async def send_audio_during_call(request: SendAudioRequest):
    """
    Play audio file during an active call
    
    ⚠️ REQUIREMENTS:
    - Must have an active call in progress
    - Audio file must be publicly accessible (HTTPS URL)
    - Supported formats: MP3, WAV
    
    Default audio URL plays Twilio's demo welcome message.
    
    Example - Use default audio:
    ```json
    {}
    ```
    
    Example - Custom audio:
    ```json
    {
        "audio_url": "https://your-server.com/audio/transmission.mp3"
    }
    ```
    
    Example - With specific call:
    ```json
    {
        "call_sid": "CA17e4ba4400a0df3dc14888fa9b007896",
        "audio_url": "https://demo.twilio.com/welcome/audio"
    }
    ```
    
    Args:
        audio_url: Publicly accessible URL of audio file (default: Twilio demo)
        call_sid: Optional - uses active call if not specified
    """
    if not TWILIO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Twilio integration not configured")
    
    call_sid = request.call_sid or twilio_handler.active_call_sid
    
    if not call_sid:
        raise HTTPException(status_code=400, detail="No active call")
    
    result = twilio_handler.send_audio_to_call(call_sid, request.audio_url)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@app.post("/api/call/send-text")
async def send_text_during_call(request: SendTextRequest):
    """
    Send text as speech to active call using Twilio TTS
    
    Note: call_sid is automatically used from the most recent active call if not provided
    
    Example:
    ```json
    {
        "text": "Ground Control to Satellite, do you copy?",
        "voice": "Polly.Matthew"
    }
    ```
    
    Or with specific call:
    ```json
    {
        "call_sid": "CA17e4ba4400a0df3dc14888fa9b007896",
        "text": "Mission accomplished, returning to base"
    }
    ```
    
    Args:
        text: Text to speak
        voice: Twilio voice (default: Polly.Matthew)
        call_sid: Optional - uses active call if not specified
    """
    if not TWILIO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Twilio integration not configured")
    
    call_sid = request.call_sid or twilio_handler.active_call_sid
    
    if not call_sid:
        raise HTTPException(status_code=400, detail="No active call")
    
    result = twilio_handler.send_text_to_call(call_sid, request.text, request.voice)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@app.post("/api/call/hangup")
async def hangup_call(call_sid: Optional[str] = None):
    """
    End active call (terminates immediately)
    
    Note: If no call_sid provided, hangs up the most recent active call
    
    Example - Hang up active call:
    ```json
    {}
    ```
    
    Example - Hang up specific call:
    ```json
    {
        "call_sid": "CA17e4ba4400a0df3dc14888fa9b007896"
    }
    ```
    
    Args:
        call_sid: Optional - uses active call if not specified
    """
    if not TWILIO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Twilio integration not configured")
    
    result = twilio_handler.hangup_call(call_sid)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result

@app.get("/api/call/status")
async def get_call_status(call_sid: Optional[str] = None):
    """
    Get status of current or specific call
    
    Args:
        call_sid: Optional - uses active call if not specified
    
    Returns call status, duration, participants, etc.
    """
    if not TWILIO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Twilio integration not configured")
    
    result = twilio_handler.get_call_status(call_sid)
    
    return result

@app.get("/api/call/recordings/{call_sid}")
async def get_call_recordings(call_sid: str):
    """
    Get all recordings from a completed call
    
    Args:
        call_sid: Call SID to get recordings for
    
    Returns list of recording URLs and direct download links
    """
    if not TWILIO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Twilio integration not configured")
    
    result = twilio_handler.get_call_recordings(call_sid)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    # Add direct download URLs from our API (no auth needed!)
    for recording in result.get("recordings", []):
        recording["download_url"] = f"/api/call/recordings/{call_sid}/download/{recording['sid']}"
    
    return result

@app.get("/api/call/recordings/{call_sid}/download/{recording_sid}")
async def download_recording(call_sid: str, recording_sid: str):
    """
    Download recording MP3 directly (NO AUTHENTICATION REQUIRED!)
    
    Just click the link and the MP3 downloads instantly!
    
    Args:
        call_sid: Call SID
        recording_sid: Recording SID (e.g., RE6fcbf2cdb13956ba3691a8f266d694f4)
    
    Returns MP3 file for direct download
    
    Example:
        GET /api/call/recordings/CAd78288c84a58004a9721f4ef51ad71d3/download/RE6fcbf2cdb13956ba3691a8f266d694f4
    """
    if not TWILIO_AVAILABLE:
        raise HTTPException(status_code=503, detail="Twilio integration not configured")
    
    # Download from Twilio using our credentials
    mp3_bytes = twilio_handler.download_recording(recording_sid)
    
    if not mp3_bytes:
        raise HTTPException(status_code=404, detail="Recording not found or failed to download")
    
    # Return MP3 file for download
    return StreamingResponse(
        io.BytesIO(mp3_bytes),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f"attachment; filename=recording_{recording_sid}.mp3"
        }
    )

@app.post("/api/call/recording-callback")
async def recording_callback(
    RecordingSid: str = Form(...),
    RecordingUrl: str = Form(...),
    CallSid: str = Form(...)
):
    """
    Webhook - Twilio calls this when recording is available
    Automatically called by Twilio - not for manual use
    """
    # Store recording URL
    if TWILIO_AVAILABLE:
        twilio_handler.recorded_audio_urls.append({
            "recording_sid": RecordingSid,
            "recording_url": RecordingUrl,
            "call_sid": CallSid,
            "timestamp": datetime.now().isoformat()
        })
    
    return {"status": "recording_received"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

