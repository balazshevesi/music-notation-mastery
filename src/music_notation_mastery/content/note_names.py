"""Natural-note ranges and stable deck identifiers."""

DECK_NAME = "Music Notation Mastery::01 - Note names"
# Keep these IDs and note GUID inputs stable across rebuilds.
CLEFS = {
    "treble": {
        "staff": 1, "deck_id": 1715014201, "extended_deck_id": 1715014203,
        "core_pitches": "C4 D4 E4 F4 G4 A4 B4 C5 D5 E5 F5 G5 A5 B5 C6".split(),
        "pitches": "C3 D3 E3 F3 G3 A3 B3 C4 D4 E4 F4 G4 A4 B4 C5 D5 E5 F5 G5 A5 B5 C6".split(),
    },
    "bass": {
        "staff": 2, "deck_id": 1715014202, "extended_deck_id": 1715014204,
        "core_pitches": "C2 D2 E2 F2 G2 A2 B2 C3 D3 E3 F3 G3 A3 B3 C4".split(),
        "pitches": "C1 D1 E1 F1 G1 A1 B1 C2 D2 E2 F2 G2 A2 B2 C3 D3 E3 F3 G3 A3 B3 C4 D4 E4 F4 G4 A4 B4 C5".split(),
    },
}
