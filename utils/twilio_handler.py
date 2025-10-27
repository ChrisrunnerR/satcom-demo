# utils/twilio_handler.py
"""
Twilio Voice Integration for Satcom Ground Station
Handles VOIP calls between Air Side and Ground Side
"""

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather, Record
import os
from typing import Optional, Dict
from datetime import datetime

class TwilioCallHandler:
    def __init__(self):
        """Initialize Twilio client with credentials from environment"""
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.phone_number]):
            print("Warning: Twilio credentials not fully configured")
            self.client = None
        else:
            self.client = Client(self.account_sid, self.auth_token)
        
        # Track active call
        self.active_call_sid = None
        self.call_status = "idle"  # idle, ringing, active, ended
        self.recorded_audio_urls = []
    
    def make_call(self, to_number: str, callback_url: str) -> Dict:
        """
        Make outgoing call to specified number
        
        Args:
            to_number: Phone number to call (e.g., +14155551234)
            callback_url: Your API URL for handling call events
        
        Returns:
            Call details including SID and status
        """
        if not self.client:
            return {"error": "Twilio client not initialized"}
        
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=self.phone_number,
                url=f"{callback_url}/api/call/answer",
                status_callback=f"{callback_url}/api/call/status-callback",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                record=True  # Record the call automatically
            )
            
            self.active_call_sid = call.sid
            self.call_status = "initiated"
            
            return {
                "call_sid": call.sid,
                "to": to_number,
                "from": self.phone_number,
                "status": call.status,
                "message": "Call initiated successfully"
            }
        except Exception as e:
            return {"error": f"Failed to make call: {str(e)}"}
    
    def answer_incoming_call(self, request_data: Dict) -> str:
        """
        Generate TwiML response for incoming call
        Sets up call to record audio and accept commands
        
        Returns:
            TwiML XML string
        """
        response = VoiceResponse()
        
        # Store call SID from Twilio request
        call_sid = request_data.get('CallSid')
        self.active_call_sid = call_sid
        self.call_status = "active"
        
        # Play welcome message
        response.say("Ground station connected. Call established.", voice='Polly.Matthew')
        
        # Start recording the call
        response.record(
            max_length=3600,  # 1 hour max
            transcribe=False,  # We'll use our own STT
            recording_status_callback="/api/call/recording-callback"
        )
        
        # Keep call alive - gather DTMF input or wait
        gather = Gather(
            num_digits=1,
            action="/api/call/gather-callback",
            timeout=30
        )
        response.append(gather)
        
        # If no input, loop back
        response.redirect("/api/call/answer")
        
        return str(response)
    
    def send_audio_to_call(self, call_sid: str, audio_url: str) -> Dict:
        """
        Send audio to active call
        
        Args:
            call_sid: Active call SID
            audio_url: URL of audio file to play (must be publicly accessible)
        
        Returns:
            Status of audio playback
        """
        if not self.client:
            return {"error": "Twilio client not initialized"}
        
        try:
            # Update call to play audio
            call = self.client.calls(call_sid).update(
                twiml=f'<Response><Play>{audio_url}</Play></Response>'
            )
            
            return {
                "call_sid": call_sid,
                "status": "audio_sent",
                "message": f"Playing audio from {audio_url}"
            }
        except Exception as e:
            return {"error": f"Failed to send audio: {str(e)}"}
    
    def send_text_to_call(self, call_sid: str, text: str, voice: str = "Polly.Matthew") -> Dict:
        """
        Send text as speech to active call using TTS
        
        Args:
            call_sid: Active call SID
            text: Text to speak
            voice: Twilio voice to use
        
        Returns:
            Status of TTS playback
        """
        if not self.client:
            return {"error": "Twilio client not initialized"}
        
        try:
            # Update call to speak text
            call = self.client.calls(call_sid).update(
                twiml=f'<Response><Say voice="{voice}">{text}</Say></Response>'
            )
            
            return {
                "call_sid": call_sid,
                "status": "text_sent",
                "message": f"Speaking: {text[:50]}..."
            }
        except Exception as e:
            return {"error": f"Failed to send text: {str(e)}"}
    
    def hangup_call(self, call_sid: Optional[str] = None) -> Dict:
        """
        End active call
        
        Args:
            call_sid: Call SID to hang up (uses active call if None)
        
        Returns:
            Status of hangup
        """
        if not self.client:
            return {"error": "Twilio client not initialized"}
        
        sid_to_hangup = call_sid or self.active_call_sid
        
        if not sid_to_hangup:
            return {"error": "No active call to hang up"}
        
        try:
            call = self.client.calls(sid_to_hangup).update(status="completed")
            
            self.call_status = "ended"
            self.active_call_sid = None
            
            return {
                "call_sid": sid_to_hangup,
                "status": "ended",
                "message": "Call ended successfully"
            }
        except Exception as e:
            return {"error": f"Failed to hang up: {str(e)}"}
    
    def get_call_status(self, call_sid: Optional[str] = None) -> Dict:
        """
        Get status of call
        
        Args:
            call_sid: Call SID to check (uses active call if None)
        
        Returns:
            Call status and details
        """
        if not self.client:
            return {"error": "Twilio client not initialized"}
        
        sid_to_check = call_sid or self.active_call_sid
        
        if not sid_to_check:
            return {
                "status": "no_active_call",
                "message": "No active call"
            }
        
        try:
            call = self.client.calls(sid_to_check).fetch()
            
            return {
                "call_sid": call.sid,
                "status": call.status,
                "direction": call.direction,
                "from": call.from_,
                "to": call.to,
                "duration": call.duration,
                "start_time": str(call.start_time),
                "end_time": str(call.end_time)
            }
        except Exception as e:
            return {"error": f"Failed to get call status: {str(e)}"}
    
    def get_call_recordings(self, call_sid: str) -> Dict:
        """
        Get recordings from a completed call
        
        Args:
            call_sid: Call SID
        
        Returns:
            List of recording URLs
        """
        if not self.client:
            return {"error": "Twilio client not initialized"}
        
        try:
            recordings = self.client.recordings.list(call_sid=call_sid, limit=20)
            
            recording_urls = [
                {
                    "sid": rec.sid,
                    "duration": rec.duration,
                    "url": f"https://api.twilio.com{rec.uri.replace('.json', '.mp3')}",
                    "date_created": str(rec.date_created)
                }
                for rec in recordings
            ]
            
            return {
                "call_sid": call_sid,
                "recordings": recording_urls,
                "count": len(recording_urls)
            }
        except Exception as e:
            return {"error": f"Failed to get recordings: {str(e)}"}

# Global instance
twilio_handler = TwilioCallHandler()

