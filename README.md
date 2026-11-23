# Music Notation Mastery

An Anki deck generated with Python, managed by [uv](https://docs.astral.sh/uv/).
[OpenSheetMusicDisplay](https://github.com/opensheetmusicdisplay/opensheetmusicdisplay)
renders the notation as PNGs; [genanki](https://github.com/kerrickstaley/genanki)
bundles the cards and images into an `.apkg` file. Cards work offline.

## Part 1: Note names

26 cards, one for each natural note in these ranges, including ledger lines:

| Subdeck | Range | Cards |
| --- | --- | --- |
| Treble clef | C4–A5 | 13 |
| Bass clef | E2–C4 | 13 |

The front shows a grand staff (treble above bass) with a single whole note on
the staff being tested; the other staff stays empty. The answer shows the letter,
scientific pitch name (middle C is C4), and clef. Focus on the letter first;
the octave is included as a reference. There are no accidentals or time signatures.
Both subdecks live under `Music Notation Mastery::01 - Note names`, leaving room
for additional parts later.

## Build

Install uv and Node.js 22 or newer (with npm), then run from this directory:

```sh
uv sync --locked
npm ci
uv run build_deck.py
```

Import `build/music-notation-mastery.apkg` in Anki using **File → Import**.
Individual images are in `build/media/`. Dependencies are downloaded at setup;
subsequent builds run locally without a browser or network access.

Python generates the MusicXML and assembles the deck. The small Node.js helper
in `render_notes.mjs` runs OpenSheetMusicDisplay using jsdom and canvas.

Deck/model IDs and note GUIDs remain stable across builds. Keep them unchanged
when editing content so Anki can recognize existing notes on reimport. To adjust
the ranges, edit the pitch lists in `CLEFS` in `build_deck.py` and their test
expectations. Reimporting a smaller deck does not remove older notes from Anki.

## Check

```sh
uv run python -m unittest discover -s tests -v
```

The checks render all 26 images and inspect the packaged database and media,
including pitches, clefs, card counts, media references, and stable note IDs.
