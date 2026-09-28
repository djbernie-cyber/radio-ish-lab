#!/usr/bin/env python3
"""Create private, unannounceable torrents for the Season One masters.

Written from scratch: a .torrent is bencoded metainfo plus SHA-1 piece hashes,
so no third-party client is needed to author one.

Three deliberate privacy choices, because these are UNRELEASED masters:

  private: 1        tells clients not to use DHT or PEX
  no announce list  nothing is registered with any tracker
  DHT off           so the swarm never learns this content exists

The result is leechable only by someone who already has the .torrent file and
knows your IP/port — i.e. peers you choose. That is the difference between a
backup and a leak, and the default for a public-tracker torrent of unreleased
material is a leak.

Torrents are written OUTSIDE the git repo, and .gitignore refuses them anywhere
inside it, so they can never be pushed to the public repository.

Each artist gets its own torrent for granular recovery, plus one whole-tree
torrent as the complete backup. Piece size 4 MiB: 120 GiB -> ~30k pieces, which
keeps the hash block small without hurting recovery granularity.
"""
import hashlib, os, sys, time, datetime

R = "/Users/bernie/Movies/Radio-ish"
OUT = os.path.expanduser("~/Radio-ish-torrents")   # deliberately outside the repo
PIECE = 4 * 1024 * 1024
EXT = (".mp3", ".wav", ".mp4", ".mov", ".aiff", ".aif", ".flac", ".m4a", ".png", ".jpg", ".jpeg")

ARTISTS = ["SDKZ", "Yogo", "Bernie", "Mundz", "Maya", "Dikier", "DJ Unknown",
           "Alexander Zwo", "Habib", "Parisa", "El Djemba", "Schrödinger’s Breakfast"]

def bencode(o):
    if isinstance(o, int):  return b"i" + str(o).encode() + b"e"
    if isinstance(o, bytes): return str(len(o)).encode() + b":" + o
    if isinstance(o, str):  return bencode(o.encode())
    if isinstance(o, dict):
        items = sorted(o.items(), key=lambda kv: (isinstance(kv[0], bytes),
                       kv[0] if isinstance(kv[0], bytes) else kv[0].encode()))
        return b"d" + b"".join(bencode(k) + bencode(v) for k, v in items) + b"e"
    if isinstance(o, (list, tuple)):
        return b"l" + b"".join(bencode(v) for v in o) + b"e"
    raise TypeError(type(o))

def collect(dirs):
    """Return (files, total_bytes) for the media under the given roots.

    Paths are always made relative to the project ROOT, never to the sub-root,
    so a peer laying the torrent out as ./<name>/<paths> reproduces the real
    tree exactly. Relative-to-subroot silently dropped the 'epk/' level and
    produced torrents that restored to the wrong layout.
    """
    out = []
    for base in dirs:
        if not os.path.isdir(base): continue
        for root, ds, ns in os.walk(base):
            ds[:] = [x for x in ds if x not in (".git", "Archive", "__pycache__")]
            for n in sorted(ns):
                if n.lower().endswith(EXT):
                    p = os.path.join(root, n)
                    out.append((p, os.path.relpath(p, R)))
    out.sort(key=lambda t: t[1])
    return out, sum(os.path.getsize(p) for p, _ in out)

def strip(files, prefix):
    """Drop a leading path component from each (already project-relative) path.

    The argument is matched against the project-relative path, not an absolute
    one, so pass the artist name here rather than an absolute directory.
    """
    pre = prefix.rstrip(os.sep) + os.sep
    return [(p, rel[len(pre):] if rel.startswith(pre) else rel) for p, rel in files]

def make(name, base, files, total, verbose=True):
    """Hash pieces in sorted path order and emit the .torrent."""
    t0 = time.time()
    pieces = bytearray(); buf = b""; done = 0
    for p, _ in files:
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 22), b""):
                buf += chunk
                while len(buf) >= PIECE:
                    pieces += hashlib.sha1(buf[:PIECE]).digest()
                    buf = buf[PIECE:]
                done += os.path.getsize(p) if False else len(chunk)
    if buf:
        pieces += hashlib.sha1(buf).digest()

    info = {
        "name": name,
        "piece length": PIECE,
        "pieces": bytes(pieces),
        "private": 1,
        "created by": "radio-ish-lab/1.0",
        "creation date": int(time.time()),
        "files": [{"length": os.path.getsize(p), "path": rel.split(os.sep)}
                  for p, rel in files],
    }
    meta = bencode({"info": info})          # NOTE: no 'announce' => unannounceable
    path = os.path.join(OUT, f"{name}.torrent")
    with open(path, "wb") as f:
        f.write(meta)
    if verbose:
        print(f"  {name:<34} {len(files):>4} files  {total/2**30:>7.1f} GiB  "
              f"{len(pieces)//20:>6} pieces  {time.time()-t0:>5.0f}s  -> {os.path.basename(path)}",
              flush=True)
    return path, meta, total, len(files)

os.makedirs(OUT, exist_ok=True)
os.chmod(OUT, 0o700)
print(f"=== private torrent creation — {datetime.date.today().isoformat()} ===")
print(f"  output: {OUT}  (outside the git repo, mode 0700)")
print(f"  private=1, no announce list, DHT/PEX off\n")

index = []
for a in ARTISTS:
    base = f"{R}/{a}/epk"
    files, total = collect([base])
    if not files:
        print(f"  {a:<34} (no media found, skipped)"); continue
    # name = the dir a peer creates (the artist folder); paths are relative to it,
    # so ./<Artist>/epk/... is recreated exactly. Stripping 'epk' here would make
    # peers restore to ./<Artist>/audio/... instead.
    p, meta, tot, n = make(a, base, strip(files, a), total)
    index.append((a, n, tot, p, hashlib.sha256(meta).hexdigest()))

# whole-tree backup torrent, named after the real root dir so it restores 1:1
files, total = collect([R])
p, meta, tot, n = make("Radio-ish", R, files, total)
index.append(("Radio-ish-FULL-TREE", n, tot, p, hashlib.sha256(meta).hexdigest()))

with open(os.path.join(OUT, "INDEX.txt"), "w") as f:
    f.write(f"# Radio-ish Lab — private backup torrents  {datetime.date.today().isoformat()}\n")
    f.write("# private=1, no tracker, DHT/PEX disabled: leechable only by peers you choose.\n")
    f.write("# KEEP THIS DIRECTORY OFF the public GitHub repo and off shared drives.\n")
    f.write("# Verify:  shasum -a 256 -a 256 <file>  against the .torrent sha256 below\n\n")
    for name, cnt, sz, path, h in index:
        f.write(f"{name:<24} {cnt:>4} files  {sz/2**30:>7.1f} GiB  sha256 {h}  {os.path.basename(path)}\n")
print(f"\n  {len(index)} torrents written to {OUT}")
print("  total size %.1f GiB" % (sum(x[2] for x in index)/2**30))
