# Piano audio attribution

Salamander Grand Piano V3 by Alexander Holm.
Source: https://github.com/sfzinstruments/SalamanderGrandPiano
Source revision: 3382bf9496bba2486f5ab0de55a264d1dfc38404
License: Creative Commons Attribution 3.0 Unported
https://creativecommons.org/licenses/by/3.0/

Derived from velocity layer 8. Notes not sampled directly are shifted by one
semitone from the nearest recording. Clips are trimmed to three seconds,
faded over the last half-second, mixed to mono and encoded as 128 kbps MP3.
These audio files retain their CC BY 3.0 license independently of the project code.

Regenerate with FFmpeg installed:
`uv run python -m music_notation_mastery.audio`

Original FLACs are cached under build/audio-sources; generated MP3s are bundled
here so normal deck builds and tests do not need network access or FFmpeg.
