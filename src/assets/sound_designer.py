"""Procedural sound design engine for high-retention YouTube documentaries."""
import wave
import numpy as np
from pathlib import Path
from typing import Dict


class SoundDesigner:
    SFX_DIR = Path("data/sfx")

    @classmethod
    def ensure_sfx_library(cls) -> Dict[str, str]:
        """Ensure all required cinematic sound effects exist, generating them procedurally if needed."""
        cls.SFX_DIR.mkdir(parents=True, exist_ok=True)
        sr = 44100

        boom_path = cls.SFX_DIR / "impact_boom.wav"
        whoosh_path = cls.SFX_DIR / "whoosh.wav"
        drone_path = cls.SFX_DIR / "tension_drone.wav"
        chime_path = cls.SFX_DIR / "chime.wav"

        # 1. Cinematic Impact Boom (1.5s sub-bass hit)
        if not boom_path.exists():
            t = np.linspace(0, 1.5, int(sr * 1.5))
            freq = 75 * np.exp(-3.5 * t)  # rapid pitch drop
            boom = np.sin(2 * np.pi * freq * t) * np.exp(-2.2 * t)
            noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-12.0 * t) * 0.2
            impact = ((boom + noise) * 32767 * 0.85).astype(np.int16)
            cls._write_wav(str(boom_path), impact, sr)

        # 2. Cinematic Whoosh (0.5s transition sweep)
        if not whoosh_path.exists():
            t_w = np.linspace(0, 0.5, int(sr * 0.5))
            env = np.sin(np.pi * t_w / 0.5) ** 2
            white = (np.random.rand(len(t_w)) * 2 - 1)
            sweep = np.sin(2 * np.pi * (160 + 900 * (t_w / 0.5) ** 2) * t_w)
            whoosh = ((white * 0.35 + sweep * 0.65) * env * 32767 * 0.65).astype(np.int16)
            cls._write_wav(str(whoosh_path), whoosh, sr)

        # 3. Cinematic Tension Drone (45s dark sub-bass ambient bed)
        if not drone_path.exists():
            t_d = np.linspace(0, 45.0, int(sr * 45.0))
            drone = (
                np.sin(2 * np.pi * 50.0 * t_d) * 0.5 +
                np.sin(2 * np.pi * 100.0 * t_d) * 0.25 +
                np.sin(2 * np.pi * 49.5 * t_d) * 0.25  # subtle acoustic beating/pulsing
            )
            drone = (drone * 32767 * 0.30).astype(np.int16)
            cls._write_wav(str(drone_path), drone, sr)

        # 4. Cash Register / Reveal Chime (0.8s)
        if not chime_path.exists():
            t_c = np.linspace(0, 0.8, int(sr * 0.8))
            chime = (
                np.sin(2 * np.pi * 1760 * t_c) * 0.6 +
                np.sin(2 * np.pi * 2637 * t_c) * 0.4
            ) * np.exp(-4.0 * t_c)
            chime = (chime * 32767 * 0.5).astype(np.int16)
            cls._write_wav(str(chime_path), chime, sr)

        return {
            "impact_boom": str(boom_path),
            "whoosh": str(whoosh_path),
            "tension_drone": str(drone_path),
            "chime": str(chime_path),
        }

    @staticmethod
    def _write_wav(path: str, data: np.ndarray, samplerate: int):
        with wave.open(path, "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(samplerate)
            f.writeframes(data.tobytes())
