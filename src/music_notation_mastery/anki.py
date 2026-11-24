"""Anki model, note identifiers, and package assembly."""

from pathlib import Path
from hashlib import sha256

import genanki

from .audio import AUDIO_DIR

from .content.time_signatures import CARDS as METER_CARDS, DECK_ID as METER_DECK_ID, DECK_NAME as METER_DECK_NAME

from .content.note_names import CLEFS, DECK_NAME
from .content.rhythm import CARDS, DECK_IDS, DECK_NAME as RHYTHM_DECK_NAME


MODEL = genanki.Model(
    1715014200,
    "Music Notation Mastery - Note identification",
    fields=[{"name": name} for name in ("ID", "Notation", "Letter", "Pitch", "Clef", "Piano", "Sound")],
    templates=[{
        "name": "Name the note",
        "qfmt": '<p>Name this note.</p><div class="notation pitch-notation">{{Notation}}</div>',
        "afmt": '{{FrontSide}}<hr id="answer"><div class="letter">{{Letter}}</div>'
                '<p>{{Pitch}} · {{Clef}} clef</p><div>{{Sound}}</div><div class="piano">{{Piano}}</div>'
                '<details><summary>Audio credit</summary>Salamander Grand Piano V3 — Alexander Holm. '
                '<a href="https://github.com/sfzinstruments/SalamanderGrandPiano">Source</a> · '
                '<a href="https://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>. '
                'Trimmed, faded, converted to MP3 and repitched where needed.</details>',
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


RHYTHM_MODEL = genanki.Model(
    1715014300,
    "Music Notation Mastery - Rhythm",
    fields=[{"name": name} for name in ("ID", "Prompt", "Notation", "Answer")],
    templates=[{
        "name": "Read the rhythm",
        "qfmt": '<p>{{Prompt}}</p><div class="notation">{{Notation}}</div>',
        "afmt": '{{FrontSide}}<hr id="answer"><p>{{Answer}}</p>',
    }],
    css=MODEL.css,
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
            piano = media_dir / f"mnm-piano-{pitch}.png"
            if not piano.is_file():
                raise FileNotFoundError(f"Missing piano image: {piano}")
            sound = AUDIO_DIR / f"mnm-audio-{pitch}.mp3"
            if not sound.is_file():
                raise FileNotFoundError(f"Missing piano audio: {sound}")
            group = "core" if pitch in settings["core_pitches"] else "extended"
            groups[group].add_note(genanki.Note(
                model=MODEL,
                guid=genanki.guid_for("music-notation-mastery", "note-names", clef, pitch),
                fields=[key, f'<img src="{filename}" alt="Note on a grand staff">',
                        pitch[0], pitch, clef.title(),
                        f'<img src="{piano.name}" alt="{pitch} highlighted on a piano keyboard">', f"[sound:{sound.name}]"],
                tags=["part_01", "note_names", clef, group],
            ))
            media.append(str(image))
            if str(piano) not in media:
                media.append(str(piano))
            if str(sound) not in media:
                media.append(str(sound))
        decks.extend(groups.values())
    rhythm_decks = {
        group: genanki.Deck(deck_id, f"{RHYTHM_DECK_NAME}::{group.title()}")
        for group, deck_id in DECK_IDS.items()
    }
    for card in CARDS:
        key = f"mnm-rhythm-{card['id']}"
        image = media_dir / f"{key}.png"
        if not image.is_file():
            raise FileNotFoundError(f"Missing rendered notation: {image}")
        rhythm_decks[card["group"]].add_note(genanki.Note(
            model=RHYTHM_MODEL,
            guid=genanki.guid_for("music-notation-mastery", "rhythm", card["id"]),
            fields=[key, card["prompt"],
                    f'<img src="{image.name}" alt="Rhythm notation">', card["answer"]],
            tags=["part_02", "rhythm", card["group"], "time_4_4"],
        ))
        media.append(str(image))
    decks.extend(rhythm_decks.values())
    meter_deck = genanki.Deck(METER_DECK_ID, METER_DECK_NAME)
    for card in METER_CARDS:
        key = f"mnm-meter-{card['id']}"
        image = media_dir / f"{key}.png"
        if not image.is_file():
            raise FileNotFoundError(f"Missing rendered notation: {image}")
        meter_deck.add_note(genanki.Note(
            model=RHYTHM_MODEL,
            guid=genanki.guid_for("music-notation-mastery", "time-signatures", card["id"]),
            fields=[key, card["prompt"],
                    f'<img src="{image.name}" alt="Time signature notation">', card["answer"]],
            tags=["part_03", "time_signatures", f"time_{card['meter'][0]}_{card['meter'][1]}"],
        ))
        media.append(str(image))
    decks.append(meter_deck)
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


