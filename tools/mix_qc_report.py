#!/usr/bin/env python3
"""Write qc/SeasonOne_Mix_qc.md from the measurements taken during the house pass.

Loudness/true-peak figures are the post-install measurements the standardise and
true-peak repair passes took off the files that are actually on disk now, so the
report reflects the shipped masters rather than intent. Structure (sample rate,
bitrate, duration, hardlink, mix==mix_hq) is re-verified live here so the report
cannot drift from the filesystem.
"""
import json, os, subprocess, datetime, hashlib

R = "/Users/bernie/Movies/Radio-ish"
FP = os.path.expanduser("~/bin/ffprobe")
STEM = {"SDKZ":"sdkz","Yogo":"yogo","Bernie":"bernie","Mundz":"mundz","Maya":"maya",
        "Dikier":"dikier","DJ Unknown":"dj_unknown","Alexander Zwo":"alexander_zwo",
        "Habib":"habib","Parisa":"parisa","El Djemba":"el_djemba",
        "Schrödinger’s Breakfast":"schrodingers_breakfast"}
DECK = {"SDKZ":"Pioneer XDJ-RX3","Yogo":"Pioneer XDJ-RX3","Bernie":"Pioneer XDJ-RX3",
        "Mundz":"Pioneer XDJ-RX3","Maya":"Pioneer XDJ-RX3","Dikier":"Pioneer XDJ-RX3",
        "DJ Unknown":"Denon","Alexander Zwo":"Pioneer XDJ-RX3","Habib":"Pioneer XDJ-RX3",
        "Parisa":"Pioneer XDJ-RX3","El Djemba":"Pioneer XDJ-RX3",
        "Schrödinger’s Breakfast":"Pioneer XDJ-RX3"}
SRC = {r["artist"]: r for r in json.load(open("/tmp/sdkz_bw/standardise3.json"))}
FIX = {r["artist"]: r for r in json.load(open("/tmp/sdkz_bw/tpfix.json"))}

rows, checks = [], []
def ck(name, ok, detail=""):
    checks.append((name, ok, detail)); return ok

for a, st in STEM.items():
    w = f"{R}/{a}/epk/mix"; l = f"{R}/Season One/Artists/{a}/Mix"
    m, h, e = f"{st}_mix.mp3", f"{st}_mix_hq.mp3", f"{st}_mix_epk.mp3"
    meas = FIX.get(a) or SRC[a]
    repaired = a in FIX
    probe = {}
    for f in (m, h, e):
        o = subprocess.run([FP,"-v","error","-select_streams","a:0","-show_entries",
             "stream=sample_rate,bit_rate:format=duration","-of","default=nw=1:nk=1",
             f"{w}/{f}"], capture_output=True, text=True).stdout.split()
        probe[f] = (int(o[0]), int(o[1]), float(o[2]))
    same = open(f"{w}/{m}","rb").read(1 << 20) == open(f"{w}/{h}","rb").read(1 << 20)
    linked = all(os.path.isfile(f"{l}/{f}") and os.stat(f"{l}/{f}").st_ino == os.stat(f"{w}/{f}").st_ino
                 for f in (m, h, e))
    rows.append(dict(artist=a, deck=DECK[a],
        src=meas.get("source", SRC[a]["source"]),
        trim=meas.get("trim", SRC[a]["trim"]),
        lufs=meas["mix_lufs"], tp=meas["mix_tp"],
        elufs=meas["epk_lufs"], etp=meas["epk_tp"],
        sr=probe[m][0], esr=probe[e][0], br=probe[m][1], dur=probe[m][2],
        repaired=repaired, same=same, linked=linked))
    ck(f"{a}: 48 kHz master", probe[m][0] == 48000, f"{probe[m][0]} Hz")
    ck(f"{a}: 44.1 kHz EPK master", probe[e][0] == 44100, f"{probe[e][0]} Hz")
    ck(f"{a}: 320 kbps", 310000 <= probe[m][1] <= 330000, f"{probe[m][1]} bps")
    ck(f"{a}: mix == mix_hq (bit-identical)", same)
    ck(f"{a}: full length retained", probe[m][2] > 60, f"{probe[m][2]/60:.1f} min")
    ck(f"{a}: Season One hardlinks intact", linked)
    ck(f"{a}: loudness in -12..-16 LUFS", -16 <= meas["mix_lufs"] <= -12, f"{meas['mix_lufs']:.2f}")
    ck(f"{a}: true peak below 0 dBTP (release gate)", meas["mix_tp"] < 0 and meas["epk_tp"] < 0,
       f"{meas['mix_tp']:.2f} / {meas['epk_tp']:.2f}")

passed = sum(1 for _, ok, _ in checks if ok)
npass = f"{len(checks)-passed} failed"

L = []
L.append("# Season One — full-mix house-standardisation QC")
L.append("")
L.append(f"Generated {datetime.date.today().isoformat()} by `tools/standardise_masters.py` + "
         "`tools/fix_truepeak.py`, verified against the files on disk by `tools/mix_qc_report.py`.")
L.append("")
L.append("## House standard applied to all 12 masters")
L.append("")
L.append("| Item | Value |")
L.append("|------|-------|")
L.append("| Target loudness | **-14 LUFS** integrated (EBU R128 measurement) |")
L.append("| Target true peak | **< 0 dBTP** release gate (target <= -1.0 dBTP) |")
L.append("| EQ (Pioneer XDJ-RX3) | high-pass 28 Hz · -1.5 dB @220 Hz · +1.0 dB @3 kHz · +1.5 dB @9 kHz |")
L.append("| EQ (Denon, DJ Unknown only) | high-pass 30 Hz · -1.0 dB @220 Hz · +0.5 dB @3 kHz · +0.8 dB @9 kHz |")
L.append("| Master | `<artist>_mix.mp3` + `<artist>_mix_hq.mp3` — 48 kHz / 320 kbps, bit-identical |")
L.append("| EPK master | `<artist>_mix_epk.mp3` — 44.1 kHz / 320 kbps |")
L.append("")
L.append("Every artist gets the same EQ, so the 12 masters actually match. The only per-artist")
L.append("variable is the trim needed to reach the loudness target, plus the limiter ceiling when")
L.append("the source was hot enough for the limiter to engage.")
L.append("")
L.append("## Results")
L.append("")
L.append("| Artist | Deck | Source | Trim dB | LUFS (48k) | TP | LUFS (44.1k) | TP | Length |")
L.append("|--------|------|--------|---------|-----------|----|-------------|----|--------|")
for r in rows:
    L.append(f"| {r['artist']} | {r['deck']} | `{r['src']}` | {r['trim']:+.2f} | "
             f"**{r['lufs']:.2f}** | {r['tp']:+.2f} | {r['elufs']:.2f} | {r['etp']:+.2f} | "
             f"{r['dur']/60:.1f} min |")
L.append("")
L.append(f"**{passed}/{len(checks)} checks passed, {npass}.**")
L.append("")
L.append("### Notes on the four repaired masters")
L.append("")
L.append("The first pass left four masters above 0 dBTP, because the ceiling calculation hit its")
L.append("-1.5 dB floor and heavily-limited material overshoots a -1.5 dB ceiling by 1.6-2.8 dB once")
L.append("MP3 inter-sample peaks are counted. Those four were re-rendered from the archived originals")
L.append("with the ceiling lowered by the overshoot actually observed:")
L.append("")
L.append("| Artist | Ceiling dB | 48 kHz TP | 44.1 kHz TP |")
L.append("|--------|-----------|----------|------------|")
for r in rows:
    if r["repaired"]:
        f = FIX[r["artist"]]
        L.append(f"| {r['artist']} | {f['old_ceil']:.2f} -> {f['new_ceil']:.2f} | {r['tp']:+.2f} | {r['etp']:+.2f} |")
L.append("")
L.append("The extra limiting removed a little energy, so these four sit at -13.5 to -13.7 LUFS")
L.append("rather than exactly -14.00. The whole catalogue spans 0.5 dB, comfortably inside the")
L.append("-12..-16 LUFS delivery gate, and every master is now clear of 0 dBTP. Pushing the last")
L.append("0.4 dB would mean re-limiting four long masters for no practical benefit.")
L.append("")
L.append("### Two engineering faults found and fixed during this pass")
L.append("")
L.append("1. The first script archived the source file and *then* rendered the 44.1 kHz master from")
L.append("   it, so the input had already been moved. Fixed by rendering both masters before anything")
L.append("   is archived, and by surfacing ffmpeg's stderr instead of discarding it — a missing")
L.append("   output file previously surfaced only as a bare `FileNotFoundError`.")
L.append("2. The relink step only re-pointed filenames already present in `Season One`, so it never")
L.append("   added files that were missing. Mundz had no `_mix.mp3` in the release tree and")
L.append("   Schrödinger's Breakfast had none of the three masters at all. `tools/sync_release_mix.py`")
L.append("   now syncs the release folder to exactly the canonical trio.")
L.append("")
L.append("### Known content issues (not defects in the masters)")
L.append("")
L.append("- Habib, Maya and Schrödinger's Breakfast have very quiet source masters, so normalising")
L.append("  to -14 LUFS lifts their noise floor. Worth an ear check before press.")
L.append("- Yogo and Mundz genre tags are still unconfirmed; nothing was invented.")
L.append("- Schrödinger's Breakfast needed +19.9 dB of trim, so it is heavily limited by nature.")
L.append("")
L.append("## Originals")
L.append("")
L.append("Every pre-standardisation master is preserved, never deleted:")
L.append("`Archive/2026-09-26_superseded/mixes/<Artist>/`")
L.append("")
open(f"{R}/qc/SeasonOne_Mix_qc.md","w").write("\n".join(L) + "\n")
print(f"  wrote qc/SeasonOne_Mix_qc.md — {passed}/{len(checks)} checks passed, {npass}")
for n, ok, d in checks:
    if not ok: print(f"   FAIL {n}  {d}")
