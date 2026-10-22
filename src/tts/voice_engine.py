"""Voiceover synthesis engine supporting Edge-TTS and offline pyttsx3 fallback."""
import asyncio
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import edge_tts
import pyttsx3
from config.settings import DEFAULT_TTS_ENGINE, DEFAULT_VOICE_ID, get_ffmpeg_path
from src.database.models import Voiceover
from src.database.repository import VoiceoverRepository


DEFAULT_PRONUNCIATION_RULES = {
    r"\bSEC\b": "S-E-C",
    r"\bEBITDA\b": "ee-bit-dah",
    r"\bCAGR\b": "cag-er",
    r"\bLBO\b": "L-B-O",
    r"\bIPO\b": "I-P-O",
    r"\bFDD\b": "F-D-D",
    r"\b(\$\d+)M\b": r"\1 million",
    r"\b(\$\d+)B\b": r"\1 billion",
}

AVAILABLE_VOICES = {
    "en-US-ChristopherNeural": {"name": "Christopher (US Male - Documentary Authority)", "gender": "Male", "locale": "en-US"},
    "en-US-GuyNeural": {"name": "Guy (US Male - Narrative Pacing)", "gender": "Male", "locale": "en-US"},
    "en-US-EricNeural": {"name": "Eric (US Male - Energetic & Clear)", "gender": "Male", "locale": "en-US"},
    "en-US-AriaNeural": {"name": "Aria (US Female - Professional & Engaging)", "gender": "Female", "locale": "en-US"},
    "en-US-JennyNeural": {"name": "Jenny (US Female - Friendly & Conversational)", "gender": "Female", "locale": "en-US"},
    "en-GB-RyanNeural": {"name": "Ryan (UK Male - Refined Documentary)", "gender": "Male", "locale": "en-GB"},
}


class VoiceEngine:
    def __init__(self, engine_name: str = DEFAULT_TTS_ENGINE, voice_id: str = DEFAULT_VOICE_ID):
        self.engine_name = engine_name
        self.voice_id = voice_id
        self.rules = DEFAULT_PRONUNCIATION_RULES

    def apply_pronunciation_rules(self, text: str) -> str:
        """Replace difficult financial acronyms, symbols, and shorthand with phonetic equivalents."""
        cleaned = text
        for pattern, replacement in self.rules.items():
            cleaned = re.sub(pattern, replacement, cleaned)
        return cleaned

    def synthesize(self, text: str, output_path: str, rate: str = "+0%", pitch: str = "+0Hz") -> Dict[str, Any]:
        """Synthesize text into an audio file. Falls back to pyttsx3 if Edge-TTS network fails."""
        cleaned_text = self.apply_pronunciation_rules(text)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if self.engine_name == "edge_tts":
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self._synthesize_edge_tts(cleaned_text, str(out), rate, pitch)
                )
                loop.close()
                return result
            except Exception as e:
                # Automatic fallback to local pyttsx3 if network error occurs
                return self._synthesize_pyttsx3(cleaned_text, str(out), fallback_reason=str(e))
        else:
            return self._synthesize_pyttsx3(cleaned_text, str(out))

    async def _synthesize_edge_tts(self, text: str, output_path: str, rate: str, pitch: str) -> Dict[str, Any]:
        """Generate audio using Microsoft Edge-TTS."""
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice_id,
            rate=rate,
            pitch=pitch,
        )
        await communicate.save(output_path)

        # Normalize audio using FFmpeg
        normalized_path = self.normalize_audio(output_path)

        return {
            "success": True,
            "engine": "edge_tts",
            "voice_id": self.voice_id,
            "file_path": normalized_path,
            "text_length": len(text),
        }

    def _synthesize_pyttsx3(self, text: str, output_path: str, fallback_reason: str = None) -> Dict[str, Any]:
        """Generate audio locally and offline using Windows SAPI5 (pyttsx3)."""
        engine = pyttsx3.init()
        engine.setProperty("rate", 160)
        engine.setProperty("volume", 1.0)

        # Output to wav
        wav_path = str(Path(output_path).with_suffix(".wav"))
        engine.save_to_file(text, wav_path)
        engine.runAndWait()
        del engine

        normalized_path = self.normalize_audio(wav_path)

        return {
            "success": True,
            "engine": "pyttsx3_offline",
            "voice_id": "windows_sapi5",
            "file_path": normalized_path,
            "text_length": len(text),
            "fallback_reason": fallback_reason,
        }

    def normalize_audio(self, input_path: str) -> str:
        """Apply EBU R128 loudness normalization (-16 LUFS for YouTube) using FFmpeg."""
        ffmpeg = get_ffmpeg_path()
        inp = Path(input_path)
        out_normalized = inp.parent / f"{inp.stem}_norm.wav"

        cmd = [
            ffmpeg,
            "-y",
            "-i", str(inp),
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-ar", "44100",
            "-ac", "2",
            str(out_normalized),
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if res.returncode == 0 and out_normalized.exists() and out_normalized.stat().st_size > 1000:
                return str(out_normalized)
        except Exception:
            pass
        return input_path
