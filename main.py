"""
Google Cloud Text-to-Speech API Server

A FastAPI server that provides text-to-speech synthesis using Google Cloud TTS API.
Supports multiple languages and voices with streaming audio responses.
"""

import os
import logging
import base64
from typing import List, Optional, Dict, Any
from io import BytesIO

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from google.cloud import texttospeech
from google.api_core import exceptions as gcp_exceptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Google TTS Server",
    description="Text-to-Speech API using Google Cloud TTS",
    version="1.0.0",
)

# Initialize Google TTS client
try:
    tts_client = texttospeech.TextToSpeechClient()
    logger.info("Google TTS client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Google TTS client: {e}")
    tts_client = None


class TTSRequest(BaseModel):
    """Request model for text-to-speech synthesis."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
    voice: str = Field(..., description="Voice ID (e.g., 'en-US-Wavenet-A')")
    speed: Optional[float] = Field(1.0, ge=0.25, le=4.0, description="Speech speed (0.25-4.0)")
    pitch: Optional[float] = Field(0.0, ge=-20.0, le=20.0, description="Voice pitch (-20.0 to 20.0)")

    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()


class VoiceInfo(BaseModel):
    """Voice information model."""
    name: str
    language_code: str
    gender: str
    natural_sample_rate: int


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    details: Optional[str] = None


class Base64TTSResponse(BaseModel):
    """Response model for base64-encoded MP3 audio."""
    audio_base64: str
    content_type: str = "audio/mpeg"
    size: int


def extract_language_code(voice_name: str) -> str:
    """Extract language code from voice name."""
    # Voice names typically follow pattern: "en-US-Wavenet-A"
    parts = voice_name.split('-')
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return "en-US"  # fallback


def get_supported_voices() -> List[VoiceInfo]:
    """Get list of supported voices for RU, HE, EN languages."""
    if not tts_client:
        return []
    
    try:
        # List available voices from Google
        voices_response = tts_client.list_voices()
        supported_languages = ["en", "ru", "he"]
        filtered_voices = []
        
        for voice in voices_response.voices:
            for language_code in voice.language_codes:
                # Check if voice supports any of our target languages
                lang_prefix = language_code.split('-')[0].lower()
                if lang_prefix in supported_languages:
                    filtered_voices.append(VoiceInfo(
                        name=voice.name,
                        language_code=language_code,
                        gender=voice.ssml_gender.name,
                        natural_sample_rate=voice.natural_sample_rate_hertz
                    ))
                    break
        
        return filtered_voices
    except Exception as e:
        logger.error(f"Failed to fetch voices: {e}")
        return []


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Google TTS Server",
        "version": "1.0.0",
        "endpoints": {
            "tts": "POST /tts - Text to speech synthesis",
            "voices": "GET /voices - List available voices",
            "health": "GET /health - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not tts_client:
        raise HTTPException(status_code=503, detail="TTS client not initialized")
    
    return {
        "status": "healthy",
        "tts_client": "connected",
        "google_credentials": "GOOGLE_APPLICATION_CREDENTIALS" in os.environ
    }


@app.get("/voices", response_model=List[VoiceInfo])
async def list_voices():
    """Get list of available voices for supported languages (RU, HE, EN)."""
    if not tts_client:
        raise HTTPException(
            status_code=503, 
            detail="TTS client not initialized. Check Google Cloud credentials."
        )
    
    try:
        voices = get_supported_voices()
        if not voices:
            logger.warning("No voices found for supported languages")
        return voices
    except gcp_exceptions.GoogleAPICallError as e:
        logger.error(f"Google API error: {e}")
        raise HTTPException(status_code=503, detail=f"Google API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error fetching voices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch voices")


@app.post("/tts")
async def synthesize_speech(request: TTSRequest):
    """
    Synthesize text to speech and return audio stream.
    
    Returns MP3 audio file as streaming response.
    """
    if not tts_client:
        raise HTTPException(
            status_code=503,
            detail="TTS client not initialized. Check Google Cloud credentials."
        )
    
    try:
        # Extract language code from voice name
        language_code = extract_language_code(request.voice)
        
        # Configure synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=request.text)
        
        # Configure voice parameters
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=request.voice,
        )
        
        # Configure audio output
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=request.speed,
            pitch=request.pitch,
        )
        
        # Perform TTS synthesis
        logger.info(f"Synthesizing text: '{request.text[:50]}...' with voice: {request.voice}")
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )
        
        # Create streaming response
        audio_stream = BytesIO(response.audio_content)
        
        return StreamingResponse(
            BytesIO(response.audio_content),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Content-Length": str(len(response.audio_content))
            }
        )
        
    except gcp_exceptions.InvalidArgument as e:
        logger.error(f"Invalid argument error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid voice or parameters: {e}")
    except gcp_exceptions.GoogleAPICallError as e:
        logger.error(f"Google API call error: {e}")
        raise HTTPException(status_code=503, detail=f"Google TTS API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during synthesis: {e}")
        raise HTTPException(status_code=500, detail="Text-to-speech synthesis failed")


@app.post("/tts/base64", response_model=Base64TTSResponse)
async def synthesize_speech_base64(request: TTSRequest):
    """
    Synthesize text to speech and return audio as base64 string.

    Returns JSON with fields: audio_base64, content_type, size.
    """
    if not tts_client:
        raise HTTPException(
            status_code=503,
            detail="TTS client not initialized. Check Google Cloud credentials."
        )

    try:
        language_code = extract_language_code(request.voice)

        synthesis_input = texttospeech.SynthesisInput(text=request.text)

        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=request.voice,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=request.speed,
            pitch=request.pitch,
        )

        logger.info(
            f"Synthesizing (base64) text: '{request.text[:50]}...' with voice: {request.voice}"
        )
        response = tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config,
        )

        audio_bytes = response.audio_content
        audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

        return Base64TTSResponse(
            audio_base64=audio_b64,
            content_type="audio/mpeg",
            size=len(audio_bytes),
        )

    except gcp_exceptions.InvalidArgument as e:
        logger.error(f"Invalid argument error (base64): {e}")
        raise HTTPException(status_code=400, detail=f"Invalid voice or parameters: {e}")
    except gcp_exceptions.GoogleAPICallError as e:
        logger.error(f"Google API call error (base64): {e}")
        raise HTTPException(status_code=503, detail=f"Google TTS API error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during base64 synthesis: {e}")
        raise HTTPException(status_code=500, detail="Text-to-speech base64 synthesis failed")


if __name__ == "__main__":
    import uvicorn
    
    # Check for Google credentials
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        logger.warning(
            "GOOGLE_APPLICATION_CREDENTIALS not set. "
            "Make sure to set this environment variable to your service account key path."
        )
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3010,
        reload=True,
        log_level="info"
    )