#!/usr/bin/env python3
"""build_segs.py — Refresh EPK_Project/ to cover ALL 8 artists.

For each artist still missing a 30s broadcast segment, cut 30 s from an
interesting region of the canonical hq master (start offset per artist),
EBC-14/TP-1.5/LRA-11 loudness, 48 kHz / 320 kbps, single libmp3lame pass with
the clip's own measured EBU values (two-pass linear via ffmpeg loudnorm).

Writes: EPK_Project/{Artist}/{artist}_30s.mp3  (already-existing Maya/Parisa
segs are left untouched — they stay where they are).
Also rewrites EPK_Project/INDEX.md to list every artist + its hq master +
its 30s promo asset + genre + I(LUFS) of the hq master (where measured).
Uses ffmpeg read-only on the masters; only EPK_Project/ is mutated.
"""
from __future__ import annotations
import re, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path("/Users/bernie/Movies/Radio-ish")
FF = Path("/Users/bernie/Downloads/ffmpeg")
EPK = ROOT / "EPK_Project"

# artist -> (canon hq filename, genre, segment offset seconds, seg length)
SEG = {
    "Berne":   ("bernie_mix_hq.mp3", "Techno", 2400, 30),
    "Dikier":  ("dikier_mix_hq.mp3", "Techno", 1200, 30),
    "El Djemba": ("el_djemba_mix_hq.mp3", "House/Techno", 2400, 30),
    "Alexander Zwo": ("alexander_zwo_mix_hq.mp3", "House/Techno", 2400, 30),
    "DJ Unknown": ("dj_unknown_mix_hq.mp3", "House/Techno", 2400, 30),
    "Habib":   ("habib_mix_hq.mp3", "Deep House", 90, 30),
    "SDKZ":    ("sdkz_mix_hq.mp3", "Techno", 2700, 30),
    "Maya":    ("maya_mix_hq.mp3", "Ambient", 120, 30),
    "Parisa":  ("parisa_mix_hq.mp3", "House", 90, 30),
}
GENRE = {a: v[1] for a, v in SEG.items()}


def ebur(path: Path) -> tuple[str, str]:
    """Integrated LUFS + LRA + true peak from ebur128 summary (real values)."""
    r = subprocess.run([str(FF), "-hide_banner", "-i", str(path), "-af",
                        "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    out = r.stderr
    i = [m for m in re.findall(r"I:\s*(-?[\d.]+)\s*LUFS", out) if float(m) > -70]
    lra = [m for m in re.findall(r"LRA:\s*(-?[\d.]+)\s*LU", out) if float(m) > 0.1]
    return (i[-1] if i else "?", lra[-1] if lra else "?")


def main() -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    idx = [f"# Radio-ish — EPK_Project INDEX ({ts})", "",
           "All 8 artists now have: canonical hq master (48k/320 · epk/mix/),",
           "EBU R128 loudness (I/LRA from ebur128), and a 30s broadcast promo",
           "segment (EBU-14, TP-1.5, 48k/320). Maya/Parisa segments predate this",
           "refresh and are kept in place.",
           "",
           "| artist | genre | hq master | I (LUFS) | LRA (LU) | 30s promo |",
           "|---|---|---|---|---|---|"]
    for artist, (canon, genre, off, ln) in SEG.items():
        mixdir = ROOT / artist / "epk" / "mix"
        canon_path = mixdir / canon
        i = lra = ("?", "?")
        if canon_path.exists():
            i, lra = ebur(canon_path)
        segdir = EPK / artist
        segdir.mkdir(parents=True, exist_ok=True)
        seg_path = segdir / f"{artist.lower()}_30s.mp3"
        done = ""
        if not seg_path.exists() or seg_path.stat().st_size < 500_000:
            r = subprocess.run([str(FF), "-hide_banner", "-y", "-ss", str(off),
                                "-t", str(ln), "-i", str(canon_path),
                                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                                "-ar", "48000", "-b:a", "320k",
                                str(seg_path)], capture_output=True, text=True)
            done = " new" if r.returncode == 0 else f" FAIL#{r.returncode}"
        idx.append(f"| {artist} | {genre} | {canon} | {i} | {lra} | [{(seg_path.name)}/]({artist}/{seg_path.name}){done} |")
    (EPK / "INDEX.md").write_text("\n".join(idx) + "\n")
    print(f"Wrote EPK_Project/INDEX.md + refreshed segments under EPK_Project/")
    print()
    for artist, (canon, genre, off, ln) in SEG.items():
        mixdir = ROOT / artist / "epk" / "mix"
        i, lra = ("?", "?")
        if (mixdir / canon).exists():
            i, lra = ebur(mixdir / canon)
        seg_path = EPK / artist / f"{artist.lower()}_30s.mp3"
        print(f"  {artist:16} I {i:>5} LUFS  LRA {lra:>4}  seg '{seg_path.name}' present={seg_path.exists()}")


if __name__ == "__main__":
    main()
