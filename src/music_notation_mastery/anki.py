"""Anki model, note identifiers, and package assembly."""

from pathlib import Path
from hashlib import sha256

import genanki

from .audio import AUDIO_DIR

from .content.note_names import CLEFS, DECK_ID, DECK_NAME


AUDIO_CREDIT = (
    '<p>Audio: Salamander Grand Piano V3 by Alexander Holm. '
    '<a href="https://github.com/sfzinstruments/SalamanderGrandPiano">Source</a> · '
    '<a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>. '
    'Trimmed, faded, converted to MP3 and repitched where needed.</p>'
)


MODEL = genanki.Model(
    1715014200,
    "Music Notation Mastery - Note identification",
    fields=[{"name": name} for name in ("ID", "Notation", "Letter", "Pitch", "Clef", "Piano", "Sound")],
    templates=[{
        "name": "Name the note",
        "qfmt": '<p>Name this note.</p><div class="notation pitch-notation">{{Notation}}</div>',
        "afmt": '{{FrontSide}}<hr id="answer"><div class="letter">{{Letter}}</div>'
                '<p>{{Pitch}} · {{Clef}} clef</p><div>{{Sound}}</div><div class="piano">{{Piano}}</div>',
    }],
    css="""
        .card { font-family: Arial, sans-serif; text-align: center; font-size: 22px; }
        .notation { background: white; border-radius: 12px; padding: 16px;
                    max-width: 360px; margin: 24px auto; }
        .pitch-notation { padding: 4px 16px; margin: 8px auto; }
        .notation img { width: 100%; height: auto; display: block; }
        .piano { background: white; max-width: 600px; margin: 12px auto; }
        .piano img { display: block; width: 100%; height: auto; }
        .letter { font-size: 48px; font-weight: bold; }
        #answer { border: 0; border-top: 1px solid #aaa; margin: 24px 0; }
    """,
)


def create_package(media_dir: Path) -> genanki.Package:
    deck = genanki.Deck(DECK_ID, DECK_NAME, description=AUDIO_CREDIT)
    decks = [deck]
    media = []
    for clef, settings in CLEFS.items():
        for pitch in settings["pitches"]:
            key = f"mnm-note-{clef}-{pitch}"
            filename = f"{key}.png"
            image = media_dir / filename
            if not image.is_file():
                raise FileNotFoundError(f"Missing rendered notation: {image}")
            piano = media_dir / f"mnm-piano-{pitch}.png"
            if not piano.is_file():
                raise FileNotFoundError(f"Missing piano image: {piano}")
            sound = AUDIO_DIR / f"mnm-audio-{pitch}.mp3"
            if not sound.is_file():
                raise FileNotFoundError(f"Missing piano audio: {sound}")
            group = "core" if pitch in settings["core_pitches"] else "extended"
            deck.add_note(genanki.Note(
                model=MODEL,
                guid=genanki.guid_for("music-notation-mastery", "note-names", clef, pitch),
                fields=[key, f'<img src="{filename}" alt="Note on a grand staff">',
                        pitch[0], pitch, clef.title(),
                        f'<img src="{piano.name}" alt="{pitch} highlighted on a piano keyboard">', f"[sound:{sound.name}]"],
                tags=["pitch", clef, group, f"note_{pitch[0]}", f"octave_{pitch[1:]}"],
            ))
            media.append(str(image))
            if str(piano) not in media:
                media.append(str(piano))
            if str(sound) not in media:
                media.append(str(sound))
    # A changed image must change the note field, not just the packaged file bytes.
    versioned_media = []
    replacements = {}
    for filename in media:
        source = Path(filename)
        data = source.read_bytes()
        versioned = media_dir / f"{source.stem}-{sha256(data).hexdigest()[:16]}{source.suffix}"
        versioned.write_bytes(data)
        replacements[f'src="{source.name}"'] = f'src="{versioned.name}"'
        replacements[f"[sound:{source.name}]"] = f"[sound:{versioned.name}]"
        versioned_media.append(str(versioned))
    for deck in decks:
        for note in deck.notes:
            for index, field in enumerate(note.fields):
                for original, replacement in replacements.items():
                    field = field.replace(original, replacement)
                note.fields[index] = field
    return genanki.Package(decks, media_files=versioned_media)


