import wave
import struct
import numpy as np

def generate_cinematic_pulse():
    sr = 48000
    duration = 90.0  # 90 seconds
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    # 1. Warm Sub-Bass Foundation (55 Hz A1 and 73.4 Hz D2) with slow rhythmic pulse
    # 0.5 Hz pulse rate (breathes every 2 seconds, 60 BPM half-time)
    pulse = 0.65 + 0.35 * np.sin(2 * np.pi * 0.5 * t - np.pi/2)
    sub = np.sin(2 * np.pi * 55.0 * t) * 0.35 + np.sin(2 * np.pi * 73.4 * t) * 0.25
    sub_track = sub * pulse
    
    # 2. Cinematic Chord Movement (D min -> Bb maj -> F maj -> C maj)
    # Slow 8-second chord progression
    chord_period = 8.0
    chord_idx = (t // chord_period) % 4
    
    # Frequencies for smooth atmospheric pads (low octave)
    # Dm: D3 (146.8), F3 (174.6), A3 (220.0)
    # Bb: Bb2 (116.5), D3 (146.8), F3 (174.6)
    # F:  F2 (87.3),  A2 (110.0), C3 (130.8)
    # C:  C3 (130.8), E3 (164.8), G3 (196.0)
    chords = [
        [146.8, 174.6, 220.0],
        [116.5, 146.8, 174.6],
        [87.3, 110.0, 130.8],
        [130.8, 164.8, 196.0]
    ]
    
    pad_track = np.zeros(num_samples, dtype=np.float32)
    # Synthesize chord layers with smooth cross-fades
    for i in range(int(duration // chord_period) + 1):
        c_start = i * chord_period
        c_end = (i + 1) * chord_period
        c_idx = i % 4
        freqs = chords[c_idx]
        
        mask = (t >= c_start) & (t < c_end)
        if not np.any(mask):
            continue
            
        t_segment = t[mask] - c_start
        # Attack / decay envelope for each chord (smooth 1s fade-in, 1s fade-out)
        env = np.ones_like(t_segment)
        fade_len = int(1.2 * sr)
        if len(env) > 2 * fade_len:
            env[:fade_len] = np.linspace(0, 1, fade_len)
            env[-fade_len:] = np.linspace(1, 0, fade_len)
            
        chord_wave = sum(np.sin(2 * np.pi * f * t_segment) for f in freqs) / len(freqs)
        pad_track[mask] += chord_wave * env * 0.35

    # 3. Soft Pink/Brown Noise Warmth (simulating tape warmth, heavily filtered)
    noise = np.random.normal(0, 0.05, num_samples).astype(np.float32)
    # Simple moving average low-pass filter (cutoff ~300 Hz)
    window_size = int(sr / 300)
    kernel = np.ones(window_size) / window_size
    warm_noise = np.convolve(noise, kernel, mode='same') * 0.15

    # Combine all elements
    mix = sub_track * 0.5 + pad_track * 0.4 + warm_noise * 0.1
    
    # Master gain normalization: gentle, smooth, quiet
    max_val = np.max(np.abs(mix))
    if max_val > 0:
        mix = mix / max_val * 0.25  # Max peak 0.25 (-12 dB peak before ducking)
        
    # Convert to 16-bit stereo PCM
    left = mix
    right = mix
    stereo = np.empty((num_samples * 2,), dtype=np.int16)
    stereo[0::2] = (np.clip(left, -1.0, 1.0) * 32767).astype(np.int16)
    stereo[1::2] = (np.clip(right, -1.0, 1.0) * 32767).astype(np.int16)
    
    out_path = "data/sfx/cinematic_ambient_pulse.wav"
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(stereo.tobytes())
        
    print(f"Generated clean cinematic ambient bed: {out_path} ({len(stereo)*2:,} bytes)")

if __name__ == "__main__":
    generate_cinematic_pulse()
