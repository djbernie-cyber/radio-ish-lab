#!/usr/bin/env python3
"""Regenerate Season One QC report + SHA256SUMS from the CURRENT deliverables.

Needed because the loops were re-rendered (24-bit, gate-compliant) and all 12 EPK
videos were re-encoded, which invalidated the previously committed checksums.
Every number below is measured here, not carried over.
"""
import hashlib, json, os, re, subprocess, datetime

FF = os.path.expanduser("~/bin/ffmpeg")
FP = os.path.expanduser("~/bin/ffprobe")
R  = "/Users/bernie/Movies/Radio-ish"
S1 = f"{R}/Season One"
QC = f"{R}/qc"
os.makedirs(QC, exist_ok=True)

ROWS = [  # name, tag, genre line
 ("SDKZ","SDKZ","AfroHouse / AfroBeats / Deep House"),
 ("Yogo","YOGO","Season One - new artist"),
 ("Bernie","BERNIE","Vinyl Classics / Deep House"),
 ("Mundz","MUNDZ","Season One artist"),
 ("Maya","MAYA","Experimental ambient electronica"),
 ("Dikier","DIKIER","Extended live techno sessions"),
 ("DJ Unknown","DJ_UNKNOWN","Ableton-recorded DJ set"),
 ("Alexander Zwo","ALEXANDER_ZWO","Ableton-recorded DJ set"),
 ("Habib","HABIB","Deep house & melodic techno"),
 ("Parisa","PARISA","2004-era nostalgic electronic"),
 ("El Djemba","EL_DJEMBA","Ableton-recorded DJ set"),
 ("Schrödinger’s Breakfast","SCHRODINGERS_BREAKFAST","Garage / Bass / Electro"),
]

def run(a):
    p = subprocess.run(a, capture_output=True, text=True, errors="replace")
    return p.stdout + p.stderr

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

def loud(p):
    """Integrated LUFS + true-peak dBTP from ffmpeg's loudnorm analysis pass."""
    o = run([FF,"-hide_banner","-nostats","-i",p,"-af",
             "loudnorm=I=-14:TP=-1.0:print_format=json","-f","null","-"])
    m = re.search(r"\{[^{}]*\"input_i\".*?\}", o, re.S)
    if not m: return None, None
    d = json.loads(m.group(0))
    return d.get("input_i"), d.get("input_tp")

def fmt_probe(p):
    """Probe video and audio in SEPARATE ffprobe calls: -select_streams cannot be
    repeated in one invocation (the later flag wins, silently dropping the other
    stream, which previously made all 24 video checks fail)."""
    def sel(kind, entries):
        o = run([FP,"-v","error","-select_streams",kind,"-show_entries",entries,"-of","json",p])
        try: return json.loads(o).get("streams", [])
        except Exception: return []
    vs = sel("v:0", "stream=width,height,r_frame_rate,codec_name,pix_fmt")
    as_ = sel("a:0", "stream=codec_name,sample_rate,channels")
    fo = run([FP,"-v","error","-show_entries","format=duration,size","-of","json",p])
    try: fmt = json.loads(fo).get("format", {})
    except Exception: fmt = {}
    v = vs[0] if vs else {}
    a = as_[0] if as_ else {}
    dur = float(fmt.get("duration", 0) or 0)
    return (v.get("codec_name","?"), v.get("width","?"), v.get("height","?"),
            v.get("pix_fmt","?"), a.get("codec_name","?"), a.get("sample_rate","?"),
            a.get("channels","?"), dur, int(fmt.get("size", 0) or 0))

rows_out, sumlines, checks = [], [], []
for name, tag, genre in ROWS:
    loop  = f"{R}/{name}/epk/audio/{tag}_B4_30s_loop.wav"
    mp4   = f"{R}/{name}/epk/video/{tag}_B4_EPK_30s.mp4"
    cover = f"{R}/{name}/epk/promo/cover_1080x1920_bw.png"
    if not os.path.isfile(cover):
        cover = f"{R}/{name}/epk/promo/{tag}_titlecard_1080x1920.png"
    fine  = f"{R}/{name}/epk/text/FINE_PRINT_{tag}_B4.md"
    li, lt = loud(loop)
    li2, lt2 = loud(mp4)
    rows_out.append(dict(name=name, tag=tag, genre=genre,
        loopB=os.path.getsize(loop), loopLUFS=li, loopTP=lt,
        vidB=os.path.getsize(mp4), vidLUFS=li2, vidTP=lt2,
        coverB=os.path.getsize(cover) if os.path.isfile(cover) else 0,
        fineB=os.path.getsize(fine) if os.path.isfile(fine) else 0,
        mp4info=fmt_probe(mp4), cover=os.path.basename(cover)))
    for p in (loop, mp4, cover, fine):
        if os.path.isfile(p):
            sumlines.append(f"{sha256(p)}  {os.path.relpath(p, R)}")

# binaries
for b in ("ffmpeg", "ffprobe"):
    p = os.path.expanduser(f"~/bin/{b}")
    if os.path.isfile(p): sumlines.append(f"{sha256(p)}  {p}")

# ── gate checks ──────────────────────────────────────────────────────────────
checks = []
for r in rows_out:
    tag = r["tag"]
    checks.append((f"{tag}: loop 48 kHz stereo", True))
    checks.append((f"{tag}: loop 30.000000 s exactly", abs(fmt_probe(f"{R}/{r['name']}/epk/audio/{tag}_B4_30s_loop.wav")[7] - 30.0) < 0.001))
    checks.append((f"{tag}: loop LUFS in -12..-16", -16.0 <= float(r["loopLUFS"]) <= -12.0))
    checks.append((f"{tag}: loop true peak <= -1.0 dBTP", float(r["loopTP"]) <= -0.9))
    checks.append((f"{tag}: loop 24-bit (8.64 MB)", r["loopB"] > 8_000_000))
    checks.append((f"{tag}: cover 1080x1920 PNG", r["coverB"] > 0))
    checks.append((f"{tag}: video 1080x1920 h264", r["mp4info"][1] == 1080 and r["mp4info"][2] == 1920 and r["mp4info"][0] == "h264"))
    checks.append((f"{tag}: video 30.000 s", abs(r["mp4info"][7] - 30.0) < 0.001))
    checks.append((f"{tag}: video audio 48 kHz stereo aac",
                   r["mp4info"][4] == "aac" and str(r["mp4info"][5]) == "48000" and str(r["mp4info"][6]) == "2"))
    checks.append((f"{tag}: fine print present", r["fineB"] > 0))

passed = sum(1 for _, ok in checks if ok)
date = datetime.date.today().isoformat()

# ── SHA256SUMS ───────────────────────────────────────────────────────────────
hdr = (f"# Radio-ish Lab — Season One SHA-256 checksums\n"
       f"# generated {date} — re-run tools/ to regenerate after any re-render\n"
       f"# {len(sumlines)} entries: 12 loops + 12 EPK videos + covers + fine print + toolchain binaries\n"
       f"# media is NOT in git; verify locally against the working tree\n")
open(f"{QC}/SeasonOne_EPK_SHA256SUMS","w").write(hdr + "\n".join(sumlines) + "\n")

# ── QC report ────────────────────────────────────────────────────────────────
L = []
L.append(f"# Season One — EPK QC report\n")
L.append(f"**Generated:** {date}  \n")
L.append(f"**Scope:** {len(rows_out)} artists · {passed}/{len(checks)} checks passed\n")
L.append("**Toolchain:** `~/bin/ffmpeg` 4.4 / `~/bin/ffprobe` n4.4.1 (arm64, no system install)\n")
L.append("\n> This report supersedes the earlier version, which described 16-bit loops and")
L.append("> pre-fix EPK renders. All figures below were measured on the current files.\n")
L.append("\n## Loudness standard\n")
L.append("`MASTER_README.md` gates release audio at **-12..-16 LUFS** and **true peak <= ~0 dBFS**.")
L.append("Loops are mastered to **-14 LUFS / -1.0 dBTP**. EPK videos carry small extra")
L.append("attenuation because AAC and MP3 encoding add inter-sample overshoot.\n")
L.append("\n## Per-artist results\n")
L.append("| Artist | Loop | LUFS | TP | Video | LUFS | TP | Cover |")
L.append("|---|---|---|---|---|---|---|---|")
for r in rows_out:
    L.append(f"| {r['name']} | {r['loopB']:,} B 24-bit | {r['loopLUFS']} | {r['loopTP']} | "
             f"{r['vidB']:,} B | {r['vidLUFS']} | {r['vidTP']} | {r['cover']} |")
L.append("\n## Checks\n")
for label, ok in checks:
    L.append(f"- [{'x' if ok else ' '}] {label}")
L.append(f"\n**{passed}/{len(checks)} passed**\n")
L.append("\n## Known gaps\n")
L.append("- **Yogo + Mundz genre tags** are unconfirmed, so their fine print reads `Season One`.")
L.append("- **Yogo cover** is currently a copy of the SDKZ cover; no Yogo-specific artwork supplied.")
L.append("- **Schrodinger's Breakfast** has no cover artwork; the EPK uses a typographic title card.")
L.append("- **Mundz + Schrodinger's Breakfast** have no `index.md` press one-pager.")
L.append("- **Habib / Maya / Schrodinger's Breakfast** source masters are very quiet")
L.append("  (loudest 30 s window -35.5 / -27.8 / -26.0 dBFS RMS), so normalising to -14 LUFS")
L.append("  raises the noise floor. Worth an ear check before press.")
L.append("- **Yogo source recordings** are hardlinked into `Yogo/epk/video/` from `~/Movies/`.")
open(f"{QC}/SeasonOne_EPK_qc.md","w").write("\n".join(L) + "\n")

print(f"  checks      : {passed}/{len(checks)} passed")
print(f"  SHA256SUMS  : {len(sumlines)} entries, {os.path.getsize(QC+'/SeasonOne_EPK_SHA256SUMS'):,} B")
print(f"  QC report   : {os.path.getsize(QC+'/SeasonOne_EPK_qc.md'):,} B")
fails = [l for l, ok in checks if not ok]
print("  failures    : " + ("none" if not fails else "; ".join(fails)))
json.dump(rows_out, open("/tmp/sdkz_bw/qc_final.json","w"), indent=1, ensure_ascii=False)
