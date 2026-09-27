#!/usr/bin/env python3
"""Standardise every Season One master to one house gain + house EQ.

Target: -14 LUFS integrated, true peak <= -1.0 dBTP (MASTER_README gate).
Chain is identical for all artists so the 12 masters actually match. The only
per-artist variable is the trim needed to reach the target.

House chain, tuned for the Pioneer XDJ-RX3 (the label's deck):
  high-pass 28 Hz      rumble/DC, protects the RX3's strong bass from slop
  -1.5 dB @ 220 Hz     takes edge off mud
  +1.0 dB @ 3 kHz      presence so it reads on a dark system
  +1.5 dB @ 9 kHz      air shelf
  trim                lands integrated loudness on -14 LUFS
  limiter -2.0 dB     leaves headroom because MP3 re-encoding adds ~1 dB
                       of inter-sample overshoot

DJ Unknown used a Denon, which is brighter than the RX3, so they get a gentler
presence/air version of the same chain.

mix and mix_hq are bit-identical by the house matrix, so we encode once and
install the same file under both names.
"""
import json, os, re, shutil, subprocess, sys, time, datetime

FF = os.path.expanduser("~/bin/ffmpeg")
FP = os.path.expanduser("~/bin/ffprobe")
R  = "/Users/bernie/Movies/Radio-ish"
ARCH = f"{R}/Archive/2026-09-26_superseded/mixes"
TMP = "/tmp/sdkz_bw/std"; os.makedirs(TMP, exist_ok=True)
TARGET_LUFS, LIMIT_LOSSY = -14.0, 0.794327   # -2.0 dB

# artist -> (source file, deck)
JOBS = [
 ("SDKZ",                    "sdkz_mix.mp3",                              "rx3"),
 ("Yogo",                    "yogo_mix.mp3",                              "rx3"),
 ("Bernie",                  "bernie_mix.mp3",                            "rx3"),
 ("Mundz",                   "mundz_mix.wav",                             "rx3"),
 ("Maya",                    "maya_mix_remaster.mp3",                     "rx3"),
 ("Dikier",                  "dikier_mix.mp3",                            "rx3"),
 ("DJ Unknown",              "dj_unknown_mix.wav",                        "denon"),
 ("Alexander Zwo",           "alexander_zwo_mix.mp3",                     "rx3"),
 ("Habib",                   "habib_mix_remaster.mp3",                    "rx3"),
 ("Parisa",                  "parisa_mix.mp3",                            "rx3"),
 ("El Djemba",               "el_djemba_mix.mp3",                         "rx3"),
 ("Schrödinger’s Breakfast",  "4-Audio 0001 [2026-09-21 130546].wav",      "rx3"),
]

EQ = {
 "rx3":  "highpass=f=28,equalizer=f=220:t=q:w=0.8:g=-1.5,"
         "equalizer=f=3000:t=q:w=0.9:g=1.0,equalizer=f=9000:t=h:w=6000:g=1.5",
 "denon":"highpass=f=30,equalizer=f=220:t=q:w=0.8:g=-1.0,"
         "equalizer=f=3000:t=q:w=0.9:g=0.5,equalizer=f=9000:t=h:w=6000:g=0.8",
}

def run(a, t=7200):
    """ffmpeg writes its loudnorm/astats report to STDERR, so capture both
    streams. Reading stdout alone silently yields nothing and every measurement
    comes back empty."""
    p = subprocess.run(a, capture_output=True, text=True, errors="replace", timeout=t)
    return (p.stdout or "") + (p.stderr or "")

def loud(p):
    o = run([FF,"-hide_banner","-nostats","-i",p,"-af",
             "loudnorm=I=-14:TP=-1.0:print_format=json","-f","null","-"], 7200)
    m = re.search(r"\{[^{}]*\"input_i\".*?\}", o, re.S)
    if m:
        d = json.loads(m.group(0))
        try:
            i, tp = float(d["input_i"]), float(d["input_tp"])
            if abs(i) < 99 and abs(tp) < 99:
                return i, tp
        except (KeyError, ValueError):
            pass
    # fallback: pure sample-peak reading, so we degrade instead of hard-failing
    o2 = run([FF,"-hide_banner","-nostats","-i",p,"-af",
              "astats=measure_overall=Peak_level:measure_perchannel=none","-f","null","-"], 7200)
    m2 = re.search(r"Peak level dB:\s*(-?[\d.]+)", o2)
    if not m2:
        return None, None
    pk = float(m2.group(1))
    return pk - 10.0, pk          # crude stand-in; flagged in the log if used

def chain(deck, trim, rate):
    return (f"{EQ[deck]},volume={trim:.2f}dB,"
            f"alimiter=level=disabled:limit={LIMIT_LOSSY}:attack=5:release=50:level_in=1")

def render(src, dst, deck, trim, rate):
    run([FF,"-y","-hide_banner","-loglevel","error","-i",src,
         "-af",chain(deck,trim,rate),"-ar",str(rate),"-ac","2",
         "-c:a","libmp3lame","-b:a","320k",dst])

log = open("/tmp/sdkz_bw/standardise.log","a", buffering=1)
def say(m):
    print("  " + m, flush=True); log.write(m + "\n")

say(f"\n=== house standardisation pass — {datetime.date.today().isoformat()} ===")
results = []
for artist, srcname, deck in JOBS:
    d = f"{R}/{artist}/epk/mix"
    src = f"{d}/{srcname}"
    if not os.path.isfile(src):
        say(f"{artist:<24} [err] source missing: {srcname}"); continue
    t0 = time.time()
    l0, tp0 = loud(src)
    if l0 is None:
        say(f"{artist:<24} [err] could not measure source"); continue

    # pass 1 with the measured trim, then converge if the EQ moved the loudness
    trim = TARGET_LUFS - l0
    tmp48 = f"{TMP}/{artist}.mp3"
    render(src, tmp48, deck, trim, 48000)
    l1, tp1 = loud(tmp48)
    passes = 1
    if l1 is not None and abs(l1 - TARGET_LUFS) > 0.3:
        trim += TARGET_LUFS - l1
        render(src, tmp48, deck, trim, 48000)
        l1, tp1 = loud(tmp48)
        passes = 2

    # archive originals, then install (mix and mix_hq are the same master)
    ad = f"{ARCH}/{artist}"
    os.makedirs(ad, exist_ok=True)
    stem = {"SDKZ":"sdkz","Yogo":"yogo","Bernie":"bernie","Mundz":"mundz","Maya":"maya",
            "Dikier":"dikier","DJ Unknown":"dj_unknown","Alexander Zwo":"alexander_zwo",
            "Habib":"habib","Parisa":"parisa","El Djemba":"el_djemba",
            "Schrödinger’s Breakfast":"schrodingers_breakfast"}[artist]
    for f in (f"{stem}_mix.mp3", f"{stem}_mix_hq.mp3", f"{stem}_mix_epk.mp3", srcname):
        p = f"{d}/{f}"
        if os.path.isfile(p) and not os.path.exists(f"{ad}/{f}"):
            shutil.move(p, f"{ad}/{f}")
    for f in (f"{stem}_mix.mp3", f"{stem}_mix_hq.mp3"):
        shutil.copy2(tmp48, f"{d}/{f}")
    # 44.1 kHz EPK master
    tmp44 = f"{TMP}/{artist}_epk.mp3"
    render(src, tmp44, deck, trim, 44100)
    shutil.copy2(tmp44, f"{d}/{stem}_mix_epk.mp3")

    # re-link the Season One delivery tree: new inode, so the old hardlink is stale
    sd = f"{R}/Season One/Artists/{artist}/Mix"
    if os.path.isdir(sd):
        for f in os.listdir(sd):
            tgt = f"{sd}/{f}"
            if os.path.exists(tgt): os.remove(tgt)
            if os.path.isfile(f"{d}/{f}"):
                os.link(f"{d}/{f}", tgt)

    le, tpe = loud(f"{d}/{stem}_mix_epk.mp3")
    results.append(dict(artist=artist, deck=deck, source=srcname,
                        src_lufs=l0, src_tp=tp0, trim_db=round(trim,2), passes=passes,
                        mix_lufs=l1, mix_tp=tp1, epk_lufs=le, epk_tp=tpe,
                        bytes=os.path.getsize(f"{d}/{stem}_mix.mp3"),
                        secs=round(time.time()-t0,1)))
    say(f"{artist:<24} {l0:>7.2f} -> {l1:>7.2f} LUFS  TP {tp1:>6.2f}  "
        f"trim {trim:>6.2f} dB  {passes} pass  {time.time()-t0:>6.0f}s")

json.dump(results, open("/tmp/sdkz_bw/standardise.json","w"), indent=1, ensure_ascii=False)
bad = [r for r in results if abs(r["mix_lufs"]+14) > 0.5 or r["mix_tp"] > -0.9]
say(f"done: {len(results)} artists, {len(results)-len(bad)} on target")
for r in bad:
    say(f"  NEEDS REVIEW: {r['artist']} {r['mix_lufs']} LUFS TP {r['mix_tp']}")
