import json
from hashlib import sha256
from pathlib import Path
import sqlite3
import struct
import subprocess
import tempfile
import unittest
from zipfile import ZipFile

from music_notation_mastery.anki import create_package, MODEL
from music_notation_mastery.build import ROOT
from music_notation_mastery.content.note_names import CLEFS
from music_notation_mastery.notation import musicxml, rhythm_musicxml, time_signature_musicxml
from music_notation_mastery.content.rhythm import CARDS
from music_notation_mastery.content.time_signatures import CARDS as METER_CARDS


class DeckTests(unittest.TestCase):
    def test_rendered_package(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            jobs = [
                {"filename": f"mnm-note-{clef}-{pitch}.png", "xml": musicxml(clef, pitch)}
                for clef, settings in CLEFS.items() for pitch in settings["pitches"]
            ]
            jobs.extend(
                {"filename": f"mnm-rhythm-{card['id']}.png",
                 "xml": rhythm_musicxml(card["events"], dotted=card.get("dotted", False), tied=card.get("tied", False))}
                for card in CARDS
            )
            jobs.extend(
                {"filename": f"mnm-meter-{card['id']}.png",
                 "xml": time_signature_musicxml(card["meter"], grouped=card["grouped"]),
                 "showTimeSignature": True}
                for card in METER_CARDS
            )
            subprocess.run(
                ["node", str(ROOT / "renderer" / "render_notes.mjs"), str(folder)],
                input=json.dumps(jobs), text=True, check=True,
            )
            subprocess.run(
                ["node", str(ROOT / "renderer" / "render_pianos.mjs"), str(folder)],
                input=json.dumps(sorted({pitch for settings in CLEFS.values() for pitch in settings["pitches"]})),
                text=True, check=True,
            )
            def versioned(name):
                path = folder / name
                digest = sha256(path.read_bytes()).hexdigest()[:16]
                return f"{path.stem}-{digest}{path.suffix}"

            package = create_package(folder)
            archive = folder / "deck.apkg"
            package.write_to_file(str(archive))
            with ZipFile(archive) as zip_file:
                media = json.loads(zip_file.read("media"))
                self.assertEqual(set(media.values()), {versioned(job["filename"]) for job in jobs} |
                                 {versioned(f"mnm-piano-{pitch}.png") for settings in CLEFS.values() for pitch in settings["pitches"]})
                rhythm_sizes = set()
                for entry in media:
                    png = zip_file.read(entry)
                    self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
                    width, height = struct.unpack(">II", png[16:24])
                    self.assertGreater(width, 300)
                    self.assertGreater(height, 300)
                    if media[entry].startswith("mnm-rhythm-"):
                        rhythm_sizes.add((width, height))
                self.assertEqual(len(rhythm_sizes), 1)
                zip_file.extract("collection.anki2", folder)
            with sqlite3.connect(folder / "collection.anki2") as db:
                self.assertEqual(db.execute("SELECT count(*) FROM notes").fetchone()[0], 77)
                self.assertEqual(db.execute("SELECT count(*) FROM cards").fetchone()[0], 77)
                self.assertEqual(db.execute("SELECT count(DISTINCT guid) FROM notes").fetchone()[0], 77)
                counts = db.execute("SELECT did, count(*) FROM cards GROUP BY did").fetchall()
                self.assertEqual(dict(counts), {1715014201: 15, 1715014202: 15, 1715014203: 7, 1715014204: 14, 1715014301: 10, 1715014303: 6, 1715014304: 4, 1715014401: 6})
                for fields, tags, deck_id in db.execute(
                    "SELECT notes.flds, notes.tags, cards.did FROM notes JOIN cards ON cards.nid = notes.id"
                ):
                    if deck_id == 1715014401:
                        key, prompt, notation, answer = fields.split("\x1f")
                        self.assertIn(versioned(f"{key}.png"), media.values())
                        self.assertIn(f'src="{versioned(f"{key}.png")}"' , notation)
                        self.assertTrue(prompt and answer)
                        self.assertIn("time_signatures", tags.split())
                        continue
                    if deck_id in (1715014301, 1715014303, 1715014304):
                        key, prompt, notation, answer = fields.split("\x1f")
                        self.assertIn(versioned(f"{key}.png"), media.values())
                        self.assertIn(f'src="{versioned(f"{key}.png")}"' , notation)
                        self.assertIn("4/4", prompt)
                        self.assertTrue(answer)
                        self.assertIn("rhythm", tags.split())
                        continue
                    key, notation, letter, pitch, clef, piano = fields.split("\x1f")
                    self.assertIn(versioned(f"{key}.png"), media.values())
                    self.assertIn(f'src="{versioned(f"{key}.png")}"' , notation)
                    self.assertIn(f'src="{versioned(f"mnm-piano-{pitch}.png")}"' , piano)
                    self.assertIn(versioned(f"mnm-piano-{pitch}.png"), media.values())
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
            before = {note.guid: list(note.fields) for deck in package.decks for note in deck.notes}
            # Simulate revised media without changing the card's identity.
            piano = folder / "mnm-piano-C4.png"
            piano.write_bytes(piano.read_bytes() + b"revised")
            updated = create_package(folder)
            after = {note.guid: note.fields for deck in updated.decks for note in deck.notes}
            self.assertEqual(before.keys(), after.keys())
            changed = [guid for guid in before if before[guid] != after[guid]]
            self.assertEqual(len(changed), 2)  # C4 appears in both clefs.
            for guid in changed:
                self.assertEqual(before[guid][:-1], after[guid][:-1])
                self.assertIn(versioned("mnm-piano-C4.png"), after[guid][-1])

    def test_piano_is_answer_only(self):
        self.assertNotIn("{{Piano}}", MODEL.templates[0]["qfmt"])
        self.assertIn("{{Piano}}", MODEL.templates[0]["afmt"])

    def test_missing_media_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                create_package(Path(directory))


if __name__ == "__main__":
    unittest.main()
