# utils/evaluate_audio.py

import warnings
import whisper
from pystoi import stoi
# from pesq import pesq  # Commented out as requested
# from jiwer import wer  # Commented out as requested
import librosa
import io
import tempfile
import os
import numpy as np

# Suppress PyTorch warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")

# Load Whisper model once to avoid repeated load latency
model = whisper.load_model("base")

def evaluate_audio(original_audio, degraded_audio, sr=16000):
    """
    Evaluate audio quality between original and degraded audio.
    Accepts either file paths (str) or audio bytes.
    Now only calculates STOI and waveform analysis (PESQ and WER commented out).
    """
    try:
        # Handle original audio (file path or bytes)
        if isinstance(original_audio, str) and os.path.exists(original_audio):
            y_ref, _ = librosa.load(original_audio, sr=sr)
        elif isinstance(original_audio, bytes):
            y_ref, _ = librosa.load(io.BytesIO(original_audio), sr=sr)
        else:
            return {"error": f"Invalid original audio input: {type(original_audio)}"}
        
        # Handle degraded audio (file path or bytes)
        if isinstance(degraded_audio, str) and os.path.exists(degraded_audio):
            y_deg, _ = librosa.load(degraded_audio, sr=sr)
        elif isinstance(degraded_audio, bytes):
            y_deg, _ = librosa.load(io.BytesIO(degraded_audio), sr=sr)
        else:
            return {"error": f"Invalid degraded audio input: {type(degraded_audio)}"}
            
    except Exception as e:
        return {"error": f"Audio loading failed: {str(e)}"}

    try:
        # Ensure both audio arrays have the same length
        min_length = min(len(y_ref), len(y_deg))
        y_ref = y_ref[:min_length]
        y_deg = y_deg[:min_length]
        
        # Check for empty or very short audio
        if min_length < 100:  # Less than ~6ms at 16kHz
            return {"error": "Audio too short for analysis (less than 6ms)"}
        
        # Check if audio is identical (within floating point precision)
        max_diff = np.max(np.abs(y_ref - y_deg))
        if max_diff < 1e-10:  # Essentially identical
            return {
                "stoi": 1.0
            }
        
        # Calculate STOI score
        stoi_score = stoi(y_ref, y_deg, sr, extended=False)
            
    except Exception as e:
        return {"error": f"Metric calculation failed: {str(e)}"}

    # PESQ and WER calculations commented out as requested
    # try:
    #     pesq_score = pesq(sr, y_ref, y_deg, 'wb')  # Use wideband since sample rate is 16kHz
    # except Exception as e:
    #     pesq_score = 0.0  # Default value if PESQ fails
    
    # try:
    #     # Create temporary files for Whisper transcription
    #     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_orig:
    #         if isinstance(original_audio, bytes):
    #             temp_orig.write(original_audio)
    #         else:
    #             with open(original_audio, 'rb') as f:
    #                 temp_orig.write(f.read())
    #         temp_orig_path = temp_orig.name
    #         
    #     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_deg:
    #         if isinstance(degraded_audio, bytes):
    #             temp_deg.write(degraded_audio)
    #         else:
    #             with open(degraded_audio, 'rb') as f:
    #                 temp_deg.write(f.read())
    #         temp_deg_path = temp_deg.name
    #         
    #     ref_result = model.transcribe(temp_orig_path, language='en')
    #     deg_result = model.transcribe(temp_deg_path, language='en')
    #     wer_score = wer(ref_result["text"], deg_result["text"])
    #     
    #     # Clean up temporary files
    #     os.unlink(temp_orig_path)
    #     os.unlink(temp_deg_path)
    #     
    # except Exception as e:
    #     wer_score = 1.0  # Default to worst case if transcription fails

    return {
        "stoi": stoi_score
    }
