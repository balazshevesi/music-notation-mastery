"""Prepare bundled piano MP3s: uv run python -m music_notation_mastery.audio."""

from pathlib import Path
import subprocess
from urllib.request import urlopen

from .content.note_names import CLEFS

ROOT = Path(__file__).resolve().parents[2]
AUDIO_DIR = ROOT / "assets" / "audio"
SOURCE_REVISION = "3382bf9496bba2486f5ab0de55a264d1dfc38404"
SOURCE_URL = f"https://raw.githubusercontent.com/sfzinstruments/SalamanderGrandPiano/{SOURCE_REVISION}"
SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def sample_for(pitch: str) -> tuple[str, int]:
    midi = 12 * (int(pitch[1:]) + 1) + SEMITONES[pitch[0]]
    sampled = min(range(21, 109, 3), key=lambda key: abs(key - midi))
    name = {0: "C", 3: "D#", 6: "F#", 9: "A"}[sampled % 12]
    return f"{name}{sampled // 12 - 1}v8.flac", midi - sampled


def main() -> None:
    cache = ROOT / "build" / "audio-sources"
    cache.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    pitches = sorted({pitch for settings in CLEFS.values() for pitch in settings["pitches"]})
    for pitch in pitches:
        filename, shift = sample_for(pitch)
        source = cache / filename
        if not source.exists():
            url = f"{SOURCE_URL}/Samples/{filename.replace('#', '%23')}"
            with urlopen(url, timeout=60) as response:
                data = response.read()
            temporary = source.with_suffix(".download")
            temporary.write_bytes(data)
            temporary.replace(source)
        destination = AUDIO_DIR / f"mnm-audio-{pitch}.mp3"
        temporary = destination.with_suffix(".tmp.mp3")
        # Change playback rate by the semitone ratio, then return to 44.1 kHz.
        filters = (f"asetrate={48000 * 2 ** (shift / 12):.8f},aresample=44100,"
                   "atrim=duration=3,afade=t=out:st=2.5:d=0.5")
        subprocess.run([
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(source), "-af", filters, "-ac", "1",
            "-c:a", "libmp3lame", "-b:a", "128k",
            "-metadata", "artist=Alexander Holm",
            "-metadata", "album=Salamander Grand Piano V3",
            "-metadata", f"title={pitch}",
            "-metadata", "copyright=CC BY 3.0; trimmed, repitched where needed, faded, converted",
            str(temporary),
        ], check=True)
        temporary.replace(destination)
        print(f"Prepared {pitch}", flush=True)


if __name__ == "__main__":
    main()
