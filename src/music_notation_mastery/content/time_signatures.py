"""Meter recognition and the grouping difference between 3/4 and 6/8."""

DECK_NAME = "Music Notation Mastery::03 - Time signatures"
DECK_ID = 1715014401

CARDS = [
    {
        "id": f"signature-{beats}-4",
        "meter": (beats, 4),
        "grouped": False,
        "prompt": "How many beats are in each bar, which note gets one beat, and how do you count?",
        "answer": f"{beats}/4: {beats} quarter-note beats per bar. "
                  f"Count {'–'.join(str(n) for n in range(1, beats + 1))}. "
                  "The top number gives the number of beats; the bottom 4 means a quarter note gets one beat.",
    }
    for beats in (2, 3, 4)
]
CARDS.append({
    "id": "signature-6-8",
    "meter": (6, 8),
    "grouped": False,
    "prompt": "How is this meter usually felt and counted? Which note gets one main beat?",
    "answer": "6/8 is usually felt as two main beats per bar. A dotted quarter gets one main beat, "
              "divided into three eighth notes. Count ONE-la-li TWO-la-li. "
              "The 6 indicates six eighth notes per bar, not six main beats; the 8 identifies the eighth-note unit.",
})
for beats, unit, grouping, count in [
    (3, 4, "three groups of two eighth notes: three quarter-note beats", "1-and 2-and 3-and"),
    (6, 8, "two groups of three eighth notes: two dotted-quarter beats", "ONE-la-li TWO-la-li"),
]:
    CARDS.append({
        "id": f"grouping-{beats}-{unit}",
        "meter": (beats, unit),
        "grouped": True,
        "prompt": "How are these six eighth notes grouped into main beats, and how do you count them?",
        "answer": f"{beats}/{unit} has {grouping}. Count {count}. "
                  "Both 3/4 and 6/8 contain six eighth notes per bar, but their beat grouping differs.",
    })
