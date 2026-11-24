"""Anki model, note identifiers, and package assembly."""

from pathlib import Path

import genanki

from .content.note_names import CLEFS, DECK_NAME


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


def create_package(media_dir: Path) -> genanki.Package:
    decks = []
    media = []
    for clef, settings in CLEFS.items():
        groups = {
            "core": genanki.Deck(settings["deck_id"], f"{DECK_NAME}::{clef.title()} clef::Core"),
            "extended": genanki.Deck(settings["extended_deck_id"], f"{DECK_NAME}::{clef.title()} clef::Extended"),
        }
        for pitch in settings["pitches"]:
            key = f"mnm-note-{clef}-{pitch}"
            filename = f"{key}.png"
            image = media_dir / filename
            if not image.is_file():
                raise FileNotFoundError(f"Missing rendered notation: {image}")
            group = "core" if pitch in settings["core_pitches"] else "extended"
            groups[group].add_note(genanki.Note(
                model=MODEL,
                guid=genanki.guid_for("music-notation-mastery", "note-names", clef, pitch),
                fields=[key, f'<img src="{filename}" alt="Note on a grand staff">',
                        pitch[0], pitch, clef.title()],
                tags=["part_01", "note_names", clef, group],
            ))
            media.append(str(image))
        decks.extend(groups.values())
    return genanki.Package(decks, media_files=media)


