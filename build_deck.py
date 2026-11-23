"""Build Part 1 with `uv run build_deck.py`."""

import json
from pathlib import Path
import subprocess
import tempfile

import genanki


ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
DECK_NAME = "Music Notation Mastery::01 - Note names"
# Keep these IDs and note GUID inputs stable across rebuilds.
CLEFS = {
    "treble": {
        "staff": 1, "deck_id": 1715014201,
        "pitches": "C4 D4 E4 F4 G4 A4 B4 C5 D5 E5 F5 G5 A5".split(),
    },
    "bass": {
        "staff": 2, "deck_id": 1715014202,
        "pitches": "E2 F2 G2 A2 B2 C3 D3 E3 F3 G3 A3 B3 C4".split(),
    },
}
MODEL = genanki.Model(
    1715014200,
    "Music Notation Mastery - Note identification",
    fields=[{"name": name} for name in ("ID", "Notation", "Letter", "Pitch", "Clef")],
    templates=[{
        "name": "Name the note",
        "qfmt": '<p>Name this note.</p><div class="notation">{{Notation}}</div>',
        "afmt": '{{FrontSide}}<hr id="answer"><div class="letter">{{Letter}}</div>'
                '<p>{{Pitch}} · {{Clef}} clef</p>',
    }],
    css="""
        .card { font-family: Arial, sans-serif; text-align: center; font-size: 22px; }
        .notation { background: white; border-radius: 12px; padding: 16px;
                    max-width: 360px; margin: 24px auto; }
        .notation img { width: 100%; height: auto; display: block; }
        .letter { font-size: 48px; font-weight: bold; }
        #answer { border: 0; border-top: 1px solid #aaa; margin: 24px 0; }
    """,
)


def musicxml(clef: str, pitch: str) -> str:
    settings = CLEFS[clef]
    if pitch not in settings["pitches"]:
        raise ValueError(f"Unsupported {clef} pitch: {pitch}")
    notes = []
    for staff in (1, 2):
        if staff == settings["staff"]:
            note = f"<note><pitch><step>{pitch[0]}</step><octave>{pitch[1:]}</octave></pitch>"
        else:
            # Keep the other staff present without introducing a visible rest.
            note = '<note print-object="no"><rest/>'
        notes.append(f"{note}<duration>4</duration><voice>{staff}</voice>"
                     f"<type>whole</type><staff>{staff}</staff></note>")
    staff_notes = "<backup><duration>4</duration></backup>".join(notes)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<score-partwise version="4.0">
  <part-list><score-part id="P1"><part-name>Note</part-name></score-part></part-list>
  <part id="P1"><measure number="1">
    <attributes>
      <divisions>1</divisions>
      <key><fifths>0</fifths></key>
      <time><beats>4</beats><beat-type>4</beat-type></time>
      <staves>2</staves>
      <clef number="1"><sign>G</sign><line>2</line></clef>
      <clef number="2"><sign>F</sign><line>4</line></clef>
    </attributes>
    {staff_notes}
    <barline location="right"><bar-style>none</bar-style></barline>
  </measure></part>
</score-partwise>"""


def create_package(media_dir: Path) -> genanki.Package:
    decks = []
    media = []
    for clef, settings in CLEFS.items():
        deck = genanki.Deck(settings["deck_id"], f"{DECK_NAME}::{clef.title()} clef")
        for pitch in settings["pitches"]:
            key = f"mnm-note-{clef}-{pitch}"
            filename = f"{key}.png"
            image = media_dir / filename
            if not image.is_file():
                raise FileNotFoundError(f"Missing rendered notation: {image}")
            deck.add_note(genanki.Note(
                model=MODEL,
                guid=genanki.guid_for("music-notation-mastery", "note-names", clef, pitch),
                fields=[key, f'<img src="{filename}" alt="Note on a grand staff">',
                        pitch[0], pitch, clef.title()],
                tags=["part_01", "note_names", clef],
            ))
            media.append(str(image))
        decks.append(deck)
    return genanki.Package(decks, media_files=media)


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    jobs = [
        {"filename": f"mnm-note-{clef}-{pitch}.png", "xml": musicxml(clef, pitch)}
        for clef, settings in CLEFS.items() for pitch in settings["pitches"]
    ]
    media_dir = BUILD / "media"
    subprocess.run(
        ["node", str(ROOT / "render_notes.mjs"), str(media_dir)],
        input=json.dumps(jobs), text=True, check=True, cwd=ROOT,
    )
    destination = BUILD / "music-notation-mastery.apkg"
    # Finish writing before replacing a previously built deck.
    with tempfile.TemporaryDirectory(dir=BUILD) as temporary:
        package_path = Path(temporary) / destination.name
        create_package(media_dir).write_to_file(str(package_path))
        package_path.replace(destination)
    print(f"Created {destination} ({len(jobs)} cards)")


if __name__ == "__main__":
    main()
