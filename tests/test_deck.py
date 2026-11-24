import json
from pathlib import Path
import sqlite3
import struct
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from build_deck import CLEFS, ROOT, create_package, musicxml


class DeckTests(unittest.TestCase):
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

    def test_rendered_package(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            jobs = [
                {"filename": f"mnm-note-{clef}-{pitch}.png", "xml": musicxml(clef, pitch)}
                for clef, settings in CLEFS.items() for pitch in settings["pitches"]
            ]
            subprocess.run(
                ["node", str(ROOT / "renderer" / "render_notes.mjs"), str(folder)],
                input=json.dumps(jobs), text=True, check=True,
            )
            package = create_package(folder)
            archive = folder / "deck.apkg"
            package.write_to_file(str(archive))
            with ZipFile(archive) as zip_file:
                media = json.loads(zip_file.read("media"))
                self.assertEqual(set(media.values()), {job["filename"] for job in jobs})
                for entry in media:
                    png = zip_file.read(entry)
                    self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
                    width, height = struct.unpack(">II", png[16:24])
                    self.assertGreater(width, 100)
                    self.assertGreater(height, 100)
                zip_file.extract("collection.anki2", folder)
            with sqlite3.connect(folder / "collection.anki2") as db:
                self.assertEqual(db.execute("SELECT count(*) FROM notes").fetchone()[0], 51)
                self.assertEqual(db.execute("SELECT count(*) FROM cards").fetchone()[0], 51)
                self.assertEqual(db.execute("SELECT count(DISTINCT guid) FROM notes").fetchone()[0], 51)
                counts = db.execute("SELECT did, count(*) FROM cards GROUP BY did").fetchall()
                self.assertEqual(dict(counts), {1715014201: 15, 1715014202: 15, 1715014203: 7, 1715014204: 14})
                for fields, tags, deck_id in db.execute(
                    "SELECT notes.flds, notes.tags, cards.did FROM notes JOIN cards ON cards.nid = notes.id"
                ):
                    key, notation, letter, pitch, clef = fields.split("\x1f")
                    self.assertIn(f'{key}.png', media.values())
                    self.assertIn(f'src="{key}.png"', notation)
                    self.assertEqual(letter, pitch[0])
                    self.assertIn(pitch, CLEFS[clef.lower()]["pitches"])
                    core = (clef == "Treble" and int(pitch[1:]) >= 4) or (
                        clef == "Bass" and (int(pitch[1:]) in (2, 3) or pitch == "C4")
                    )
                    self.assertIn("core" if core else "extended", tags.split())
                    expected_id = {("Treble", True): 1715014201, ("Bass", True): 1715014202,
                                   ("Treble", False): 1715014203, ("Bass", False): 1715014204}
                    self.assertEqual(deck_id, expected_id[clef, core])
            first = [note.guid for deck in package.decks for note in deck.notes]
            second = [note.guid for deck in create_package(folder).decks for note in deck.notes]
            self.assertEqual(first, second)

    def test_missing_media_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                create_package(Path(directory))


if __name__ == "__main__":
    unittest.main()
