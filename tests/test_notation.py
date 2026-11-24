import unittest
import xml.etree.ElementTree as ET

from music_notation_mastery.content.note_names import CLEFS
from music_notation_mastery.notation import musicxml


class NotationTests(unittest.TestCase):
    def test_pitches_and_musicxml(self):
        expected = {
            "treble": ("1", "C3 D3 E3 F3 G3 A3 B3 C4 D4 E4 F4 G4 A4 B4 C5 D5 E5 F5 G5 A5 B5 C6".split()),
            "bass": ("2", "C1 D1 E1 F1 G1 A1 B1 C2 D2 E2 F2 G2 A2 B2 C3 D3 E3 F3 G3 A3 B3 C4 D4 E4 F4 G4 A4 B4 C5".split()),
        }
        for clef, (staff, pitches) in expected.items():
            self.assertEqual(CLEFS[clef]["pitches"], pitches)
            for pitch in pitches:
                root = ET.fromstring(musicxml(clef, pitch))
                self.assertEqual(root.findtext(".//staves"), "2")
                self.assertEqual(
                    [(item.get("number"), item.findtext("sign"), item.findtext("line"))
                     for item in root.findall(".//clef")],
                    [("1", "G", "2"), ("2", "F", "4")],
                )
                self.assertEqual(root.findtext(".//pitch/step"), pitch[0])
                self.assertEqual(root.findtext(".//pitch/octave"), pitch[1:])
                pitched_notes = root.findall(".//note[pitch]")
                self.assertEqual(len(pitched_notes), 1)
                self.assertEqual(pitched_notes[0].findtext("staff"), staff)
                rests = root.findall(".//note[rest]")
                self.assertEqual(len(rests), 1)
                self.assertEqual(rests[0].get("print-object"), "no")
                self.assertNotEqual(rests[0].findtext("staff"), staff)
                self.assertEqual(root.findtext(".//backup/duration"), "4")
                self.assertIsNone(root.find(".//alter"))

