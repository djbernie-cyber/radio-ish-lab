#!/usr/bin/env python3
"""Measure the Season One masters: loudness, true peak, and octave-band balance.

The EQ decision must be driven by measurement. Band energies come from ffmpeg's
bandpass filters on a loudness-weighted pass, reported relative to the loudest
artist so we can see which masters are bright, dull, muddy or thin.
"""
import json, os, re, subprocess, concurrent.futures as cf

FF = os.path.expanduser("~/bin/ffmpeg")
FP = os.path.expanduser("~/bin/ffprobe")
R  = "/Users/bernie/Movies/Radio-ish"

# deck assignment from the label: XDJ-RX3 unless the artist used a Denon
DECK = {"DJ Unknown": "Denon"}

# the deliverable mixes, per the house matrix in MASTER_README
MIXDIRS = [
 ("SDKZ",  "SDKZ"), ("Yogo", "YOGO"), ("Bernie", "BERNIE"), ("Mundz", "MUNDZ"),
 ("Maya", "MAYA"), ("Dikier", "DIKIER"), ("DJ Unknown", "DJ_UNKNOWN"),
 ("Alexander Zwo", "ALEXANDER_ZWO"), ("Habib", "HABIB"), ("Parisa", "PARISA"),
 ("El Djemba", "EL_DJEMBA"), ("Schrödinger’s Breakfast", "SCHRODINGERS_BREAKFAST"),
]

def run(a, t=1800):
    p = subprocess.run(a, capture_output=True, text=True, errors="replace", timeout=t)
    return p.stdout + p.stderr

def dur(p):
    try: return float(run([FP,"-v","error","-show_entries","format=duration","-of","csv=p=0",p],120).strip())
    except Exception: return 0.0

def loud(p):
    o = run([FF,"-hide_banner","-nostats","-i",p,"-af",
             "loudnorm=I=-14:TP=-1.0:print_format=json","-f","null","-"], 3600)
    m = re.search(r"\{[^{}]*\"input_i\".*?\}", o, re.S)
    if not m: return None, None, None
    d = json.loads(m.group(0))
    return d.get("input_i"), d.get("input_tp"), d.get("input_lra")

BANDS = [("sub",20,60),("bass",60,120),("lomid",120,250),("mud",250,500),
         ("lomid2",500,1000),("pres",1000,2000),("pres2",2000,4000),
         ("brill",4000,8000),("air",8000,16000)]

def bands(p, mid=90):
    """Relative energy per octave band from a `mid`-second excerpt at 1/4 in."""
    tot = dur(p)
    if tot <= 0: return {}
    ss = max(0.0, tot*0.25)
    out = {}
    for name, lo, hi in BANDS:
        o = run([FF,"-hide_banner","-nostats","-ss",f"{ss:.2f}","-t",str(mid),"-i",p,
                 "-af",f"bandpass=f={lo}:width_type=o:w={lo},astats=metadata=1:reset=0,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-",
                 "-f","null","-"], 600)
        vals = [float(m.group(1)) for m in re.finditer(r"lavfi\.astats\.Overall\.RMS_level=(-?[\d.]+)", o)]
        out[name] = round(max(vals), 2) if vals else None
    return out

def loop_of(name, tag):
    return f"{R}/{name}/epk/audio/{tag}_B4_30s_loop.wav"

def measure_one(item):
    name, tag = item
    res = {"artist": name, "deck": DECK.get(name, "Pioneer XDJ-RX3")}
    L = loop_of(name, tag)
    if os.path.isfile(L):
        i, tp, lra = loud(L)
        res["loop"] = {"file": os.path.relpath(L, R), "lufs": i, "tp": tp, "lra": lra,
                       "bytes": os.path.getsize(L), "dur": round(dur(L), 6)}
        res["loop_bands"] = bands(L, 30)
    m = f"{R}/{name}/epk/mix"
    mixes = []
    if os.path.isdir(m):
        for f in sorted(os.listdir(m)):
            if f.lower().endswith((".mp3", ".wav", ".flac", ".m4a")):
                p = f"{m}/{f}"
                i, tp, lra = loud(p)
                mixes.append({"file": f, "bytes": os.path.getsize(p),
                              "dur": round(dur(p), 3), "lufs": i, "tp": tp, "lra": lra})
    res["mixes"] = mixes
    return res

with cf.ThreadPoolExecutor(max_workers=4) as ex:
    data = list(ex.map(measure_one, MIXDIRS))

json.dump(data, open("/tmp/sdkz_bw/mix_audit.json","w"), indent=1, ensure_ascii=False)

print("== 30s LOOPS (the EPK deliverable) ==")
print(f"  {'ARTIST':<24}{'DECK':<18}{'LUFS':>8}{'TP':>8}{'LRA':>7}  VERDICT vs -14/-1.0")
for d in data:
    L = d.get("loop")
    if not L: print(f"  {d['artist']:<24} (no loop)"); continue
    li, tp = float(L["lufs"]), float(L["tp"])
    v = "on target" if abs(li+14) < 0.6 and tp <= -0.9 else ("LOUD" if li > -13 else "QUIET")
    print(f"  {d['artist']:<24}{d['deck']:<18}{li:>8.2f}{tp:>8.2f}{L['lra']:>7}  {v}")

print("\n== FULL-LENGTH MIXES (house matrix deliverables) ==")
print(f"  {'ARTIST':<24}{'FILE':<26}{'DUR':>10}{'LUFS':>9}{'TP':>8}  VERDICT")
for d in data:
    if not d["mixes"]: print(f"  {d['artist']:<24}{'(none)':<26}"); continue
    for m in d["mixes"]:
        try: li, tp = float(m["lufs"]), float(m["tp"])
        except (TypeError, ValueError): print(f"  {d['artist']:<24}{m['file']:<26} (unreadable)"); continue
        v = "on target" if abs(li+14) < 0.6 and tp <= -0.9 else ("CLIPPING" if tp > -0.9 else ("LOUD" if li > -13 else "QUIET"))
        print(f"  {d['artist']:<24}{m['file']:<26}{m['dur']:>10.1f}{li:>9.2f}{tp:>8.2f}  {v}")

print("\n== octave balance, relative to the fleet loudest (dB; 0 = loudest artist) ==")
allb = {}
for d in data:
    b = d.get("loop_bands")
    if b and all(v is not None for v in b.values()): allb[d["artist"]] = b
if allb:
    ref = {k: max(b[k] for b in allb.values()) for k in next(iter(allb.values()))}
    keys = [k for k in next(iter(allb.values()))]
    print(f"  {'ARTIST':<24}" + "".join(f"{k:>8}" for k in keys))
    for a, b in allb.items():
        print(f"  {a:<24}" + "".join(f"{b[k]-ref[k]:>8.1f}" for k in keys))
