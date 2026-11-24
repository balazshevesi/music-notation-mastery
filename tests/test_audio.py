import unittest

from music_notation_mastery.audio import AUDIO_DIR, sample_for
from music_notation_mastery.content.note_names import CLEFS


class AudioTests(unittest.TestCase):
    def test_samples_and_octave_boundaries(self):
        self.assertEqual(sample_for("C1"), ("C1v8.flac", 0))
        self.assertEqual(sample_for("C4"), ("C4v8.flac", 0))
        self.assertEqual(sample_for("C6"), ("C6v8.flac", 0))
        self.assertEqual(sample_for("B3"), ("C4v8.flac", -1))
        self.assertEqual(sample_for("D4"), ("D#4v8.flac", -1))
        self.assertEqual(sample_for("E4"), ("D#4v8.flac", 1))

    def test_all_pitches_have_bundled_mp3(self):
        pitches = {pitch for settings in CLEFS.values() for pitch in settings["pitches"]}
        self.assertEqual(len(pitches), 36)
        for pitch in pitches:
            self.assertLessEqual(abs(sample_for(pitch)[1]), 1)
            data = (AUDIO_DIR / f"mnm-audio-{pitch}.mp3").read_bytes()
            self.assertTrue(data.startswith(b"ID3"))
            self.assertGreater(len(data), 10000)
