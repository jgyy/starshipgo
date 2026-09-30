#!/usr/bin/env python3
"""Procedural sound effects for the ship interior (numpy + stdlib wave, no assets needed).

    python tools/audio/generate_audio.py            # writes godot/audio/*.wav
"""
import os
import wave

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "godot", "audio")
SR = 22050
rng = np.random.default_rng(1701)


def save(name, x):
    x = np.clip(x, -1, 1)
    pcm = (x * 32000).astype("<i2")
    os.makedirs(OUT, exist_ok=True)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def lowpass_periodic(n, cutoff_hz, slope=2.0):
    """Periodic (seamlessly loopable) coloured noise: shape white noise in the frequency domain."""
    spec = np.fft.rfft(rng.normal(size=n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec *= 1.0 / (1.0 + (f / cutoff_hz) ** slope)
    spec[0] = 0
    x = np.fft.irfft(spec, n)
    return x / np.abs(x).max()


def ambient_hum(seconds=8):
    n = SR * seconds
    t = np.arange(n) / SR
    # integer number of cycles over the loop length -> seamless
    tone = sum(a * np.sin(2 * np.pi * (f * seconds // 1 / seconds) * t) for f, a in ((50, .5), (100, .25), (150, .1), (75, .12)))
    air = lowpass_periodic(n, 900, 1.5) * 0.35
    wobble = 1 + 0.08 * np.sin(2 * np.pi * (2 / seconds) * t)
    save("ambient_hum", (tone * 0.5 + air) * wobble * 0.55)


def engine_rumble(seconds=8):
    n = SR * seconds
    t = np.arange(n) / SR
    rum = lowpass_periodic(n, 120, 3.0) * 0.9
    pulse = 0.5 * np.sin(2 * np.pi * (24 / seconds) * t) + 0.3 * np.sin(2 * np.pi * (36 / seconds) * t)
    save("engine_rumble", (rum + pulse * 0.4) * 0.7)


def footstep(idx):
    n = int(SR * 0.32)
    t = np.arange(n) / SR
    env = np.exp(-t * 28)
    ring = np.sin(2 * np.pi * (170 + idx * 23) * t) * np.exp(-t * 16) * 0.5
    thump = np.sin(2 * np.pi * (65 + idx * 6) * t) * np.exp(-t * 20)
    click = lowpass_periodic(n, 2500, 1.0) * np.exp(-t * 60)
    save(f"footstep_{idx + 1}", (thump * 0.9 + ring + click * 0.6 + lowpass_periodic(n, 900) * env * 0.25) * 0.75)


def door():
    n = int(SR * 0.9)
    t = np.arange(n) / SR
    sweep = np.sin(2 * np.pi * np.cumsum(180 + 380 * np.sin(np.pi * t / 0.9)) / SR)
    swish = lowpass_periodic(n, 3200, 1.2) * np.sin(np.pi * t / 0.9) ** 1.5
    clunk = np.exp(-(t - 0.02) ** 2 / 0.0002) * 0.0 + np.sin(2 * np.pi * 90 * t) * np.exp(-t * 30) * 0.5
    save("door", (sweep * 0.14 * np.sin(np.pi * t / 0.9) + swish * 0.55 + clunk) * 0.9)


def lift():
    n = int(SR * 2.4)
    t = np.arange(n) / SR
    hum = np.sin(2 * np.pi * (60 + 30 * np.sin(np.pi * t / 2.4)) * t) * 0.3
    air = lowpass_periodic(n, 700) * 0.2
    ding_t = np.clip(t - 1.7, 0, None)
    ding = (np.sin(2 * np.pi * 988 * ding_t) + 0.4 * np.sin(2 * np.pi * 1976 * ding_t)) * np.exp(-ding_t * 5) * (t > 1.7) * 0.35
    save("lift", (hum + air) * np.minimum(1, t * 8) * np.minimum(1, (2.4 - t) * 4) + ding)


if __name__ == "__main__":
    ambient_hum()
    engine_rumble()
    for i in range(3):
        footstep(i)
    door()
    lift()
    print("wrote", sorted(os.listdir(OUT)))
