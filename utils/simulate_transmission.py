# utils/simulate_transmission.py

import random
import numpy as np
from pydub import AudioSegment
import tempfile
import os
import io
from datetime import datetime

def simulate_transmission(audio_path_or_bytes, noise_level=0.1, packet_loss=10, segment_ms=100):
    """
    Simulates satcom transmission effects:
    - Random packet loss by dropping segments of audio
    - Gaussian noise injection
    """
    try:
        # Handle both file paths and audio bytes
        if isinstance(audio_path_or_bytes, str) and os.path.exists(audio_path_or_bytes):
            # Load from file path
            audio = AudioSegment.from_wav(audio_path_or_bytes)
        elif isinstance(audio_path_or_bytes, bytes):
            # Load from bytes
            audio = AudioSegment.from_wav(io.BytesIO(audio_path_or_bytes))
        else:
            raise RuntimeError(f"Invalid audio input: {audio_path_or_bytes}")
    except Exception as e:
        raise RuntimeError(f"Failed to load audio: {str(e)}")

    # Chop into segments and drop some to simulate packet loss
    chunks = [audio[i:i+segment_ms] for i in range(0, len(audio), segment_ms)]
    retained_chunks = [
        chunk for chunk in chunks if random.randint(0, 100) > packet_loss
    ]
    degraded = sum(retained_chunks) if retained_chunks else audio[:segment_ms]  # fallback if all dropped

    # Inject Gaussian noise
    samples = np.array(degraded.get_array_of_samples())
    noise = np.random.normal(0, noise_level * np.max(np.abs(samples)), samples.shape)
    noisy_samples = np.clip(samples + noise, -32768, 32767).astype(np.int16)
    degraded = degraded._spawn(noisy_samples.tobytes())

    # Convert to bytes for session state storage
    audio_bytes = io.BytesIO()
    degraded.export(audio_bytes, format="wav")
    audio_bytes.seek(0)
    
    return audio_bytes.getvalue()
