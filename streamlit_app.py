# Streamlit App Entry Point (streamlit_app.py)
import streamlit as st
import requests
import tempfile
import os
import io
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from google.cloud import texttospeech
from dotenv import load_dotenv
import google.auth
from google.oauth2 import service_account
import json

# Access Together AI key
together_api_key = st.secrets["together"]["api_key"]

# Load credentials from secrets
gcp_credentials = service_account.Credentials.from_service_account_info(
    json.loads(st.secrets["gcp"]["credentials"])
)

tts_client = texttospeech.TextToSpeechClient(credentials=gcp_credentials)

# Inject credentials when creating the client
client = tts_client

# Load environment variables from .env file
load_dotenv()

from utils import generate_text, simulate_transmission, evaluate_audio

# Create audio directory if it doesn't exist (for local development)
os.makedirs("audio", exist_ok=True)

def plot_waveform_with_analysis(original_bytes, degraded_bytes, noise_level, packet_loss):
    """Create waveform plots with highlighting for problem areas"""
    import librosa
    
    # Load audio data
    y_orig, sr = librosa.load(io.BytesIO(original_bytes), sr=16000)
    y_degraded, sr = librosa.load(io.BytesIO(degraded_bytes), sr=16000)
    
    # Ensure same length for comparison
    min_length = min(len(y_orig), len(y_degraded))
    y_orig = y_orig[:min_length]
    y_degraded = y_degraded[:min_length]
    
    # Create time axis
    time = np.linspace(0, len(y_orig) / sr, len(y_orig))
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Original waveform
    ax1.plot(time, y_orig, 'b-', alpha=0.7, linewidth=0.5, label='Original Audio')
    ax1.set_title('Original Audio Waveform', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Amplitude')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Degraded waveform with highlighting
    ax2.plot(time, y_degraded, 'r-', alpha=0.7, linewidth=0.5, label='Transmitted Audio')
    
    # Highlight areas with significant differences (potential packet loss)
    diff_threshold = 0.1 * np.max(np.abs(y_orig))
    significant_diff = np.abs(y_orig - y_degraded) > diff_threshold
    
    # Highlight problem areas
    if np.any(significant_diff):
        ax2.fill_between(time, -1, 1, where=significant_diff, 
                        alpha=0.3, color='yellow', label='Problem Areas')
    
    ax2.set_title(f'Transmitted Audio Waveform (Noise: {noise_level:.2f}, Packet Loss: {packet_loss}%)', 
                  fontsize=14, fontweight='bold')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('Amplitude')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

st.set_page_config(page_title="Satcom Audio Demo", layout="centered")
st.title("📡 Satcom Audio Transmission Demo")

# 1. Text Input or GPT Generation
st.subheader("1. Input Text")

# Initialize session state for text if not exists
if "current_text" not in st.session_state:
    st.session_state["current_text"] = "The quick brown fox jumps over the lazy dog."

# Always show the text area with current text
input_text = st.text_area("Enter your message", value=st.session_state["current_text"], height=100, key="text_input")

# GPT generation button
if st.button("🤖 Generate with GPT"):
    st.session_state["show_gpt_form"] = True

# GPT generation form (popup-like)
if st.session_state.get("show_gpt_form", False):
    with st.form("gpt_generation_form"):
        st.markdown("### Generate Text with GPT")
        word_count = st.number_input("Number of words", min_value=5, max_value=100, value=15, step=1)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Generate"):
                with st.spinner("Generating text..."):
                    generated_text = generate_text(word_count, api_key=together_api_key)
                    st.session_state["current_text"] = generated_text
                    st.session_state["show_gpt_form"] = False
                    st.rerun()
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state["show_gpt_form"] = False
                st.rerun()

# 2. Generate Speech with Google TTS
st.subheader("2. Generate Speech")
tts_button = st.button("🔊 Generate Speech")

if tts_button and input_text:
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Stage 1: Initializing TTS client
        status_text.text("Initializing text-to-speech client...")
        progress_bar.progress(20)
        
        # Use the pre-configured client with credentials
        # client = texttospeech.TextToSpeechClient()
        
        # Stage 2: Preparing text for conversion
        status_text.text("Preparing text for speech conversion...")
        progress_bar.progress(40)

        synthesis_input = texttospeech.SynthesisInput(text=input_text)

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Chirp3-HD-Algenib"
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=0.90
        )

        # Stage 3: Sending request to TTS server
        status_text.text("Sending text to conversion server...")
        progress_bar.progress(60)
        
        response = tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

        # Stage 4: Converting speech
        status_text.text("Converting text to speech...")
        progress_bar.progress(80)

        # Store audio in session state for Streamlit Cloud compatibility
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"tts_output_{timestamp}.wav"
        
        # Save to audio directory for local development, or use session state for cloud
        st.session_state["original_audio_path"] = audio_filename
        st.session_state["original_audio_bytes"] = response.audio_content

        # Stage 5: Complete
        status_text.text("Speech generation complete!")
        progress_bar.progress(100)
        
        # Display audio using bytes for cloud compatibility
        st.audio(st.session_state["original_audio_bytes"], format="audio/wav")
        
    except Exception as e:
        status_text.text(f"Error during speech generation: {str(e)}")
        progress_bar.progress(0)
        st.error(f"Failed to generate speech: {str(e)}")

# 3. Simulate Transmission
st.subheader("3. Simulate Satcom Transmission")
if "original_audio_bytes" in st.session_state:
    noise_level = st.slider("Noise Level", 0.0, 1.0, 0.1, step=0.05)
    packet_loss = st.slider("Packet Loss %", 0, 50, 10, step=5)
    if st.button("🚀 Transmit Audio"):
        with st.spinner("Simulating satcom transmission..."):
            transmitted_audio_bytes = simulate_transmission(
                st.session_state["original_audio_bytes"], noise_level, packet_loss
            )
            st.session_state["received_audio_bytes"] = transmitted_audio_bytes
            st.session_state["transmission_params"] = {"noise_level": noise_level, "packet_loss": packet_loss}
            st.audio(transmitted_audio_bytes, format="audio/wav")

# 4. Waveform Analysis
st.subheader("4. Waveform Analysis")
if "received_audio_bytes" in st.session_state:
    if st.button("📊 Generate Waveform Analysis"):
        with st.spinner("Generating waveform analysis..."):
            # Display waveform analysis
            fig = plot_waveform_with_analysis(
                st.session_state["original_audio_bytes"],
                st.session_state["received_audio_bytes"],
                st.session_state["transmission_params"]["noise_level"],
                st.session_state["transmission_params"]["packet_loss"]
            )
            st.pyplot(fig)
            
            # Add analysis explanation
            st.markdown("""
            **Waveform Analysis:**
            - **Blue line**: Original audio waveform
            - **Red line**: Transmitted audio waveform  
            - **Yellow highlights**: Problem areas where significant differences occur
            - **Problem areas** indicate packet loss, noise interference, or signal degradation
            """)

# 5. Evaluate Audio
st.subheader("5. Evaluate Transmission Quality")
if "received_audio_bytes" in st.session_state:
    if st.button("📈 Run Evaluation"):
        with st.spinner("Evaluating audio quality..."):
            scores = evaluate_audio(
                st.session_state["original_audio_bytes"],
                st.session_state["received_audio_bytes"]
            )
            
            # Check if evaluation was successful
            if "error" in scores:
                st.error(f"Evaluation failed: {scores['error']}")
            else:
                # Display scores with expandable details
                st.markdown(f"**STOI:** {scores['stoi']:.2f}")
                with st.expander("ℹ️ STOI Details"):
                    st.markdown("""
                    **STOI (Short-Time Objective Intelligibility)**
                    
                    **Definition:** Measures speech intelligibility by evaluating correlation between clean and processed speech spectral envelopes.
                    
                    **Range:** 0 to 1 (higher is better)
                    - 0.9-1.0: Excellent intelligibility
                    - 0.7-0.9: Good intelligibility  
                    - 0.5-0.7: Moderate intelligibility
                    - 0.0-0.5: Poor intelligibility
                    
                    **Your Score:** {:.2f} - {}
                    """.format(scores['stoi'], 
                              "Excellent" if scores['stoi'] >= 0.9 else "Good" if scores['stoi'] >= 0.7 else "Moderate" if scores['stoi'] >= 0.5 else "Poor"))
                
                st.markdown(f"**PESQ:** {scores['pesq']:.2f}")
                with st.expander("ℹ️ PESQ Details"):
                    st.markdown("""
                    **PESQ (Perceptual Evaluation of Speech Quality)**
                    
                    **Definition:** Assesses subjective speech quality accounting for distortion, noise, and perceptual differences.
                    
                    **Range:** -0.5 to 4.5 (higher is better)
                    - 4.0-4.5: Excellent quality
                    - 3.0-4.0: Good quality
                    - 2.0-3.0: Moderate quality
                    - 0.0-2.0: Poor quality
                    
                    **Your Score:** {:.2f} - {}
                    """.format(scores['pesq'],
                              "Excellent" if scores['pesq'] >= 4.0 else "Good" if scores['pesq'] >= 3.0 else "Moderate" if scores['pesq'] >= 2.0 else "Poor"))
                
                st.markdown(f"**WER:** {scores['wer']:.2f}")
                with st.expander("ℹ️ WER Details"):
                    st.markdown("""
                    **WER (Word Error Rate)**
                    
                    **Definition:** Measures ASR accuracy by calculating error rate in transcribed words.
                    
                    **Formula:** (Insertions + Deletions + Substitutions) / Total Words
                    
                    **Range:** 0 to 1 (lower is better)
                    - 0.0-0.05: Excellent transcription
                    - 0.05-0.10: Good transcription
                    - 0.10-0.20: Moderate transcription
                    - 0.20-1.0: Poor transcription
                    
                    **Your Score:** {:.2f} ({:.0%}) - {}
                    """.format(scores['wer'], scores['wer'],
                              "Excellent" if scores['wer'] <= 0.05 else "Good" if scores['wer'] <= 0.10 else "Moderate" if scores['wer'] <= 0.20 else "Poor"))
                
                # Overall summary
                st.markdown("---")
                st.markdown("**📋 Summary:**")
                if scores['stoi'] < 0.5 and scores['pesq'] < 2.0:
                    st.warning("Low speech quality detected.")
                elif scores['wer'] < 0.1:
                    st.success("Good transcription accuracy despite quality issues.")
                else:
                    st.info("Mixed results - check individual metrics for details.")
