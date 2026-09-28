#!/usr/bin/env python3
"""SHA-256 manifest of every media file in the project.

This is the actual immutability guarantee. Telegram (and any object store) holds
copies that can be deleted or edited; a manifest of SHA-256 digests committed to
GitHub is what proves later that the bytes still match. Re-run to detect any
silent edit, re-encode or corruption.

Sorted for a stable manifest, and written with relative paths so it can be
verified from the project root on any machine.
"""
import hashlib, os, sys, time, datetime

R = "/Users/bernie/Movies/Radio-ish"
EXT = (".mp3", ".wav", ".mp4", ".mov", ".aiff", ".aif", ".flac", ".m4a",
       ".png", ".jpg", ".jpeg",
       # DAW sessions: irreplaceable source for every render. Without these the
       # audio restores but no session can be reopened or re-edited.
       ".asd", ".als", ".flp", ".nksr", ".rpp", ".mxt")
OUT = f"{R}/qc/SeasonOne_Media_SHA256SUMS"
os.makedirs(f"{R}/qc", exist_ok=True)

def sha(p, buf=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(buf), b""):
            h.update(c)
    return h.hexdigest()

files = []
for root, dirs, names in os.walk(R):
    dirs[:] = [d for d in dirs if d not in (".git", "Archive", "node_modules", "__pycache__")]
    for n in names:
        if n.lower().endswith(EXT):
            p = os.path.join(root, n)
            files.append((os.path.relpath(p, R), p))
files.sort()

t0 = time.time(); done = 0; n = len(files); total = 0
lines = ["# Radio-ish Lab — media SHA-256 manifest",
         f"# generated {datetime.date.today().isoformat()} by tools/media_manifest.py",
         f"# {n} files — verify with: shasum -a 256 -c qc/SeasonOne_Media_SHA256SUMS",
         "# paths are relative to the project root; the manifest is the immutability",
         "# guarantee, the copies are not. Re-run to detect silent edits.",
         ""]
for rel, p in files:
    try:
        d = sha(p)
    except OSError as e:
        print(f"  [skip] {rel}: {e}", flush=True); continue
    sz = os.path.getsize(p); total += sz; done += 1
    lines.append(f"{d}  {rel}")
    if done % 25 == 0 or done == n:
        el = time.time() - t0
        print(f"  {done}/{n}  {total/2**30:.1f} GiB  {el:.0f}s elapsed", flush=True)

with open(OUT, "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"\n  wrote {OUT} — {done} files, {total/2**30:.1f} GiB, {time.time()-t0:.0f}s")
