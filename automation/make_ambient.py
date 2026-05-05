"""
soul.orbits — generate a 10s ambient pad WAV for Reels.

A barely-audible low-frequency drone with slight breath envelope. Purpose:
satisfy Meta's audio-track requirement (silent MP4 = silent rejection on
Reel publish) without dominating the Reel — user replaces with IG trending
audio for max reach.

Output: reels/public/audio/ambient.wav
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "reels" / "public" / "audio" / "ambient.wav"
OUT.parent.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100
DURATION_S = 10.0
N = int(SAMPLE_RATE * DURATION_S)


def synth(i: int) -> int:
    t = i / SAMPLE_RATE

    # Slow breath envelope (peak 30% mid-track, soft ends)
    env = 0.5 - 0.5 * math.cos(2 * math.pi * t / DURATION_S)
    env = env * 0.30  # cap volume — barely audible

    # Layered drone: deep root + soft fifth, slowly detuning
    f1 = 65.41  # C2
    f2 = 98.00  # G2
    drift = 0.5 * math.sin(2 * math.pi * t / 4.0)  # 0.25 Hz tremor

    s1 = math.sin(2 * math.pi * (f1 + drift) * t)
    s2 = 0.6 * math.sin(2 * math.pi * (f2 - drift) * t)
    s3 = 0.3 * math.sin(2 * math.pi * (f1 * 2 + drift * 2) * t)

    sample = env * (s1 + s2 + s3) / 3.0
    # 16-bit PCM range
    return max(-32767, min(32767, int(sample * 32767)))


with wave.open(str(OUT), "wb") as w:
    w.setnchannels(1)  # mono
    w.setsampwidth(2)  # 16-bit
    w.setframerate(SAMPLE_RATE)
    frames = bytearray()
    for i in range(N):
        frames.extend(struct.pack("<h", synth(i)))
    w.writeframes(bytes(frames))

print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {DURATION_S}s)")
