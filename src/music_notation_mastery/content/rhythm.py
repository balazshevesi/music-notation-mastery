"""Beginner note and rest values in 4/4."""

DECK_NAME = "Music Notation Mastery::02 - Rhythm"
DECK_IDS = {"values": 1715014301}

# Durations use four divisions per quarter-note beat.
VALUES = {
    "whole": (16, "4 beats"),
    "half": (8, "2 beats"),
    "quarter": (4, "1 beat"),
    "eighth": (2, "½ beat"),
    "16th": (1, "¼ beat"),
}

CARDS = [
    {
        "id": f"{kind}-{value}",
        "group": "values",
        "events": [(value, kind == "rest")],
        "prompt": "What is this called, and how many beats does it last in 4/4?",
        "answer": f"{'Sixteenth' if value == '16th' else value.title()} {kind} — {beats}.",
    }
    for value, (_, beats) in VALUES.items()
    for kind in ("note", "rest")
]

# 4302 was used by the removed clapping deck; do not reuse it.
DECK_IDS.update({"dotted": 1715014303, "ties": 1715014304})

for value, beats, calculation in [
    ("half", "3", "2 + 1"),
    ("quarter", "1½", "1 + ½"),
    ("eighth", "¾", "½ + ¼"),
]:
    for kind in ("note", "rest"):
        CARDS.append({
            "id": f"dotted-{kind}-{value}",
            "group": "dotted",
            "events": [(value, kind == "rest")],
            "dotted": True,
            "prompt": "Name this dotted symbol and its duration in 4/4.",
            "answer": f"Dotted {value} {kind} — {beats} beats ({calculation}). "
                      "A dot adds half the original duration.",
        })

for first, second, beats, calculation in [
    ("half", "half", "4", "2 + 2"),
    ("half", "quarter", "3", "2 + 1"),
    ("quarter", "quarter", "2", "1 + 1"),
    ("eighth", "eighth", "1", "½ + ½"),
]:
    CARDS.append({
        "id": f"tie-{first}-{second}",
        "group": "ties",
        "events": [(first, False), (second, False)],
        "tied": True,
        "prompt": "How many beats does this tied note last in 4/4, and how is it played?",
        "answer": f"{beats} {'beat' if beats == '1' else 'beats'} ({calculation}). "
                  "Play once and hold for the combined duration; do not play the second note again. "
                  "A tie joins notes of the same pitch.",
    })
