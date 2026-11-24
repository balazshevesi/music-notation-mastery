# Music Notation Mastery

An Anki deck generated with Python, managed by [uv](https://docs.astral.sh/uv/).
[OpenSheetMusicDisplay](https://github.com/opensheetmusicdisplay/opensheetmusicdisplay)
renders the notation as PNGs; [genanki](https://github.com/kerrickstaley/genanki)
bundles the cards and images into an `.apkg` file. Cards work offline.

## Part 1: Note names

51 cards, one for each natural note in these ranges, including ledger lines:

| Subdeck | Range | Cards |
| --- | --- | --- |
| Treble clef::Core | C4–C6 | 15 |
| Bass clef::Core | C2–C4 | 15 |
| Treble clef::Extended | C3–B3 | 7 |
| Bass clef::Extended | C1–B1 and D4–C5 | 14 |

Start with the 30 Core cards, then introduce the 21 Extended cards as needed.
Cards are also tagged `core` or `extended` for filtering in Anki.
Together these cover 36 unique natural pitches from C1 to C6 (five octaves),
with C3–C5 practiced in both clefs.

The front shows a grand staff (treble above bass) with a single whole note on
the staff being tested; the other staff stays empty. The answer shows the letter,
scientific pitch name (middle C is C4), and clef. Focus on the letter first;
the octave is included as a reference. There are no accidentals or time signatures.
All subdecks live under `Music Notation Mastery::01 - Note names`, leaving room
for additional parts later.

## Build

Install uv and Node.js 22 or newer (with npm), then run from this directory:

```sh
uv sync --locked
npm ci --prefix renderer
uv run build-deck
```

Import `build/music-notation-mastery.apkg` in Anki using **File → Import**.
Individual images are in `build/media/`. Dependencies are downloaded at setup;
subsequent builds run locally without a browser or network access.

Python generates the MusicXML and assembles the deck. The small Node.js helper
in `renderer/render_notes.mjs` runs OpenSheetMusicDisplay using jsdom and canvas.

Deck/model IDs and note GUIDs remain stable across builds. Keep them unchanged
when editing content so Anki can recognize existing notes on reimport. To adjust
the ranges, edit the pitch lists in `CLEFS` in `src/music_notation_mastery/content/note_names.py` and their test
expectations. Existing cards may retain their previous deck placement on reimport;
use the Anki browser to move those cards into the corresponding Core or Extended
subdeck if needed. Reimporting a smaller deck does not remove older notes from Anki.

## Check

```sh
uv run python -m unittest discover -s tests -v
```

The checks render all 51 images and inspect the packaged database and media,
including pitches, clefs, card counts, media references, and stable note IDs.

## Project structure

- `src/music_notation_mastery/content/`: learning content; currently natural-note ranges.
- `src/music_notation_mastery/notation.py`: MusicXML generation.
- `src/music_notation_mastery/anki.py`: card templates, stable note IDs, and packaging.
- `src/music_notation_mastery/build.py`: rendering and package build orchestration.
- `src/music_notation_mastery/cli.py`: the `build-deck` command.
- `renderer/`: Node.js notation renderer and its dependencies.
- `tests/`: notation and package checks.
- `build/`: generated media and deck files (ignored by Git).

Run builds from this source checkout; the Python build uses the renderer beside
`src/`. Add new lessons under `content/` as they are introduced.
