#!/usr/bin/env python3
"""
retag_audio.py — Radio-ish Lab standardized audio metadata sweep (re-runnable).

For EVERY mp3 deliverable across all 10 artists (epk/audio, epk/mix, epk/promo,
EPK_Project/<Artist> segments, and every platform mirror — Bandcamp, SoundCloud,
Mixcloud, Instagram, Tracksource — plus promo and season folders),
embeds the ARTIST'S OWN POSTER (Social_Media/promo/<Artist>/cover_1080x1920.png)
as attached cover artwork, plus the standardized fine-print credits:

   Produced by Agent Mgumbe Studio · Developed by Schrödinger's Breakfast
   for Before Hotel Management (B4)

Writes to a temp file then cp -f back so hardlinked mirror groups remain in
sync (inode preserved), and skips inodes already handled so mirrored/hardlinked
duplicates are only re-rendered once. Idempotent / re-runnable (files already
carrying the credit comment are skipped).
"""
import os, re, subprocess, tempfile, time

FF    = "/Users/bernie/Downloads/ffmpeg"
BASE  = "/Users/bernie/Movies/Radio-ish"
TMPD  = "/var/folders/j6/7pnzn2kd2mlfr19zxcv1nq680000gn/T/opencode"
PROMO = os.path.join(BASE, "Social_Media", "promo")

CREDIT = ("Produced by Agent Mgumbe Studio and Developed by Schr\u00f6dinger's "
          "Breakfast for Before Hotel Management (B4)")

# (folder token used to key the artist, exact real folder name, real artist name)
ARTISTS = [
    ("Alexander Zwo", "Alexander Zwo", "Alexander Zwo"),
    ("Bernie",        "Bernie",        "Bernie"),
    ("Dikier",        "Dikier",        "Dikier"),
    ("DJ Unknown",    "DJ Unknown",    "DJ Unknown"),
    ("El Djemba",     "El Djemba",     "El Djemba"),
    ("Habib",         "Habib",         "Habib"),
    ("Maya",          "Maya",          "Maya"),
    ("Mundz",         "Mundz",         "Mundz"),
    ("Parisa",        "Parisa",        "Parisa"),
    ("SDKZ",          "SDKZ",          "SDKZ"),
]

SEEN_AUDIO = set()

def cover_for(path):
    lp = path.lower()
    for token, folder, _ in ARTISTS:
        if token.lower() in lp:
            cv = os.path.join(PROMO, folder, "cover_1080x1920.png")
            if os.path.isfile(cv):
                return cv
    return None

def run(cmd):
    subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def render(path):
    """Re-render <file> with its artist's own poster as cover + credits, in place."""
    cover = cover_for(path)
    if not cover:
        print("  [skip:no-cover-for-artist] %s" % os.path.basename(path))
        return
    ino = os.lstat(path).st_ino
    if ino in SEEN_AUDIO:
        print("  [skip:hardlink-dup] %s" % os.path.basename(path))
        return
    # already done? (idempotent)
    try:
        meta = subprocess.check_output(
            [FF, "-hide_banner", "-nostats", "-i", path, "-f", "ffmetadata", "-"],
            stderr=subprocess.DEVNULL).decode("utf-8", "ignore")
        if "Schr\u00f6dinger's Breakfast" in meta and "Before Hotel Management (B4)" in meta:
            print("  [skip:already-tagged] %s" % os.path.basename(path))
            return
    except Exception:
        pass
    SEEN_AUDIO.add(ino)
    tmp = os.path.join(TMPD, "_retag_%d.mp3" % abs(hash(path)))
    ok = run([FF, "-y", "-hide_banner", "-nostats", "-i", path, "-i", cover,
              "-map", "0:a", "-map", "1:v", "-c:a", "copy", "-c:v", "mjpeg",
              "-disposition:v", "attached_pic", "-id3v2_version", "3",
              "-metadata", "producer=Agent Mgumbe Studio",
              "-metadata", "developer=Schr\u00f6dinger's Breakfast",
              "-metadata", "publisher=Before Hotel Management (B4)",
              "-metadata", "comment=" + CREDIT,
              "-metadata:s:v", "title=Album cover",
              "-metadata:s:v", "comment=Cover (front)",
              tmp])
    if os.path.exists(tmp):
        with open(tmp, "rb") as src, open(path, "wb") as dst:
            dst.write(src.read())
        os.remove(tmp)
        print("  [retagged] %s" % os.path.basename(path))

def main():
    count = 0
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if not d.startswith((".", "_", "Social_Media/Tracksource"))]
        for fn in files:
            if fn.lower().endswith(".mp3"):
                render(os.path.join(root, fn))
                count += 1
    print("== swept %s candidate mp3s ==" % count)

if __name__ == "__main__":
    main()
