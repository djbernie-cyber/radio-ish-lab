#!/usr/bin/env python3
"""Loudness / true-peak QC for the 12 Season One B4 loops (release gate)."""
import json, subprocess, os, re

FF = os.path.expanduser("~/bin/ffmpeg")
R = "/Users/bernie/Movies/Radio-ish"
ROWS = [("SDKZ","SDKZ"),("Yogo","YOGO"),("Bernie","BERNIE"),("Mundz","MUNDZ"),
        ("Maya","MAYA"),("Dikier","DIKIER"),("DJ Unknown","DJ_UNKNOWN"),
        ("Alexander Zwo","ALEXANDER_ZWO"),("Habib","HABIB"),("Parisa","PARISA"),
        ("El Djemba","EL_DJEMBA"),("Schrödinger’s Breakfast","SCHRODINGERS_BREAKFAST")]

def run(args):
    p = subprocess.run(args, capture_output=True, text=True, errors="replace")
    return p.stdout + p.stderr

def measure(path):
    out = run([FF,"-hide_banner","-nostats","-i",path,
               "-af","loudnorm=I=-14:TP=-1.0:print_format=json","-f","null","-"])
    m = re.search(r"\{[^{}]*\"input_i\".*?\}", out, re.S)
    d = json.loads(m.group(0)) if m else {}
    pk = run([FF,"-hide_banner","-nostats","-i",path,
              "-af","astats=measure_overall=Peak_level:measure_perchannel=none","-f","null","-"])
    s = re.search(r"Peak level dB:\s*(-?[\d.]+)", pk)
    return d.get("input_i","?"), d.get("input_tp","?"), d.get("input_lra","?"), (s.group(1) if s else "?")

print(f"  {'ARTIST':<24}{'LUFS':>9}{'TRUE_PEAK':>11}{'SAMPLE_PK':>11}{'LRA':>8}   VERDICT (gate: -12..-16 LUFS, TP <= 0 dBTP)")
res=[]
for a,t in ROWS:
    L=f"{R}/{a}/epk/audio/{t}_B4_30s_loop.wav"
    if not os.path.isfile(L):
        print(f"  {a:<24}{'  MISSING LOOP':>9}"); continue
    i,tp,lra,sp = measure(L)
    try:
        tpf=float(tp)
        v = "CLIPS - fix required" if tpf>0 else ("at 0 dBTP limit" if tpf>-0.1 else "PASS")
    except ValueError:
        v="?"
    res.append((a,i,tp,lra,sp,v))
    print(f"  {a:<24}{i:>9}{tp:>11}{sp:>11}{lra:>8}   {v}")

bad=[r for r in res if "CLIPS" in r[5]]
lim=[r for r in res if "limit" in r[5]]
json.dump(res, open("/tmp/sdkz_bw/loudness.json","w"), indent=1)
print(f"\n  {len(res)-len(bad)-len(lim)} pass | {len(lim)} at the 0 dBTP ceiling | {len(bad)} clip and need re-render")
if bad: print("  CLIPPING: " + ", ".join(r[0] for r in bad))
