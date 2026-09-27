#!/usr/bin/env python3
"""qc_loud.py — small, correct: per-artist canonical EBU R128 loudness + comment.

Header-probes every epk mix variant (duration/SR/kbps) for the matrix, then runs
one ebur128 EBU pass on the canonical hq master (windowed to 90 min for sets
>3 h). Real values come from the LAST 'I:'/'LRA:' lines of the ebur128 report
(the running lines are skipped). Writes:

    Radio-ish/QC_Reports/QC_MASTER_<ts>.md
    Radio-ish/QC_Reports/{Artist}_qc_<ts>.md      (variant matrix + loudness)
    Radio-ish/QC_Reports/{Artist}_SHA256SUMS

Read-only on audio. Safe to re-run. python3 qc_loud.py
"""
from __future__ import annotations
import hashlib, re, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path("/Users/bernie/Movies/Radio-ish")
FF = Path("/Users/bernie/Downloads/ffmpeg")
WINDOW = 5400  # 90-min ebur128 window for sets longer than 3 h

CANON = {
    "Habib":  "habib_mix_hq.mp3",
    "Maya":   "maya_mix_hq.mp3",
    "Parisa": "parisa_mix_hq.mp3",
    "SDKZ":   "sdkz_mix_hq.mp3",
    "Dikier": "dikier_mix.mp3",
    "Bernie": "bernie_mix_hq.mp3",
    "El Djemba": "el_djemba_mix_hq.mp3",
    "Alexander Zwo": "alexander_zwo_mix_hq.mp3",
    "DJ Unknown": "dj_unknown_mix_hq.mp3",
}


def probe(path: Path) -> tuple[str, str, str]:
    r = subprocess.run([str(FF), "-hide_banner", "-i", str(path)],
                       capture_output=True, text=True).stderr
    d = re.search(r"Duration:\s*([\d:.]+)", r)
    s = re.search(r"Audio:.*?\b(\d{4,5})\s*Hz", r)
    k = re.search(r"Audio:.*?\b(\d{3})\s*kb/s", r)
    return (d.group(1) if d else "",
            s.group(1) if s else "",
            k.group(1) if k else "")


def to_sec(dur: str) -> int:
    p = [int(x.split(".")[0]) for x in dur.split(":")]
    return p[0] * 3600 + p[1] * 60 + p[2]


def r128(path: Path, sec: int = 0) -> str:
    """EBU integrated + LRA, from ebur128 — real values = LAST summary lines."""
    a = [str(FF), "-hide_banner", "-i", str(path)]
    if sec:
        a.append("-t")
        a.append(str(sec))
    a += ["-af", "ebur128", "-f", "null", "-"]
    out = subprocess.run(a, capture_output=True, text=True).stderr
    i = [m for m in re.findall(r"I:\s*(-?[\d.]+) LUFS", out) if float(m) > -70]
    lra = [m for m in re.findall(r"LRA:\s*(-?[\d.]+) LU", out) if float(m) > 0.1]
    return (f"I {i[-1] if i else '?'} LUFS · LRA {lra[-1] if lra else '?'} LU")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out = ROOT / "QC_Reports"
    out.mkdir(exist_ok=True)
    master = out / f"QC_MASTER_{ts}.md"
    rows = []
    for artist, canon in CANON.items():
        d = ROOT / artist / "epk" / "mix"
        if not d.is_dir():
            print(f"[skip] {artist}: no mix dir")
            continue
        lines = [f"# {artist} — Radio-ish QC ({ts})", "",
                 "| variant | duration | SR(kHz) | kbps |", "|---|---|---|---|", ""]
        dur = ""
        for f in sorted(d.glob("*.mp3")):
            if f.name in (".DS_Store", "SHA256SUMS"):
                continue
            du, s, k = probe(f)
            if f.name == canon:
                dur = du
            lines.append(f"| {f.name} | {du or '?'} | {s and int(s) // 1000 or '?'} | {k or '?'} |")
        canon_f = d / canon
        window = WINDOW if (dur and to_sec(dur) > 3 * 3600) else 0
        note = f"  (90-min window)" if window else ""
        lv = r128(canon_f, window) if canon_f.exists() else "? no canon file"
        lines += ["", "## Canonical master", f"- EBU R128: **{lv}**{note}", "",
                  "## SHA256SUMS", ""]
        sums = []
        for f in sorted(d.glob("*.mp3")):
            if f.name in (".DS_Store", "SHA256SUMS"):
                continue
            sums.append(f"{sha256(f)}  {f.name}")
            lines.append("```sh") if False else None
        lines.append("```")
        lines += sums
        lines.append("```")
        (out / f"{artist}_qc_{ts}.md").write_text("\n".join(lines) + "\n")
        rows.append((artist, canon, dur, lv, note))
    with master.open("w") as mh:
        mh.write(f"# Radio-ish — QC MASTER ({ts})\n\n"
                 "| artist | canon | duration | EBU R128 |\n"
                 "|---|---|---|---|\n")
        for a, c, d_, lv, note in rows:
            mh.write(f"| {a} | {c} | {d_} | {lv}{note} |\n")
    print(f"Wrote QC_Reports/QC_MASTER_{ts}.md + per-artist reports + SHA256SUMS\n")
    for a, c, d_, lv, note in rows:
        print(f"  {a:14} {lv}{note}")


if __name__ == "__main__":
    main()
