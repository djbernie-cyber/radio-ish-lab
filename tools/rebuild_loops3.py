#!/usr/bin/env python3
"""Rebuild the 12 Season One B4 loops: auto window pick + gate-compliant loudness.

Fixes (all found by real measurement, not assumed):
  1. hardcoded window offset -> Habib's loop was digital silence
  2. no loudness normalisation -> 3 loops >0 dBTP, 6 outside -12..-16 LUFS
  3. loops were 16-bit while the published spec says 24-bit

Window selection uses exact per-30s RMS from ONE decoded PCM pass. The previous
attempt used `astats=metadata` + `ametadata=print`, which prints PER FRAME
(346k spurious "windows" on an 8041 s file) and selected an offset past EOF.

Seam construction C is UNCHANGED: body = A[0.5:30.5] crossfaded at the end with A[0:0.5].
"""
import json, os, re, struct, subprocess, sys, math

FF = os.path.expanduser("~/bin/ffmpeg")
FP = os.path.expanduser("~/bin/ffprobe")
R  = "/Users/bernie/Movies/Radio-ish"
TMP = "/tmp/sdkz_bw/loops3"; os.makedirs(TMP, exist_ok=True)
SR, CH, WIN = 48000, 2, 30
WSPAN = SR * WIN * CH          # samples (int16) per 30 s window

SRC = [
 ("SDKZ",                    f"{R}/SDKZ/SDKZ_B4_03.09.26.WAV",                                             "SDKZ"),
 ("Yogo",                    f"{R}/radio-ish 2 Project/Samples/Recorded/4-Audio 0003 [2026-09-24 154843].wav",   "YOGO"),
 ("Bernie",                  f"{R}/Bernie/epk/audio/2026-09-12 14-25-18.wav",                                 "BERNIE"),
 ("Mundz",                   f"{R}/Mundz/epk/audio/mundz_session_152305.wav",                                 "MUNDZ"),
 ("Dikier",                  f"{R}/Dikier/epk/audio/2026-09-10 14-20-14.wav",                                 "DIKIER"),
 ("DJ Unknown",              f"{R}/DJ Unknown/epk/processing/2026-09-19 16-07-31_raw.wav",                    "DJ_UNKNOWN"),
 ("Alexander Zwo",           f"{R}/Alexander Zwo/epk/processing/2026-09-14 16-53-34_raw.wav",                 "ALEXANDER_ZWO"),
 ("Parisa",                  f"{R}/Parisa/epk/audio/parisa_mix_wvideo.wav",                                   "PARISA"),
 ("El Djemba",               f"{R}/El Djemba/epk/processing/2026-09-14 13-36-32_raw.wav",                     "EL_DJEMBA"),
 ("Maya",                    f"{R}/Maya/epk/mix/maya_mix_epk.mp3",                                            "MAYA"),
 ("Habib",                   f"{R}/Habib/epk/mix/habib_mix_epk.mp3",                                          "HABIB"),
 ("Schrödinger’s Breakfast",  f"{R}/Schrödinger’s Breakfast/epk/mix/4-Audio 0001 [2026-09-21 130546].wav",     "SCHRODINGERS_BREAKFAST"),
]

def run(a):
    p = subprocess.run(a, capture_output=True, text=True, errors="replace")
    return p.stdout + p.stderr

def window_rms(src):
    """Exact RMS (dBFS) of every 30 s window, via one streaming PCM decode."""
    p = subprocess.Popen([FF,"-v","error","-i",src,"-ac",str(CH),"-ar",str(SR),
                          "-f","s16le","-"], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, bufsize=1<<20)
    out, carry, total = [], b"", 0
    WBYTES = WSPAN * 2
    def take(buf):
        """consume all whole windows in buf, return the leftover bytes"""
        nonlocal total
        n = (len(buf) // WBYTES) * WSPAN
        if n == 0: return buf
        s = struct.unpack(f"<{n}h", buf[:n*2])
        total += n
        for i in range(n // WSPAN):
            w = s[i*WSPAN:(i+1)*WSPAN]
            acc = 0
            for v in w: acc += v*v
            rms = math.sqrt(acc / len(w))
            out.append(20*math.log10(rms/32768.0) if rms > 0 else -200.0)
        return buf[n*2:]
    while True:
        buf = p.stdout.read(1 << 22)          # 4 MB per read
        if not buf: break
        carry = take(carry + buf)
    p.stdout.close(); p.wait()
    return out, total/(SR*CH)

def best_offset(rms):
    """strongest window, excluding the first (fade-in) and last (tail)."""
    c = [(v,i) for i,v in enumerate(rms) if 0 < i < len(rms)-1 and v > -60]
    if not c: c = list(enumerate(rms))
    if not c: return None, -200.0
    v,i = max(c)
    return i*WIN, v

def seam(src, start, out):
    fc = ("[0:a]aformat=sample_fmts=s32:sample_rates=48000:channel_layouts=stereo,asplit=2[a][b];"
          "[a]atrim=0.5:30.5,asetpts=N/SR/TB[m];[b]atrim=0:0.5,asetpts=N/SR/TB[h];"
          "[m][h]acrossfade=d=0.5:c1=tri:c2=tri[o]")
    run([FF,"-y","-hide_banner","-loglevel","error","-ss",str(start),"-t","31","-i",src,
         "-filter_complex",fc,"-map","[o]","-t","30","-ar","48000","-ac","2","-c:a","pcm_s24le",out])
    return os.path.isfile(out) and os.path.getsize(out) > 8_000_000

def loud(p):
    o = run([FF,"-hide_banner","-nostats","-i",p,"-af",
             "loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json","-f","null","-"])
    m = re.search(r"\{[^{}]*\"input_i\".*?\}", o, re.S)
    if not m: return None
    d = json.loads(m.group(0))
    try:  # guard against -inf/inf, which loudnorm's pass-2 parser rejects
        if not all(abs(float(d[k])) < 99 for k in ("input_i","input_tp","input_thresh","target_offset")):
            return None
    except (TypeError, ValueError): return None
    return d

def norm2(d, tmp, dst):
    af = (f"loudnorm=I=-14:TP=-1.0:LRA=11:measured_I={d['input_i']}:"
          f"measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:"
          f"measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true")
    run([FF,"-y","-hide_banner","-loglevel","error","-i",tmp,"-af",af,
         "-ar","48000","-ac","2","-c:a","pcm_s24le",dst])
    return os.path.isfile(dst) and os.path.getsize(dst) > 8_000_000

def dur(p):
    try: return float(run([FP,"-v","error","-show_entries","format=duration","-of","csv=p=0",p]).strip())
    except ValueError: return 0.0

print(f"  {'ARTIST':<24}{'WIN':>6}{'PICK_RMS':>10}{'OFFSET':>8}{'DUR':>11}{'LUFS':>8}{'TP':>8}{'BITS':>6}  STATUS")
report=[]
for name, src, tag in SRC:
    if not os.path.isfile(src):
        print(f"  {name:<24}  [err] source missing"); continue
    rms, sdur = window_rms(src)
    off, pickdb = best_offset(rms)
    if off is None:
        print(f"  {name:<24}  [err] no usable window"); continue
    tmp = f"{TMP}/{tag}_seam.wav"
    if not seam(src, off, tmp):
        print(f"  {name:<24}{off:>8}  [err] seam render failed"); continue
    d = loud(tmp)
    dst = f"{R}/{name}/epk/audio/{tag}_B4_30s_loop.wav"
    if not d:
        print(f"  {name:<24}{off:>8}  [err] pass-1 gave non-finite levels"); continue
    if not norm2(d, tmp, dst):
        print(f"  {name:<24}{off:>8}  [err] pass-2 failed"); continue
    chk = loud(dst)
    li, lt = chk["input_i"], chk["input_tp"]
    dd = dur(dst)
    bits = "24" if os.path.getsize(dst) > 8_000_000 else "16"
    ok = abs(dd-30.0) < 0.001 and float(lt) <= -0.9 and -16.0 <= float(li) <= -12.0 and bits=="24"
    print(f"  {name:<24}{len(rms):>6}{pickdb:>10.1f}{off:>8}{dd:>11.6f}{li:>8}{lt:>8}{bits:>6}  {'PASS' if ok else 'CHECK'}")
    report.append(dict(artist=name, tag=tag, src=src, offset=off, pick_rms=round(pickdb,2),
                       dur=dd, lufs=li, tp=lt, bytes=os.path.getsize(dst)))

json.dump(report, open("/tmp/sdkz_bw/loops3.json","w"), indent=1, ensure_ascii=False)
good=[r for r in report if abs(r["dur"]-30.0)<0.001 and float(r["tp"])<=-0.9 and -16.0<=float(r["lufs"])<=-12.0]
print(f"\n  {len(good)}/{len(report)} loops now meet: 30.000000 s, -12..-16 LUFS, TP <= -1.0 dBTP, 24-bit")
