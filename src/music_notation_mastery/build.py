"""Coordinate notation rendering and Anki packaging from this checkout."""

import json
from pathlib import Path
import subprocess
import tempfile

from .anki import create_package
from .content.note_names import CLEFS
from .notation import musicxml, rhythm_musicxml
from .content.rhythm import CARDS


ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"


def build_deck() -> None:
    BUILD.mkdir(exist_ok=True)
    jobs = [
        {"filename": f"mnm-note-{clef}-{pitch}.png", "xml": musicxml(clef, pitch)}
        for clef, settings in CLEFS.items() for pitch in settings["pitches"]
    ]
    jobs.extend(
        {"filename": f"mnm-rhythm-{card['id']}.png",
         "xml": rhythm_musicxml(card["events"], dotted=card.get("dotted", False), tied=card.get("tied", False))}
        for card in CARDS
    )
    media_dir = BUILD / "media"
    subprocess.run(
        ["node", str(ROOT / "renderer" / "render_notes.mjs"), str(media_dir)],
        input=json.dumps(jobs), text=True, check=True, cwd=ROOT,
    )
    destination = BUILD / "music-notation-mastery.apkg"
    # Finish writing before replacing a previously built deck.
    with tempfile.TemporaryDirectory(dir=BUILD) as temporary:
        package_path = Path(temporary) / destination.name
        create_package(media_dir).write_to_file(str(package_path))
        package_path.replace(destination)
    print(f"Created {destination} ({len(jobs)} cards)")

