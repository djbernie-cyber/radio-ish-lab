#!/usr/bin/env python3
"""True-peak repair for the masters that came out of standardise_masters.py too hot.

All 12 masters now sit at -14.00 LUFS. Four came out with true peaks ABOVE 0 dBTP
(El Djemba +1.27, Bernie +0.83, Schrodinger's +0.74, DJ Unknown +0.09), because
standardise_masters.py hit the floor of its ceiling formula (-1.5 dB) and
heavily-limited material overshoots a -1.5 dB ceiling by 1.6-2.8 dB once MP3
inter-sample peaks are included.

Rather than re-deriving anything, this reuses the trim each artist already
landed on and simply lowers the limiter ceiling by the overshoot actually
observed, plus margin for the extra overshoot that harder limiting creates.
Lowering the ceiling shaves a little energy off, so the pre-limiter trim is
compensated to hold -14 LUFS.

Sources are always the ARCHIVED ORIGINALS, never the already-processed master,
so nothing is ever a second-generation encode.
"""
import json, os, re, shutil, subprocess, time, datetime

FF = os.path.expanduser("~/bin/ffmpeg")
R  = "/Users/bernie/Movies/Radio-ish"
ARCH = f"{R}/Archive/2026-09-26_superseded/mixes"
TMP = "/tmp/sdkz_bw/fix"; os.makedirs(TMP, exist_ok=True)
TARGET_LUFS, TP_TARGET = -14.0, -1.0

# only these four: measured TP above 0 dBTP after the v3 pass
OFFENDERS = ["El Djemba", "Bernie", "DJ Unknown", "Schrödinger’s Breakfast"]

STEM = {"SDKZ":"sdkz","Yogo":"yogo","Bernie":"bernie","Mundz":"mundz","Maya":"maya",
        "Dikier":"dikier","DJ Unknown":"dj_unknown","Alexander Zwo":"alexander_zwo",
        "Habib":"habib","Parisa":"parisa","El Djemba":"el_djemba",
        "Schrödinger’s Breakfast":"schrodingers_breakfast"}
SRCNAME = {"SDKZ":"sdkz_mix.mp3","Yogo":"yogo_mix.mp3","Bernie":"bernie_mix.mp3",
           "Mundz":"mundz_mix.wav","Maya":"maya_mix_remaster.mp3","Dikier":"dikier_mix.mp3",
           "DJ Unknown":"dj_unknown_mix.wav","Alexander Zwo":"alexander_zwo_mix.mp3",
           "Habib":"habib_mix_remaster.mp3","Parisa":"parisa_mix.mp3",
           "El Djemba":"el_djemba_mix.mp3",
           "Schrödinger’s Breakfast":"4-Audio 0001 [2026-09-21 130546].wav"}
DECK = {"DJ Unknown":"denon"}
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

prev = {r["artist"]: r for r in json.load(open("/tmp/sdkz_bw/standardise3.json"))}
log = open("/tmp/sdkz_bw/tpfix.log", "a", buffering=1)
def say(m): print("  " + m, flush=True); log.write(m + "\n")

say(f"\n=== true-peak repair — {datetime.date.today().isoformat()} ===")
results = []
for artist in OFFENDERS:
    p = prev[artist]
    d, ad, stem = f"{R}/{artist}/epk/mix", f"{ARCH}/{artist}", STEM[artist]
    mix, hq, epk = f"{d}/{stem}_mix.mp3", f"{d}/{stem}_mix_hq.mp3", f"{d}/{stem}_mix_epk.mp3"
    src = f"{ad}/{SRCNAME[artist]}"
    if not (os.path.isfile(src) and os.path.getsize(src) > 1024):
        say(f"{artist:<24} [err] archived source missing: {src}"); continue

    # overshoot actually observed above the ceiling that produced these files
    old_ceil = p["ceiling"]
    observed = max(p["mix_tp"], p["epk_tp"]) - old_ceil
    new_ceil = TP_TARGET - (observed + 0.3)      # +0.3 dB margin for harder limiting
    delta    = new_ceil - old_ceil              # negative
    trim     = p["trim"] + 0.5 * abs(delta)     # hold -14 LUFS through the extra limiting
    lim      = 10 ** (new_ceil / 20.0)
    deck     = DECK.get(artist, "rx3")

    t0 = time.time()
    wav = f"{TMP}/{stem}.wav"
    af = (f"{EQ[deck]},volume={trim:.2f}dB,"
          f"alimiter=level=disabled:limit={lim:.6f}:attack=5:release=50:level_in=1")
    if not ff(["-i",src,"-af",af,"-ar","48000","-ac","2","-c:a","pcm_s24le",wav], wav, "wav"):
        say(f"{artist:<24} [err] intermediate failed"); continue

    p48, p44 = f"{TMP}/{stem}.mp3", f"{TMP}/{stem}_epk.mp3"
    if not ff(["-i",wav,"-ar","48000","-ac","2","-c:a","libmp3lame","-b:a","320k",p48], p48, "mp3-48"):
        say(f"{artist:<24} [err] 48k encode failed"); continue
    if not ff(["-i",wav,"-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","320k",p44], p44, "mp3-44"):
        say(f"{artist:<24} [err] 44.1k encode failed"); continue

    shutil.copy2(p48, mix); shutil.copy2(p48, hq); shutil.copy2(p44, epk)
    os.remove(wav)
    sd = f"{R}/Season One/Artists/{artist}/Mix"
    if os.path.isdir(sd):
        for f in os.listdir(sd):
            t = f"{sd}/{f}"
            if os.path.exists(t): os.remove(t)
            if os.path.isfile(f"{d}/{f}"): os.link(f"{d}/{f}", t)

    lm, tm = lufs_tp(mix); le, te = lufs_tp(epk)
    results.append(dict(artist=artist, old_ceil=old_ceil, new_ceil=round(new_ceil,2),
                        trim=round(trim,2), mix_lufs=lm, mix_tp=tm,
                        epk_lufs=le, epk_tp=te, secs=round(time.time()-t0,1)))
    flag = "" if (tm <= TP_TARGET and te <= TP_TARGET) else "  ** STILL OVER **"
    say(f"{artist:<24} ceil {old_ceil:>5.2f}->{new_ceil:>5.2f} trim {trim:>6.2f} | "
        f"48k {lm:>7.2f}/{tm:>6.2f}  44.1k {le:>7.2f}/{te:>6.2f}  {time.time()-t0:>5.0f}s{flag}")

json.dump(results, open("/tmp/sdkz_bw/tpfix.json","w"), indent=1, ensure_ascii=False)
bad = [r for r in results if r["mix_tp"] > TP_TARGET or r["epk_tp"] > TP_TARGET]
say(f"done: {len(results)} repaired, {len(results)-len(bad)} now at or under {TP_TARGET} dBTP")
for r in bad: say(f"  REVIEW {r['artist']}: {r['mix_tp']} / {r['epk_tp']}")
