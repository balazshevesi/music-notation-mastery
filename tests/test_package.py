import json
from pathlib import Path
import sqlite3
import struct
import subprocess
import tempfile
import unittest
from zipfile import ZipFile

from music_notation_mastery.anki import create_package
from music_notation_mastery.build import ROOT
from music_notation_mastery.content.note_names import CLEFS
from music_notation_mastery.notation import musicxml


class DeckTests(unittest.TestCase):
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
