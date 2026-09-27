#!/usr/bin/env python3
"""Re-render EPK mp4s whose AAC true peak exceeds -1.0 dBTP.

AAC is lossy: it adds inter-sample overshoot, so a source mastered to exactly
-1.0 dBTP can land above 0 dBTP after encoding. Attenuate the mp4 audio only
(the 24-bit loop WAV stays the reference master) and verify post-encode.
"""
import json, os, re, subprocess

FF = os.path.expanduser("~/bin/ffmpeg")
R  = "/Users/bernie/Movies/Radio-ish"
FONT  = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT2 = "/System/Library/Fonts/Supplemental/Arial.ttf"

TASKS = [  # name, tag, line1, line2
 ("Bernie", "BERNIE", "BERNIE", "Vinyl Classics / Deep House"),
 ("Schrödinger’s Breakfast", "SCHRODINGERS_BREAKFAST", "SCHRODINGER'S BREAKFAST", "Garage / Bass / Electro"),
]

def run(a):
    p = subprocess.run(a, capture_output=True, text=True, errors="replace")
    return p.stdout + p.stderr

def tp_of(path):
    o = run([FF,"-hide_banner","-nostats","-i",path,"-af",
             "loudnorm=I=-14:TP=-1.0:print_format=json","-f","null","-"])
    m = re.search(r"\{[^{}]*\"input_i\".*?\}", o, re.S)
    if not m: return None, None
    d = json.loads(m.group(0))
    return d.get("input_i"), d.get("input_tp")

def esc(s): return s.replace("'", "\\\\'").replace(":", "\\\\:")

for name, tag, l1, l2 in TASKS:
    E  = f"{R}/{name}/epk"
    loop  = f"{E}/audio/{tag}_B4_30s_loop.wav"
    cover = f"{E}/promo/cover_1080x1920_bw.png"
    if not os.path.isfile(cover):
        cover = f"{E}/promo/{tag}_titlecard_1080x1920.png"
    out = f"{E}/video/{tag}_B4_EPK_30s.mp4"
    vf = (f"drawtext=fontfile='{FONT}':fontcolor=white:fontsize=64:bordercolor=black:borderw=8:"
          f"shadowcolor=black:shadowx=4:shadowy=4:text='{esc(l1)}':x=(w-text_w)/2:y=1240,"
          f"drawtext=fontfile='{FONT2}':fontcolor=white:fontsize=40:bordercolor=black:borderw=7:"
          f"shadowcolor=black:shadowx=3:shadowy=3:text='{esc(l2)}':x=(w-text_w)/2:y=1330,"
          f"drawtext=fontfile='{FONT2}':fontcolor=0xC8C8C8:fontsize=34:bordercolor=black:borderw=6:"
          f"shadowcolor=black:shadowx=3:shadowy=3:text='RADIO-ISH LAB  ·  SEASON ONE':x=(w-text_w)/2:y=1420,"
          f"drawtext=fontfile='{FONT2}':fontcolor=0x9A9A9A:fontsize=30:bordercolor=black:borderw=6:"
          f"shadowcolor=black:shadowx=3:shadowy=3:text='30s seamless loop  ·  1080x1920':x=(w-text_w)/2:y=1500")
    gain = 0.0
    for attempt in range(1, 5):
        af = f"volume={gain:.2f}dB" if gain else "anull"
        run([FF,"-y","-hide_banner","-loglevel","error","-loop","1","-framerate","30","-i",cover,
             "-i",loop,"-vf",vf,"-af",af,"-c:v","libx264","-preset","medium","-crf","20",
             "-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","256k","-ar","48000","-ac","2",
             "-t","30","-movflags","+faststart",out])
        i, tp = tp_of(out)
        if tp is None:
            print(f"  {name}: measurement failed"); break
        tpf = float(tp)
        print(f"  {name:<26} try {attempt}  gain {gain:>5.2f} dB -> {i:>7} LUFS  {tp:>7} dBTP")
        if -2.2 <= tpf <= -1.0:
            print(f"  {name:<26} OK  (post-AAC TP inside -1.0..-2.2 dBTP, {os.path.getsize(out):,} B)")
            break
        # overshoot is roughly constant per encode -> scale the correction
        need = tpf - (-1.4)          # aim for -1.4 dBTP, mid-window
        gain -= max(0.2, min(3.0, need))
