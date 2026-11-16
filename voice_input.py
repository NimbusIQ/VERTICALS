"""
modules/voice_input.py
─────────────────────
Handles all voice/audio input for the Gemini Coding Agent.

Two modes:
  1. transcribe_audio_file(path)  — Transcribe a local audio file using Gemini's
                                    native audio understanding (no Whisper needed).
  2. record_from_microphone()     — Record from the system microphone and transcribe.

Supported audio formats: mp3, wav, ogg, flac, m4a, webm, aac
"""

import os
import io
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Supported audio MIME types
AUDIO_MIME_TYPES = {
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".m4a": "audio/mp4",
    ".webm": "audio/webm",
    ".aac": "audio/aac",
}


def transcribe_audio_file(file_path: str) -> str:
    """
    Transcribe an audio file to text using Gemini's native audio understanding.

    This sends the audio directly to Gemini as a multi-modal input and asks it
    to transcribe the content, which is more accurate than local Whisper for
    technical/domain-specific speech.

    Args:
        file_path: Path to the audio file.

    Returns:
        Transcribed text string.
    """
    from google import genai
    from google.genai import types

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    suffix = path.suffix.lower()
    mime_type = AUDIO_MIME_TYPES.get(suffix)
    if not mime_type:
        raise ValueError(
            f"Unsupported audio format: {suffix}. "
            f"Supported: {', '.join(AUDIO_MIME_TYPES.keys())}"
        )

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    logger.info(f"Transcribing audio file: {file_path} ({mime_type})")

    with open(file_path, "rb") as f:
        audio_bytes = f.read()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        inline_data=types.Blob(
                            mime_type=mime_type,
                            data=audio_bytes,
                        )
                    ),
                    types.Part(
                        text=(
                            "Please transcribe this audio recording verbatim. "
                            "Focus on technical terms, programming languages, "
                            "framework names, and software requirements. "
                            "Output only the transcription, nothing else."
                        )
                    ),
                ],
            )
        ],
    )

    transcript = response.text.strip()
    logger.info(f"Transcription complete ({len(transcript)} chars).")
    return transcript


def record_from_microphone(duration_seconds: int = 10) -> str:
    """
    Record audio from the system microphone and transcribe it.

    Requires: pyaudio, SpeechRecognition
    Install: pip install pyaudio SpeechRecognition

    Falls back to a manual text input prompt if pyaudio is not available
    (e.g., in a headless server environment).

    Args:
        duration_seconds: Maximum recording duration in seconds.

    Returns:
        Transcribed text string.
    """
    try:
        import speech_recognition as sr

        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print(f"🎤 Recording for up to {duration_seconds} seconds... (speak now)")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=duration_seconds)

        # Save to a temp WAV file and use Gemini to transcribe
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio.get_wav_data())
            tmp_path = tmp.name

        try:
            transcript = transcribe_audio_file(tmp_path)
        finally:
            os.unlink(tmp_path)

        return transcript

    except ImportError:
        logger.warning(
            "pyaudio / SpeechRecognition not installed. "
            "Falling back to manual text input."
        )
        print("⚠️  Microphone libraries not installed.")
        print("   Install with: pip install pyaudio SpeechRecognition")
        print("   Falling back to text input.\n")
        return input("📝 Type your voice request instead: ").strip()

    except Exception as e:
        logger.error(f"Microphone recording failed: {e}")
        print(f"⚠️  Microphone error: {e}")
        print("   Falling back to text input.\n")
        return input("📝 Type your voice request instead: ").strip()
