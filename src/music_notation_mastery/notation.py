"""Generate grand-staff MusicXML for note identification."""

from .content.note_names import CLEFS


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


