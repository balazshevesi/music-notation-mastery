"""Coordinate notation rendering and Anki packaging from this checkout."""

import json
from pathlib import Path
import subprocess
import tempfile

from .anki import create_package
from .content.note_names import CLEFS
from .notation import musicxml


ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build"


def build_deck() -> None:
    BUILD.mkdir(exist_ok=True)
    jobs = [
        {"filename": f"mnm-note-{clef}-{pitch}.png", "xml": musicxml(clef, pitch)}
        for clef, settings in CLEFS.items() for pitch in settings["pitches"]
    ]
    media_dir = BUILD / "media"
    subprocess.run(
        ["node", str(ROOT / "renderer" / "render_notes.mjs"), str(media_dir)],
        input=json.dumps(jobs), text=True, check=True, cwd=ROOT,
    )
    subprocess.run(
        ["node", str(ROOT / "renderer" / "render_pianos.mjs"), str(media_dir)],
        input=json.dumps(sorted({pitch for settings in CLEFS.values() for pitch in settings["pitches"]})),
        text=True, check=True,
    )
    destination = BUILD / "music-notation-mastery.apkg"
    # Finish writing before replacing a previously built deck.
    with tempfile.TemporaryDirectory(dir=BUILD) as temporary:
        package_path = Path(temporary) / destination.name
        create_package(media_dir).write_to_file(str(package_path))
        package_path.replace(destination)
    print(f"Created {destination} ({len(jobs)} cards)")

