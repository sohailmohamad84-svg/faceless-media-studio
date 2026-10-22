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

        # 5. Camera Shutter Click (0.15s crisp dual mechanical click for archival photos)
        shutter_path = cls.SFX_DIR / "shutter_click.wav"
        if not shutter_path.exists():
            t_s = np.linspace(0, 0.15, int(sr * 0.15))
            click1 = np.exp(-120 * (t_s - 0.02) ** 2) * (np.random.rand(len(t_s)) * 2 - 1)
            click2 = np.exp(-140 * (t_s - 0.07) ** 2) * (np.random.rand(len(t_s)) * 2 - 1)
            shutter = ((click1 * 0.8 + click2 * 0.6) * 32767 * 0.8).astype(np.int16)
            cls._write_wav(str(shutter_path), shutter, sr)

        # 6. Heavy Rubber Stamp Thud (0.35s deep dull thud for BANKRUPT / SEC stamps)
        stamp_path = cls.SFX_DIR / "stamp_thud.wav"
        if not stamp_path.exists():
            t_st = np.linspace(0, 0.35, int(sr * 0.35))
            thud = np.sin(2 * np.pi * 65 * np.exp(-10 * t_st) * t_st) * np.exp(-12 * t_st)
            click = (np.random.rand(len(t_st)) * 2 - 1) * np.exp(-35 * t_st) * 0.4
            stamp = ((thud * 0.85 + click * 0.35) * 32767 * 0.9).astype(np.int16)
            cls._write_wav(str(stamp_path), stamp, sr)

        # 7. Paper Rustle / Document Slam (0.4s texture)
        paper_path = cls.SFX_DIR / "paper_rustle.wav"
        if not paper_path.exists():
            t_p = np.linspace(0, 0.4, int(sr * 0.4))
            rustle = (np.random.rand(len(t_p)) * 2 - 1) * np.sin(np.pi * t_p / 0.4) * np.exp(-3.5 * t_p)
            paper = (rustle * 32767 * 0.55).astype(np.int16)
            cls._write_wav(str(paper_path), paper, sr)

        return {
            "impact_boom": str(boom_path),
            "whoosh": str(whoosh_path),
            "tension_drone": str(drone_path),
            "chime": str(chime_path),
            "shutter_click": str(shutter_path),
            "stamp_thud": str(stamp_path),
            "paper_rustle": str(paper_path),
        }

    @classmethod
    def composite_master_soundtrack(
        cls,
        voiceover_audio_path: str,
        scene_cues: list,
        output_wav_path: str,
        ffmpeg_bin: str = "ffmpeg",
    ) -> str:
        """Composite an exact, millisecond-accurate multi-track documentary soundtrack:
        - Voiceover at full volume with natural clarity
        - Looping sub-bass ambient tension drone bed
        - Precision SFX hits (camera clicks, rubber stamps, paper rustles, bass booms) placed at exact scene transitions
        """
        import subprocess

        sfx_lib = cls.ensure_sfx_library()
        sr = 44100

        # Step 1: Decode voiceover to 44.1kHz mono WAV
        temp_vo_wav = Path(output_wav_path).parent / "temp_vo_mono.wav"
        subprocess.run(
            [ffmpeg_bin, "-y", "-i", voiceover_audio_path, "-ac", "1", "-ar", str(sr), str(temp_vo_wav)],
            capture_output=True,
            timeout=30,
        )

        def _read_wav_samples(path: str) -> np.ndarray:
            with wave.open(path, "rb") as w:
                n = w.getnframes()
                ch = w.getnchannels()
                data = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32)
                if ch > 1:
                    data = data.reshape(-1, ch).mean(axis=1)
                return data

        vo_data = _read_wav_samples(str(temp_vo_wav)) if temp_vo_wav.exists() else np.zeros(sr * 10, dtype=np.float32)
        total_len = len(vo_data)

        # Step 2: Build Tension Drone Bed
        drone_data = _read_wav_samples(sfx_lib["tension_drone"])
        drone_bed = np.tile(drone_data, int(np.ceil(total_len / len(drone_data))))[:total_len] * 0.09

        # Step 3: Master Bed with SFX Layer
        sfx_bed = np.zeros(total_len, dtype=np.float32)

        # Preload SFX samples into memory
        loaded_sfx = {}
        for name, path in sfx_lib.items():
            if name != "tension_drone" and Path(path).exists():
                loaded_sfx[name] = _read_wav_samples(path)

        for cue in scene_cues:
            # cue is a tuple/dict: (timestamp_sec, sfx_name, volume)
            if isinstance(cue, (list, tuple)) and len(cue) >= 2:
                t_sec, sfx_name = cue[0], cue[1]
                vol = cue[2] if len(cue) > 2 else 0.4
            elif isinstance(cue, dict):
                t_sec = cue.get("time_sec", 0.0)
                sfx_name = cue.get("sfx", "whoosh")
                vol = cue.get("vol", 0.4)
            else:
                continue

            if sfx_name in loaded_sfx:
                s_data = loaded_sfx[sfx_name] * vol
                start_idx = int(t_sec * sr)
                end_idx = min(total_len, start_idx + len(s_data))
                if start_idx < total_len:
                    sfx_bed[start_idx:end_idx] += s_data[: end_idx - start_idx]

        # Step 4: Mix Voiceover + Drone Bed + Precision SFX
        master = vo_data * 1.0 + drone_bed + sfx_bed

        # Soft limiter / normalization to prevent digital distortion
        max_val = np.max(np.abs(master))
        if max_val > 31000:
            master = master * (31000.0 / max_val)

        out_data = master.astype(np.int16)
        cls._write_wav(output_wav_path, out_data, sr)

        # Clean up temp
        if temp_vo_wav.exists():
            temp_vo_wav.unlink(missing_ok=True)

        return output_wav_path

    @staticmethod
    def _write_wav(path: str, data: np.ndarray, samplerate: int):
        with wave.open(path, "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(samplerate)
            f.writeframes(data.tobytes())
