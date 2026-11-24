"""Generate MusicXML for note identification and rhythm practice."""

from .content.note_names import CLEFS
from .content.rhythm import VALUES


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


def rhythm_musicxml(events: list[tuple[str, bool]], *, dotted: bool = False, tied: bool = False) -> str:
    """Render an isolated value or two tied notes of the same pitch."""
    if len(events) != (2 if tied else 1) or (tied and any(rest for _, rest in events)):
        raise ValueError("Expected one value or two tied notes, without tied rests")
    notes = []
    for index, (value, rest) in enumerate(events):
        symbol = "<rest/>" if rest else "<pitch><step>C</step><octave>5</octave></pitch>"
        duration = VALUES[value][0] * 2
        if dotted:
            duration = duration * 3 // 2
        tie_type = "start" if index == 0 else "stop"
        tie = f'<tie type="{tie_type}"/>' if tied else ""
        notation = f'<notations><tied type="{tie_type}"/></notations>' if tied else ""
        notes.append(
            f"<note>{symbol}<duration>{duration}</duration>{tie}"
            f"<type>{value}</type>{'<dot/>' if dotted else ''}{notation}</note>"
        )
    # Isolated values are deliberately incomplete bars, not full-measure rests.
    return f"""<?xml version="1.0" encoding="utf-8"?>
<score-partwise version="4.0">
  <part-list><score-part id="P1"><part-name>Rhythm</part-name></score-part></part-list>
  <part id="P1"><measure number="1" implicit="yes">
    <attributes>
      <divisions>8</divisions>
      <time><beats>4</beats><beat-type>4</beat-type></time>
      <clef><sign>G</sign><line>2</line></clef>
    </attributes>
    {''.join(notes)}
    <barline location="right"><bar-style>none</bar-style></barline>
  </measure></part>
</score-partwise>"""


def time_signature_musicxml(meter: tuple[int, int], *, grouped: bool = False) -> str:
    """Show a numeric signature or a complete bar with explicit eighth-note beams."""
    if meter not in ((2, 4), (3, 4), (4, 4), (6, 8)):
        raise ValueError(f"Unsupported meter: {meter}")
    if grouped and meter not in ((3, 4), (6, 8)):
        raise ValueError("Grouping comparisons use 3/4 or 6/8")
    beats, unit = meter
    if grouped:
        group_size = 2 if meter == (3, 4) else 3
        notes = []
        for index in range(6):
            position = index % group_size
            beam = "begin" if position == 0 else "end" if position == group_size - 1 else "continue"
            notes.append(
                "<note><pitch><step>C</step><octave>5</octave></pitch>"
                f'<duration>1</duration><type>eighth</type><beam number="1">{beam}</beam></note>'
            )
        content = "".join(notes)
    else:
        content = f'<note print-object="no"><rest measure="yes"/><duration>{beats * 8 // unit}</duration></note>'
    return f"""<?xml version="1.0" encoding="utf-8"?>
<score-partwise version="4.0">
  <part-list><score-part id="P1"><part-name>Meter</part-name></score-part></part-list>
  <part id="P1"><measure number="1">
    <attributes>
      <divisions>2</divisions>
      <time symbol="normal"><beats>{beats}</beats><beat-type>{unit}</beat-type></time>
      <clef><sign>G</sign><line>2</line></clef>
    </attributes>
    {content}
    <barline location="right"><bar-style>{'regular' if grouped else 'none'}</bar-style></barline>
  </measure></part>
</score-partwise>"""
