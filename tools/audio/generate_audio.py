#!/usr/bin/env python3
"""Procedural sound effects for the ship interior (numpy + stdlib wave, no assets needed).

    python tools/audio/generate_audio.py            # writes godot/audio/*.wav
    python tools/audio/generate_audio.py OUT_DIR    # writes somewhere else

Output is deterministic: every sound draws from its own RNG seeded from the sound name, so adding
or reordering sounds never changes the others.  Format: 16-bit mono PCM, 22050 Hz.
"""
import os
import sys
import zlib
import wave

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "godot", "audio")
SR = 22050
FOOT_PEAK = 23000   # int16 peak of footsteps / door, about -3 dBFS (23000/32768)


def rng_for(name):
    return np.random.default_rng(zlib.crc32(name.encode()))


def remove_dc(x):
    return x - np.mean(x)


def save(out, name, x, peak=None):
    """Write x (nominally -1..1) as 16-bit mono WAV. With `peak` (int16 units) the clip is DC-free
    and normalised to exactly that peak; otherwise it is scaled by 32000 and clipped."""
    if peak is not None:
        x = remove_dc(x)
        pcm = np.rint(x / np.abs(x).max() * peak).astype("<i2")
    else:
        pcm = np.rint(np.clip(x, -1, 1) * 32000).astype("<i2")
    os.makedirs(out, exist_ok=True)
    with wave.open(os.path.join(out, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def lowpass_periodic(rng, n, cutoff_hz, slope=2.0):
    """Periodic (seamlessly loopable) coloured noise: shape white noise in the frequency domain."""
    spec = np.fft.rfft(rng.normal(size=n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec *= 1.0 / (1.0 + (f / cutoff_hz) ** slope)
    spec[0] = 0
    x = np.fft.irfft(spec, n)
    return x / np.abs(x).max()


def ambient_hum(out, seconds=8):
    rng = rng_for("ambient_hum")
    n = SR * seconds
    t = np.arange(n) / SR
    # integer number of cycles over the loop length -> seamless
    tone = sum(a * np.sin(2 * np.pi * (f * seconds // 1 / seconds) * t) for f, a in ((50, .5), (100, .25), (150, .1), (75, .12)))
    air = lowpass_periodic(rng, n, 900, 1.5) * 0.35
    wobble = 1 + 0.08 * np.sin(2 * np.pi * (2 / seconds) * t)
    save(out, "ambient_hum", remove_dc((tone * 0.5 + air) * wobble * 0.55))


def engine_rumble(out, seconds=8):
    rng = rng_for("engine_rumble")
    n = SR * seconds
    t = np.arange(n) / SR
    rum = lowpass_periodic(rng, n, 120, 3.0) * 0.9
    pulse = 0.5 * np.sin(2 * np.pi * (24 / seconds) * t) + 0.3 * np.sin(2 * np.pi * (36 / seconds) * t)
    save(out, "engine_rumble", remove_dc((rum + pulse * 0.4) * 0.7))


def footstep(out, idx):
    name = f"footstep_{idx + 1}"
    rng = rng_for(name)
    n = int(SR * 0.32)
    t = np.arange(n) / SR
    env = np.exp(-t * 28)
    ring = np.sin(2 * np.pi * (170 + idx * 23) * t) * np.exp(-t * 16) * 0.5
    thump = np.sin(2 * np.pi * (65 + idx * 6) * t) * np.exp(-t * 20)
    click = lowpass_periodic(rng, n, 2500, 1.0) * np.exp(-t * 60)
    x = thump * 0.9 + ring + click * 0.6 + lowpass_periodic(rng, n, 900) * env * 0.25
    save(out, name, x, peak=FOOT_PEAK)


def door(out):
    """~0.45 s: door.gd slides the leaf in ~0.31 s, then a short hiss. The swish peaks at the start."""
    rng = rng_for("door")
    n = int(SR * 0.45)
    t = np.arange(n) / SR
    swish_env = np.minimum(1.0, t / 0.008) * np.exp(-t * 7.0)
    sweep = np.sin(2 * np.pi * np.cumsum(520 - 380 * np.minimum(1.0, t / 0.35)) / SR) * swish_env
    swish = lowpass_periodic(rng, n, 3200, 1.2) * swish_env
    clunk = np.sin(2 * np.pi * 90 * t) * np.exp(-t * 30) * 0.5
    save(out, "door", sweep * 0.14 + swish * 0.55 + clunk, peak=FOOT_PEAK)


def generate(out=OUT):
    ambient_hum(out)
    engine_rumble(out)
    for i in range(3):
        footstep(out, i)
    door(out)
    return sorted(os.listdir(out))


if __name__ == "__main__":
    print("wrote", generate(sys.argv[1] if len(sys.argv) > 1 else OUT))
