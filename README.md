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
scientific pitch name (middle C is C4), clef, and a piano graphic highlighting the
exact key on an 88-key keyboard with a larger close-up. The answer also plays
a three-second piano MP3, with Anki’s replay control. Focus on the letter first;
the octave is included as a reference. There are no accidentals or time signatures.
All subdecks live under `Music Notation Mastery::01 - Note names`, leaving room
for additional parts later.

## Part 2: Rhythm

20 cards across three subdecks:

- **Values (10):** whole, half, quarter, eighth, and sixteenth
notes and rests.
- **Dotted (6):** dotted half, quarter, and eighth notes and rests.
- **Ties (4):** two notes of the same pitch joined into one held sound.

Identify each duration in 4/4, where a quarter note is worth one beat.
Answers explain the dot's extra half-value and how tied durations add together.

Each card shows notation on a staff, with a written answer.
Edit rhythm content in `src/music_notation_mastery/content/rhythm.py`.

The complete package contains **77 cards**; existing note-name cards retain their IDs.

## Part 3: Time signatures

6 recognition cards:

- **2/4, 3/4, 4/4:** beats per bar, the quarter-note beat, and counting.
- **6/8:** two main dotted-quarter beats, each divided into three eighth notes.
- **3/4 versus 6/8:** six eighth notes explicitly beamed in three pairs or two
  groups of three, with written counting guidance.

Edit these cards in `src/music_notation_mastery/content/time_signatures.py`.
These cards share the rhythm question/answer template and use separate stable IDs.

## Build

Install uv and Node.js 22 or newer (with npm), then run from this directory:

```sh
uv sync --locked
npm ci --prefix renderer
uv run build
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
node --test tests/test_pianos.mjs
```

The checks render all 77 notation images and 36 shared piano images and inspect the packaged database and media,
including pitches, clefs, card counts, media references, and stable note IDs.

## Project structure

- `src/music_notation_mastery/content/`: learning content; currently natural-note ranges.
- `src/music_notation_mastery/notation.py`: MusicXML generation.
- `src/music_notation_mastery/anki.py`: card templates, stable note IDs, and packaging.
- `src/music_notation_mastery/build.py`: rendering and package build orchestration.
- `src/music_notation_mastery/cli.py`: the `build` command.
- `renderer/`: Node.js notation renderer and its dependencies.
- `tests/`: notation and package checks.
- `build/`: generated media and deck files (ignored by Git).

Run builds from this source checkout; the Python build uses the renderer beside
`src/`. Add new lessons under `content/` as they are introduced.

Piano answer graphics are generated offline by `renderer/render_pianos.mjs` using
[piano-chart](https://github.com/ailon/piano-chart), with svgdom providing SVG layout
and canvas producing PNGs. No runtime JavaScript or network is required in Anki.
The note-name model appends a `Piano` field while preserving existing field order
and note GUIDs. When reimporting, allow Anki to update the note type and templates
if prompted so the new answer field appears.

Packaged media filenames include a hash of their contents. When an image changes,
its filename and the note's image reference change together, allowing reimports
to update the graphic without changing the note GUID or its learning history.

## Piano audio

36 MP3 clips are bundled in `assets/audio/`, shared by the 51 note-name cards.
Playback is on the answer side only and works offline. Audio uses Anki's normal
playback preferences. Existing note GUIDs are preserved; the note type appends a
`Sound` field. Allow note and note-type updates when reimporting.

Source: **Salamander Grand Piano V3 by Alexander Holm**, licensed under
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
See `assets/audio/README.md` and `assets/audio/LICENSE.txt` for provenance and
license details. Attribution is also included in the note-name subdeck descriptions.
Clips use velocity layer 8, are repitched by at most one semitone where needed,
trimmed to three seconds, faded, mixed to mono, and encoded as 128 kbps MP3.

Normal builds use the bundled files. To regenerate them, install FFmpeg and run:

```sh
uv run python -m music_notation_mastery.audio
```

The first regeneration downloads the required original FLACs into
`build/audio-sources/`; subsequent regenerations reuse them.
