# utils/simulate_transmission.py

import random
import numpy as np
from pydub import AudioSegment
import tempfile
import os
import io
from datetime import datetime
import librosa
import soundfile as sf

def simulate_transmission(audio_path_or_bytes, noise_level=0.1, packet_loss=10, compression_level=0.5, segment_ms=100):
    """
    Simulates satcom transmission effects:
    - Random packet loss by dropping segments of audio
    - Gaussian noise injection
    - Compression/vocoder artifacts (robotic, metallic voice quality)
    """
    # If no degradation is requested, return the original audio unchanged
    if noise_level == 0 and packet_loss == 0 and compression_level == 0:
        if isinstance(audio_path_or_bytes, bytes):
            return audio_path_or_bytes
        else:
            # If it's a file path, read and return the bytes
            with open(audio_path_or_bytes, 'rb') as f:
                return f.read()
    
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

    # Apply compression/vocoder artifacts
    if compression_level > 0:
        degraded = apply_compression_artifacts(degraded, compression_level)

    # Convert to bytes for session state storage
    audio_bytes = io.BytesIO()
    degraded.export(audio_bytes, format="wav")
    audio_bytes.seek(0)
    
    return audio_bytes.getvalue()

def apply_compression_artifacts(audio_segment, compression_level):
    """
    Apply compression/vocoder artifacts to simulate satcom audio compression:
    - Bandpass filtering to simulate limited bandwidth
    - Quantization effects
    - Harmonic distortion
    - Temporal smearing
    """
    try:
        # Convert to numpy array
        samples = np.array(audio_segment.get_array_of_samples())
        sample_rate = audio_segment.frame_rate
        
        # Apply bandpass filtering to simulate limited bandwidth (typical satcom: 300Hz - 3kHz)
        low_freq = 300
        high_freq = 3000
        
        # Create bandpass filter
        from scipy import signal
        
        # Design Butterworth bandpass filter
        nyquist = sample_rate / 2
        low = low_freq / nyquist
        high = high_freq / nyquist
        
        if low < 1.0 and high < 1.0:
            b, a = signal.butter(4, [low, high], btype='band')
            samples = signal.filtfilt(b, a, samples)
        
        # Apply quantization effects (simulate low bitrate compression)
        if compression_level > 0.3:
            # Reduce bit depth to simulate compression
            bit_depth = max(8, int(16 - compression_level * 8))
            max_val = 2**(bit_depth - 1) - 1
            samples = np.round(samples / (32768 / max_val)) * (32768 / max_val)
        
        # Apply harmonic distortion (metallic/robotic effect)
        if compression_level > 0.5:
            # Add some harmonic distortion
            distortion_amount = compression_level * 0.3
            samples = samples + distortion_amount * np.sign(samples) * (samples**2) / 32768
        
        # Apply temporal smearing (compression artifacts)
        if compression_level > 0.7:
            # Simple temporal smoothing
            window_size = int(compression_level * 10) + 1
            if window_size > 1:
                samples = np.convolve(samples, np.ones(window_size)/window_size, mode='same')
        
        # Apply frequency domain compression artifacts
        if compression_level > 0.4:
            # Reduce dynamic range in frequency domain
            # This simulates how compression codecs work
            fft_size = 1024
            hop_length = fft_size // 4
            
            # Process in overlapping windows
            processed_samples = np.zeros_like(samples)
            for i in range(0, len(samples) - fft_size, hop_length):
                window = samples[i:i+fft_size]
                window_fft = np.fft.fft(window)
                
                # Reduce dynamic range (compression effect)
                magnitude = np.abs(window_fft)
                compressed_magnitude = np.sign(magnitude) * (magnitude ** (1 - compression_level * 0.5))
                
                # Reconstruct signal
                compressed_fft = compressed_magnitude * np.exp(1j * np.angle(window_fft))
                compressed_window = np.real(np.fft.ifft(compressed_fft))
                
                # Overlap-add
                processed_samples[i:i+fft_size] += compressed_window * 0.5
            
            # Normalize and blend with original
            blend_factor = compression_level * 0.6
            samples = (1 - blend_factor) * samples + blend_factor * processed_samples
        
        # Ensure samples are within valid range
        samples = np.clip(samples, -32768, 32767).astype(np.int16)
        
        # Convert back to AudioSegment
        return audio_segment._spawn(samples.tobytes())
        
    except Exception as e:
        # If compression fails, return original audio
        print(f"Warning: Compression artifacts failed: {str(e)}")
        return audio_segment
