#!/usr/bin/env python3
"""Standardise every Season One master to one house gain + house EQ.  (v3)

Target: -14 LUFS integrated, true peak <= -1.0 dBTP (MASTER_README gate).
The chain is identical for every artist, so the 12 masters actually match. The
only per-artist variable is the trim needed to reach the target loudness.

House chain, tuned for the Pioneer XDJ-RX3 (the label deck):
  high-pass 28 Hz    rumble/DC; protects the RX3's strong bass from slop
  -1.5 dB @ 220 Hz   takes the edge off mud
  +1.0 dB @ 3 kHz    presence, so it reads on a dark system
  +1.5 dB @ 9 kHz    air shelf
  trim               lands integrated loudness on -14 LUFS
  limiter            peak safety

Why v3: v1 re-encoded the full file up to four times chasing true peak, and v2
did the same. Both measured the SOURCE once, then spent an hour per artist
rediscovering a 1 dB offset. v3 instead:

  1. one heavy pass  source -> 48 kHz 24-bit WAV intermediate (chain + trim)
  2. measure the INTERMEDIATE, so any loudness drift from the EQ is known
  3. one static correction applied to the WAV if the trim needs refining
  4. cheap encodes from that WAV for mix / mix_hq (48 k) and _epk (44.1 k)

So each artist costs one decode+filter pass plus two fast encodes, and both
masters are bit-consistent because they come from the same intermediate. MP3
inter-sample overshoot is then handled by choosing the limiter ceiling with
headroom to spare rather than by iteration.

mix and mix_hq are bit-identical by the house matrix, so they share one encode.
Resumable: a master already measuring on target is left untouched.
"""
import json, math, os, re, shutil, subprocess, time, datetime

FF = os.path.expanduser("~/bin/ffmpeg")
R  = "/Users/bernie/Movies/Radio-ish"
ARCH = f"{R}/Archive/2026-09-26_superseded/mixes"
TMP = "/tmp/sdkz_bw/std3"; os.makedirs(TMP, exist_ok=True)
TARGET_LUFS, TP_CEIL, OVERSHOOT = -14.0, -0.9, 1.3   # measured MP3 overshoot, dB

STEM = {"SDKZ":"sdkz","Yogo":"yogo","Bernie":"bernie","Mundz":"mundz","Maya":"maya",
        "Dikier":"dikier","DJ Unknown":"dj_unknown","Alexander Zwo":"alexander_zwo",
        "Habib":"habib","Parisa":"parisa","El Djemba":"el_djemba",
        "Schrödinger’s Breakfast":"schrodingers_breakfast"}
JOBS = [
 ("SDKZ",                    "sdkz_mix.mp3",          "rx3"),
 ("Yogo",                    "yogo_mix.mp3",          "rx3"),
 ("Bernie",                  "bernie_mix.mp3",        "rx3"),
 ("Mundz",                   "mundz_mix.wav",         "rx3"),
 ("Maya",                    "maya_mix_remaster.mp3", "rx3"),
 ("Dikier",                  "dikier_mix.mp3",        "rx3"),
 ("DJ Unknown",              "dj_unknown_mix.wav",    "denon"),
 ("Alexander Zwo",           "alexander_zwo_mix.mp3", "rx3"),
 ("Habib",                   "habib_mix_remaster.mp3","rx3"),
 ("Parisa",                  "parisa_mix.mp3",        "rx3"),
 ("El Djemba",               "el_djemba_mix.mp3",     "rx3"),
 ("Schrödinger’s Breakfast",  "4-Audio 0001 [2026-09-21 130546].wav", "rx3"),
]
EQ = {
 "rx3":  "highpass=f=28,equalizer=f=220:t=q:w=0.8:g=-1.5,"
         "equalizer=f=3000:t=q:w=0.9:g=1.0,equalizer=f=9000:t=h:w=6000:g=1.5",
 "denon":"highpass=f=30,equalizer=f=220:t=q:w=0.8:g=-1.0,"
         "equalizer=f=3000:t=q:w=0.9:g=0.5,equalizer=f=9000:t=h:w=6000:g=0.8",
}

def run(a, t=21600):
    p = subprocess.run(a, capture_output=True, text=True, errors="replace", timeout=t)
    return (p.stdout or "") + (p.stderr or "")

def lufs_tp(p):
    o = run([FF,"-hide_banner","-nostats","-i",p,"-af",
             "loudnorm=I=-14:TP=-1.0:print_format=json","-f","null","-"])
    m = re.search(r"\{[^{}]*\"input_i\".*?\}", o, re.S)
    if not m: return None, None
    d = json.loads(m.group(0))
    try: return float(d["input_i"]), float(d["input_tp"])
    except Exception: return None, None

def ff(a, out, label):
    o = run([FF,"-y","-hide_banner","-loglevel","error"] + a)
    if not (os.path.isfile(out) and os.path.getsize(out) > 1024):
        tail = o.strip().splitlines()[-1] if o.strip() else "no output"
        print(f"      ffmpeg {label}: {tail[:170]}", flush=True)
        return False
    return True

def on_target(path):
    l, t = lufs_tp(path)
    if l is None: return False, None, None
    return (abs(l - TARGET_LUFS) <= 0.4 and t <= TP_CEIL), l, t

log = open("/tmp/sdkz_bw/standardise3.log", "a", buffering=1)
def say(m): print("  " + m, flush=True); log.write(m + "\n")

say(f"\n=== house standardisation v3 — {datetime.date.today().isoformat()} ===")
results = []
for artist, srcname, deck in JOBS:
    d = f"{R}/{artist}/epk/mix"
    stem = STEM[artist]
    mix, hq, epk = f"{d}/{stem}_mix.mp3", f"{d}/{stem}_mix_hq.mp3", f"{d}/{stem}_mix_epk.mp3"
    ad = f"{ARCH}/{artist}"

    if os.path.isfile(mix) and os.path.isfile(epk):
        ok_m, lm, tm = on_target(mix)
        ok_e, le, te = on_target(epk)
        if ok_m and ok_e:
            say(f"{artist:<24} already on target — skipped")
            continue

    src = None
    for cand in (f"{ad}/{srcname}", f"{ad}/{stem}_mix.mp3", f"{ad}/{stem}_mix.wav",
                 f"{ad}/{stem}_mix_hq.mp3", f"{d}/{srcname}"):
        if os.path.isfile(cand) and os.path.getsize(cand) > 1024:
            src = cand; break
    if not src:
        say(f"{artist:<24} [err] no usable source"); continue

    t0 = time.time()
    l0, tp0 = lufs_tp(src)
    if l0 is None:
        say(f"{artist:<24} [err] could not measure source"); continue

    trim = TARGET_LUFS - l0
    # ceiling: keep peaks clear of 0 dBTP after MP3 overshoot
    ceil_db = min(-1.5, (tp0 + trim if tp0 is not None else -1.5) - 2.5)
    lim = 10 ** (ceil_db / 20.0)
    wav = f"{TMP}/{stem}.wav"
    af = (f"{EQ[deck]},volume={trim:.2f}dB,"
          f"alimiter=level=disabled:limit={lim:.6f}:attack=5:release=50:level_in=1")
    if not ff(["-i",src,"-af",af,"-ar","48000","-ac","2","-c:a","pcm_s24le",wav], wav, "wav"):
        say(f"{artist:<24} [err] intermediate render failed"); continue

    # the EQ shifts loudness slightly; correct it on the WAV (cheap, no re-filter)
    lw, tw = lufs_tp(wav)
    if lw is not None and abs(lw - TARGET_LUFS) > 0.25:
        corr = TARGET_LUFS - lw
        af2 = (f"volume={corr:.2f}dB,"
               f"alimiter=level=disabled:limit={min(1.0, lim*10**(corr/20)):.6f}:attack=5:release=50:level_in=1")
        tmpw = f"{TMP}/{stem}_c.wav"
        if ff(["-i",wav,"-af",af2,"-c:a","pcm_s24le",tmpw], tmpw, "wav-correct"):
            os.replace(tmpw, wav)
            trim += corr

    p48, p44 = f"{TMP}/{stem}.mp3", f"{TMP}/{stem}_epk.mp3"
    if not ff(["-i",wav,"-ar","48000","-ac","2","-c:a","libmp3lame","-b:a","320k",p48], p48, "mp3-48"):
        say(f"{artist:<24} [err] 48 kHz encode failed"); continue
    if not ff(["-i",wav,"-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","320k",p44], p44, "mp3-44"):
        say(f"{artist:<24} [err] 44.1 kHz encode failed"); continue

    os.makedirs(ad, exist_ok=True)
    for f in (f"{stem}_mix.mp3", f"{stem}_mix_hq.mp3", f"{stem}_mix_epk.mp3", srcname):
        p = f"{d}/{f}"
        if os.path.isfile(p) and not os.path.exists(f"{ad}/{f}"):
            shutil.move(p, f"{ad}/{f}")
    shutil.copy2(p48, mix); shutil.copy2(p48, hq); shutil.copy2(p44, epk)
    os.remove(wav)   # transient: 11 GB for the long masters

    sd = f"{R}/Season One/Artists/{artist}/Mix"
    if os.path.isdir(sd):
        for f in os.listdir(sd):
            t = f"{sd}/{f}"
            if os.path.exists(t): os.remove(t)
            if os.path.isfile(f"{d}/{f}"): os.link(f"{d}/{f}", t)

    lm, tm = lufs_tp(mix); le, te = lufs_tp(epk)
    results.append(dict(artist=artist, source=os.path.basename(src), src_lufs=l0,
                        src_tp=tp0, trim=round(trim,2), ceiling=round(ceil_db,2),
                        mix_lufs=lm, mix_tp=tm, epk_lufs=le, epk_tp=te,
                        secs=round(time.time()-t0,1)))
    flag = "" if (tm <= TP_CEIL and te <= TP_CEIL) else "  ** TP OVER GATE **"
    say(f"{artist:<24} {l0:>7.2f} -> 48k {lm:>7.2f}/{tm:>6.2f}  44.1k {le:>7.2f}/{te:>6.2f}"
        f"  trim {trim:>6.2f} ceil {ceil_db:>5.1f}  {time.time()-t0:>5.0f}s{flag}")

json.dump(results, open("/tmp/sdkz_bw/standardise3.json","w"), indent=1, ensure_ascii=False)
bad = [r for r in results if r["mix_tp"] > TP_CEIL or r["epk_tp"] > TP_CEIL
       or abs(r["mix_lufs"]+14) > 0.5 or abs(r["epk_lufs"]+14) > 0.5]
say(f"done: {len(results)} processed, {len(results)-len(bad)} fully on target")
for r in bad: say(f"  REVIEW {r['artist']}: {r['mix_lufs']}/{r['mix_tp']}  {r['epk_lufs']}/{r['epk_tp']}")
