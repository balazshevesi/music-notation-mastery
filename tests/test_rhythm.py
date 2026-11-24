import unittest
import xml.etree.ElementTree as ET

from music_notation_mastery.content.rhythm import CARDS
from music_notation_mastery.notation import rhythm_musicxml


class RhythmTests(unittest.TestCase):
    def test_values(self):
        self.assertEqual(len({card["id"] for card in CARDS}), 20)
        expected = {"whole": 16, "half": 8, "quarter": 4, "eighth": 2, "16th": 1}
        for card in CARDS:
            root = ET.fromstring(rhythm_musicxml(card["events"], dotted=card.get("dotted", False), tied=card.get("tied", False)))
            notes = root.findall(".//note")
            self.assertEqual(root.findtext(".//divisions"), "8")
            self.assertEqual(root.findtext(".//beats"), "4")
            self.assertEqual(root.findtext(".//beat-type"), "4")
            self.assertEqual(len(notes), len(card["events"]))
            for note, (value, rest) in zip(notes, card["events"]):
                self.assertEqual(int(note.findtext("duration")), expected[value] * (3 if card.get("dotted") else 2))
                self.assertEqual(len(note.findall("dot")), int(card.get("dotted", False)))
                self.assertEqual(note.findtext("type"), value)
                self.assertEqual(note.find("rest") is not None, rest)

            if card.get("tied"):
                self.assertEqual([n.find("tie").get("type") for n in notes], ["start", "stop"])
                self.assertEqual([n.find("notations/tied").get("type") for n in notes], ["start", "stop"])
                self.assertEqual([n.findtext("pitch/step") for n in notes], ["C", "C"])
            else:
                self.assertFalse(root.findall(".//tie"))

    def test_tied_rests_rejected(self):
        with self.assertRaises(ValueError):
            rhythm_musicxml([("quarter", False), ("quarter", True)], tied=True)

    def test_multiple_symbols_rejected(self):
        with self.assertRaises(ValueError):
            rhythm_musicxml([("quarter", False), ("quarter", True)])
