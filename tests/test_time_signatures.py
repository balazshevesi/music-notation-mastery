import unittest
import xml.etree.ElementTree as ET

from music_notation_mastery.content.time_signatures import CARDS
from music_notation_mastery.notation import time_signature_musicxml


class TimeSignatureTests(unittest.TestCase):
    def test_meters_and_grouping(self):
        self.assertEqual(len({card["id"] for card in CARDS}), 6)
        for card in CARDS:
            beats, unit = card["meter"]
            root = ET.fromstring(time_signature_musicxml(card["meter"], grouped=card["grouped"]))
            self.assertEqual(root.findtext(".//beats"), str(beats))
            self.assertEqual(root.findtext(".//beat-type"), str(unit))
            notes = root.findall(".//note")
            self.assertEqual(sum(int(note.findtext("duration")) for note in notes), beats * 8 // unit)
            if card["grouped"]:
                expected = (["begin", "end"] * 3 if unit == 4
                            else ["begin", "continue", "end"] * 2)
                self.assertEqual([note.findtext("beam") for note in notes], expected)
                self.assertEqual([note.findtext("type") for note in notes], ["eighth"] * 6)
            else:
                self.assertEqual(len(notes), 1)
                self.assertEqual(notes[0].get("print-object"), "no")

    def test_invalid_meter_rejected(self):
        with self.assertRaises(ValueError):
            time_signature_musicxml((5, 4))
        with self.assertRaises(ValueError):
            time_signature_musicxml((2, 4), grouped=True)
