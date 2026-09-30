"""Audio generator tests (skipped when numpy is unavailable)."""
import hashlib
import os
import sys
import tempfile
import unittest
import wave

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AUDIO = os.path.join(ROOT, "godot", "audio")
sys.path.insert(0, os.path.join(ROOT, "tools", "audio"))

try:
    import numpy as np
    import generate_audio
except ImportError:  # CI python job installs only the stdlib
    np = None

NAMES = ["ambient_hum", "engine_rumble", "footstep_1", "footstep_2", "footstep_3", "door"]


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def read(path):
    with wave.open(path, "rb") as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2
        rate = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64)
    return rate, data


@unittest.skipUnless(np is not None, "numpy not available")
class AudioTests(unittest.TestCase):
    def test_files_exist_and_format(self):
        for n in NAMES:
            p = os.path.join(AUDIO, n + ".wav")
            self.assertTrue(os.path.exists(p), p)
            with wave.open(p, "rb") as w:
                self.assertEqual(w.getnchannels(), 1, n)
                self.assertEqual(w.getsampwidth(), 2, n)
                self.assertEqual(w.getframerate(), generate_audio.SR, n)

    def test_no_lift_sound(self):
        self.assertFalse(os.path.exists(os.path.join(AUDIO, "lift.wav")))
        self.assertFalse(os.path.exists(os.path.join(AUDIO, "lift.wav.import")))
        self.assertFalse(hasattr(generate_audio, "lift"))

    def test_peaks_and_dc(self):
        for n in NAMES:
            _, x = read(os.path.join(AUDIO, n + ".wav"))
            peak = np.abs(x).max()
            self.assertLess(peak / 32768, 0.95, n)
            self.assertGreater(peak, 1000, n)
            self.assertLess(abs(x.mean()), 0.01 * peak, n)

    def test_footsteps_common_peak(self):
        peaks = [np.abs(read(os.path.join(AUDIO, "footstep_%d.wav" % i))[1]).max() for i in (1, 2, 3)]
        self.assertLess(max(peaks) / min(peaks), 1.10)

    def test_door_length(self):
        rate, x = read(os.path.join(AUDIO, "door.wav"))
        self.assertAlmostEqual(len(x) / rate, 0.45, delta=0.03)
        # swish peaks at the start
        self.assertLess(np.argmax(np.abs(x)) / rate, 0.1)

    def test_deterministic(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            generate_audio.generate(a)
            generate_audio.generate(b)
            for n in NAMES:
                ha = sha(os.path.join(a, n + ".wav"))
                hb = sha(os.path.join(b, n + ".wav"))
                self.assertEqual(ha, hb, n)
                # and the committed file matches a fresh generation
                hc = sha(os.path.join(AUDIO, n + ".wav"))
                self.assertEqual(ha, hc, n + " (committed file is stale; rerun generate_audio.py)")


if __name__ == "__main__":
    unittest.main()
