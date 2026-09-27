#!/usr/bin/env python3
"""retag_video.py — Radio-ish Lab video cover sweep (re-runnable).

For EVERY video deliverable across all 10 artists (epk/video masters, epk/mix
videos, every Instagram reel/short/repost mirror, and every platform mirror:
YouTube/Instagram/Mixcloud/Facebook/X), attaches the artist's OWN poster
(Social_Media/promo/<Artist>/cover_1080x1920.png, i.e. the same grid-of-10
promo crop piped from the lab) as the video's cover art (attached_pic) plus
the fine-print credit line. Hardlink-mirror safe (render temp + cp -f), inode-
deduped (mirrored hardlinks re-rendered once), idempotent (already-credited
videos skipped).
"""
import os, re, subprocess, tempfile, time

FF = "/Users/bernie/Downloads/ffmpeg"
BASE = "/Users/bernie/Movies/Radio-ish"
PROMO = os.path.join(BASE, "Social_Media", "promo")
TMPD = "/var/folders/j6/7pnzn2kd2mlfr19zxcv1nq680000gn/T/opencode"
CREDIT = ("Produced by Agent Mgumbe Studio and Developed by Erwin Schrödinger's "
          "Breakfast for Before Hotel Management (B4) · Radio-ish Lab")

ARTISTS = [
    ("Alexander Zwo", ["alex", "zwo", "zwo"]),
    ("Bernie", ["bernie", "bernie"]),
    ("Dikier", ["dikier", "dikier"]),
    ("DJ Unknown", ["dj unknown", "dj_unknown", "djunknown", "unknown"]),
    ("El Djemba", ["el djemba", "el_djemba", "djemba", "djemba"]),
    ("Habib", ["habib", "habib"]),
    ("Maya", ["maya", "maya"]),
    ("SDKZ", ["sdkz", "sdkz"]),
    ("Parisa", ["parisa", "parisa", "parisa"]),
    ("Mundz", ["mundz", "mundz"]),
]

def resolve(p):
    lp = p.lower()
    for name, toks in ARTISTS:
        if any(t in lp for t in toks):
            cv = os.path.join(PROMO, name, "cover_1080x1920.png")
            if os.path.isfile(cv):
                return cv
    return None

SEEN = set()

def render(p):
    if not p.lower().endswith((".mp4", ".mov", ".m4v")):
        return
    cv = resolve(p)
    if not cv:
        print("  [skip:no-cover] %s" % os.path.basename(p))
        return
    ino = os.lstat(p).st_ino
    if ino in SEEN:
        print("  [skip:dup-inode] %s" % os.path.basename(p))
        return
    SEEN.add(ino)
    try:
        out = subprocess.check_output([FF, "-hide_banner", "-nostats", "-i", p],
                                      stderr=subprocess.STDOUT, text=True)
        if "Produced by Agent Mgumbe Studio" in out:
            print("  [skip:already] %s" % os.path.basename(p))
            return
    except Exception:
        pass
    tmp = os.path.join(TMPD, "_vid_%d.mp4" % abs(hash(p)))
    r = subprocess.call([FF, "-y", "-hide_banner", "-nostats", "-i", p, "-i", cv,
         "-map", "0", "-map", "1:v", "-c:v", "copy", "-c:a", "copy",
         "-c:v:1", "mjpeg", "-disposition:v:1", "attached_pic",
         "-metadata:s:v:1", "title=Album cover",
         "-metadata:s:v:1", "comment=Cover (front)",
         "-metadata", "comment=" + CREDIT,
         "-metadata", "producer=Agent Mgumbe Studio",
         "-metadata", "developer=Erwin Schrödinger's Breakfast",
         "-metadata", "publisher=Before Hotel Management (B4)",
         tmp],
        stdout=open(os.devnull, "wb"), stderr=subprocess.DEVNULL)
    if os.path.exists(tmp):
        with open(tmp, "rb") as src, open(p, "wb") as dst:
            dst.write(src.read())
        os.remove(tmp)
        print("  [ok] %s" % os.path.basename(p))

def main():
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if not d.startswith((".", "_"))]
        for fn in files:
            render(os.path.join(root, fn))

if __name__ == "__main__":
    main()
