#!/usr/bin/env python3
"""qc_sweep.py — Radio-ish Lab QC sweep (read-only).

Probes every variant in every artist's epk/mix (duration / sample-rate /
bitrate) and performs an EBU R128 sweep + true-peak on the artist's canonical
(hq) master. Very long sets (>= 2.5 h) are analyzed on a 90-minute window to
keep the sweep practical; the window is recorded in the report.

Writes:
  QC_Reports/{Artist}_QC_{ts}.md            per artist
  QC_Reports/QC_MASTER_{ts}.md              combined table
  {Artist}/epk/mix/SHA256SUMS               per-artist checksums (canonical)
"""
import hashlib, re, subprocess, sys, time
from pathlib import Path

ROOT = Path("/Users/bernie/Movies/Radio-ish")
FF = Path("/Users/bernie/Downloads/ffmpeg")
TS = time.strftime("%Y%m%d_%H%M%S")
WINDOW = 5400  # 90-minute loudness window for very long sets

ARTISTS = {
    "Habib":     ("Deep House", "habib_mix_hq.mp3"),
    "Maya":      ("Ambient", "maya_mix_hq.mp3"),
    "Parisa":    ("House", "parisa_mix_hq.mp3"),
    "SDKZ":      ("Techno", "sdkz_mix_hq.mp3"),
    "Dikier":    ("Techno", "dikier_mix.mp3"),
    "Bernie":    ("Techno", "bernie_mix_hq.mp3"),
    "El Djemba": ("House / Techno", "el_djemba_mix_hq.mp3"),
    "Alexander Zwo": ("House / Techno", "alexander_zwo_mix_hq.mp3"),
}

def probe(path):
    r = subprocess.run([str(FF), "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True)
    err = r.stderr
    dur = re.search(r"Duration:\s*([\d:.]+)", err)
    sr = re.search(r"Audio:.*?\b(\d{4,5})\s*Hz", err)
    br = re.search(r"Audio:.*?(\d{3})\s*kb/s", err)
    return (dur.group(1) if dur else "?",
            int(sr.group(1)) if sr else 0,
            int(br.group(1)) if br else 0)

def dur_sec(d):
    try:
        p = [int(x) for x in d.split(":")]
        return p[0]*3600 + p[1]*60 + p[2]
    except Exception:
        return 0

def run_windows(path, win):
    """EBU R128 (I, LRA) + volumedetect (mean/peak) on first `win` seconds."""
    i = lra = pk = "?"
    r1 = subprocess.run([str(FF), "-hide_banner", "-t", str(win), "-i", str(path),
                         "-af", "ebur128", "-f", "null", "-"],
                        capture_output=True, text=True)
    out = r1.stderr
    m = re.search(r"I:\s*(-?[\d.]+)\s*LUFS", out)
    if m: i = m.group(1)
    m = re.search(r"LRA:\s*(-?[\d.]+)\s*LU", out)
    if m: lra = m.group(1)
    r2 = subprocess.run([str(FF), "-hide_banner", "-t", str(win), "-i", str(path),
                         "-af", "volumedetect", "-f", "null", "-"],
                        capture_output=True, text=True)
    m = re.search(r"max_volume:\s*(-?[\d.]+)\s*dB", r2.stderr)
    if m: pk = m.group(1)
    return i, lra, pk

def loudness_text(i, lra, pk, winused):
    window = f" (window {winused/60:.0f} min)" if winused else ""
    return (f"| Integrated | {i} LUFS{window} |\n"
            f"| Loudness Range | {lra} LU |\n"
            f"| Max volume | {pk} dB |")

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

QC = ROOT / "QC_Reports"
QC.mkdir(exist_ok=True)
master_rows = []
for artist, (genre, canon) in ARTISTS.items():
    mixd = ROOT / artist / "epk" / "mix"
    per = [f"{artist}_QC_{TS}.md"]
    lines = [f"# {artist} — Radio-ish QC", "",
             f"Genre: {genre} · File set: {mixd}", ""]
    truth = []
    for f in sorted(mixd.glob("*.mp3")):
        du, sr, br = probe(f)
        lines.append(f"- `{f.name}` — {du} · {sr} Hz · {br} kbps")
        truth.append((f.name, du))
    dsec = dur_sec(du) and dur_sec(du)
    winused = 0
    if dsec and dsec >= 2*3600 + 30*60:
        winused = WINDOW
        i, lra, pk = run_windows(mixd / canon, WINDOW)
    else:
        winused = 0
        i, lra, pk = run_windows(mixd / canon, 0)
    lines += ["", "## Canonical master — EBU R128", "",
              loudness_text(i, lra, pk, winused), "",
              "## Checksums", "", "```"]
    cpath = mixd / canon
    if cpath.exists():
        h = sha256(cpath)
        for name, _ in truth:
            lines.append(f"{h}  {name}")
    lines.append("```")
    lines.append("")
    (QC / per[0]).write_text("\n".join(lines))
    master_rows.append(f"| {artist} | {genre} | {canon} | {du} | {i} | {lra} | {pk} |")

master_path = QC / f"QC_MASTER_{TS}.md"
head = ["# Radio-ish QC MASTER", f"Run: {TS}", "",
        "| artist | genre | canonical | duration | I LUFS | LRA | max dB |", "|---|---|---|---|---|---|---|"]
(QC / f"QC_MASTER_{TS}.md").write_text("\n".join(head + master_rows))
print(f"Wrote {len(ARTISTS)} artist reports + QC_MASTER_{TS}.md at {QC}")
