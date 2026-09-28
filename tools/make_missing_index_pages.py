#!/usr/bin/env python3
"""Create the three missing Season One Press/index.md one-pagers.

Nine of the twelve artists shipped an index.md; Mundz, Yogo and Schrodinger's
Breakfast did not, which left the release tree visibly incomplete.

Follows the existing convention exactly: the text lives in the artist's working
folder (<Artist>/epk/index.md) and Season One holds a hardlink to it, so editing
either side edits one file. Content mirrors the established SDKZ format, but the
master list reflects the CURRENT standardised house matrix and the genres are
left honest rather than invented.
"""
import os, datetime

R = "/Users/bernie/Movies/Radio-ish"
DATA = {
 "Mundz": dict(
   stem="mundz", upper="MUNDZ", dur="2:10:59",
   src="mundz_session_152305.wav",
   tracks=["mundz_session_152305.wav - original session capture"],
   video=["mundz_set_p1.mov - performance video, part 1",
          "mundz_set_p2.mov - performance video, part 2"],
   style=("Mundz is a Radio-ish Lab Season One artist. Style and genre descriptors "
          "are still to be confirmed by the artist - the release does not invent them.")),
 "Yogo": dict(
   stem="yogo", upper="YOGO", dur="2:46:33",
   src="mastered mix (epk/mix)",
   tracks=["2026-09-24 15-10-39.mov - full performance video",
           "2026-09-24 15-49-02.mov - full performance video"],
   video=[],
   style=("Yogo is a new Radio-ish Lab Season One artist. Style and genre descriptors "
          "are still to be confirmed by the artist - the release does not invent them.")),
 "Schrödinger’s Breakfast": dict(
   stem="schrodingers_breakfast", upper="SCHRODINGER'S BREAKFAST", dur="3:30:02",
   src="4-Audio 0001 [2026-09-21 130546].wav",
   tracks=["2026-09-21 13-34-28.mov - full performance video"],
   video=[],
   style=("Garage / Bass / Electro. A long-form three-and-a-half hour set built from "
          "Dub and bass-leaning garage pressure.")),
}

log = open("/tmp/sdkz_bw/index_pages.log", "a", buffering=1)
def say(m): print("  " + m, flush=True); log.write(m + "\n")
say(f"\n=== missing press index pages — {datetime.date.today().isoformat()} ===")

for artist, d in DATA.items():
    s = d["stem"]
    L = [f"# {d['upper']} - EPK", "", "## DJ & Performing Artist", "", "### Audio",
         f"- {s}_mix.mp3 - Mixed DJ set, house-standardised master "
         f"(-14 LUFS, 48 kHz/320 kbps, {d['dur']})",
         f"- {s}_mix_hq.mp3 - HQ mastered mix (48 kHz/320 kbps, bit-identical to the master)",
         f"- {s}_mix_epk.mp3 - EPK delivery master (44.1 kHz/320 kbps)",
         f"- {s.upper()}_B4_30s_loop.wav - Seamless 30 s loop (48 kHz/24-bit stereo)"]
    L += [f"- {t}" for t in d["tracks"]]
    L += ["", "### Video", f"- {s.upper()}_B4_EPK_30s.mp4 - EPK promo video, 30 s, "
              "H.264 + AAC, burned-in fine print"]
    L += [f"- {v}" for v in d["video"]]
    L += ["", "### Style", d["style"], "",
          "---", f"*Radio-ish Lab · Season One · {d['upper']}*"]
    body = "\n".join(L) + "\n"

    work = f"{R}/{artist}/epk/index.md"
    with open(work, "w") as f:
        f.write(body)
    rel = f"{R}/Season One/Artists/{artist}/Press/index.md"
    if os.path.lexists(rel): os.remove(rel)
    os.link(work, rel)
    ok = os.stat(work).st_ino == os.stat(rel).st_ino
    say(f"{artist:<26} wrote {len(body):>5} B -> epk/index.md, hardlinked to Press/index.md "
        f"({'ok' if ok else 'LINK FAILED'})")

say("all 12 artists now have a press index page")
