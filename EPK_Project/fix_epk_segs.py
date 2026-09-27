#!/usr/bin/env python3
"""fix_epk_segs.py — close the two open EPK_Project gaps.

1. Habib 30s seg: re-cut from habib_mix_hq.mp3, offset 120 s, loudnorm → −14
   (the on-disk seg was built pre-lift and measured −24.8; canonical hq now
   targets −14 after remaster so the seg should match).

2. Bernie: create epk seg from bernie_mix_hq.mp3 at offset 2400 s; the promo
   folder currently lists only a *berne* variant which doesn't match the
   canonical *bernie* master name, so we write bernie_30s.mp3.

Both read-only on masters; only EPK_Project/ mutated. Then refreshes
INDEX.md dims+sizes for the two changed segs.

Run: python3 fix_epk_segs.py
"""
from __future__ import annotations
import re, subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path("/Users/bernie/Movies/Radio-ish")
FF = Path("/Users/bernie/Downloads/ffmpeg")
EPK = ROOT / "EPK_Project"

# (artist_dir, source_hq_master, src_offset_s, out_name)
JOBS = [
    ("Habib",  "habib_mix_hq.mp3",   120, "habib_30s.mp3"),
    ("Bernie", "bernie_mix_hq.mp3", 2400, "bernie_30s.mp3"),
]


def cut(src: Path, off: int, out: Path) -> int:
    r = subprocess.run([
        str(FF), "-hide_banner", "-y", "-ss", str(off), "-t", "30",
        "-i", str(src), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
        "-ar", "48000", "-b:a", "320k", str(out),
    ], capture_output=True, text=True)
    return r.returncode


def choose(segdir: Path) -> Path:
    """Resolution bucket from a fragment of loudnorm stderr — minimal eb unit."""
    r = subprocess.run([str(FF), "-hide_banner", "-t", "25",
                        "-i", str(segdir / "habib_30s.mp3"),
                        "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    return r

def loud(path: Path) -> tuple[str, str]:
    o = subprocess.run([str(FF), "-hide_banner", "-i", str(path), "-af", "ebur128",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    i = [m for m in re.findall(r"I:\s*(-?[\d.]+)\s*LUFS", o) if float(m) > -70]
    l = [m for m in re.findall(r"LRA:\s*(-?[\d.]+)\s*LU", o) if float(m) > 0.1]
    return (i[-1] if i else "?", l[-1] if l else "?")


def probe(path: Path) -> tuple[str, str, str]:
    r = subprocess.run([str(FF), "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True).stderr
    d = re.search(r"Duration:\s*([\d:.]+)", r)
    s = re.search(r"Audio:.*?\b(\d{4,5})\s*Hz", r)
    k = re.search(r"Audio:.*?\b(\d{3})\s*kb/s", r)
    return (d.group(1) if d else "?",
            s.group(1) if s else "?",
            k.group(1) if k else "?")


def main() -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    for artist, master, off, outn in JOBS:
        segdir = EPK / artist
        src = ROOT / artist / "epk" / "mix" / master
        out = segdir / outn
        if not src.exists():
            print(f"[skip] {artist}: canon {master} missing")
            continue
        segdir.mkdir(parents=True, exist_ok=True)
        rc = cut(src, off, out)
        i, lra = loud(out)
        print(f"{artist}: {'OK' if rc == 0 else 'FAIL'}  {outn}  I {i} LUFS  LRA {lra} LU")

    # refresh INDEX with current dims for the two touched segs
    idx = EPK / "INDEX.md"
    if idx.exists():
        text = idx.read_text()
        for artist, _, _, outn in JOBS:
            p = EPK / artist / outn
            if not p.exists():
                continue
            d, s, k = probe(p)
            src = ROOT / artist / "epk" / "mix" / {
                "Habib": "habib_mix_hq.mp3", "Bernie": "bernie_mix_hq.mp3"}[artist]
            text = text.replace(f"`{outn}`",
                                f"`{outn}` ({d}, {int(s) // 1000}kHz/{k})")
        idx.write_text(text)
        print("INDEX.md refreshed for touched segs.")


if __name__ == "__main__":
    main()
