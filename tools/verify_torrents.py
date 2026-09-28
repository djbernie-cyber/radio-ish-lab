#!/usr/bin/env python3
"""Independently verify the generated .torrent files.

make_torrents.py hand-rolls the bencode and the piece layout, so "it wrote a
file" is not evidence the torrent is any good. This decodes each .torrent back
into a structure, rebuilds the byte stream exactly as a client would from the
file list, re-hashes every piece with SHA-1, and compares against the digest
stored in the metainfo. Any disagreement means the torrent is broken.

Also re-checks the privacy flags, because a torrent that quietly lost
private=1 or picked up an announce URL would put unreleased masters into the
public DHT swarm.
"""
import hashlib, os, sys

TORR = os.path.expanduser("~/Radio-ish-torrents")
BASE = "/Users/bernie/Movies/Radio-ish"
PIECE = 4 * 1024 * 1024

def bdecode(b, i=0):
    c = b[i:i+1]
    if c == b"i":
        j = b.index(b"e", i); return int(b[i+1:j]), j+1
    if c == b"l":
        i += 1; out = []
        while b[i:i+1] != b"e":
            v, i = bdecode(b, i); out.append(v)
        return out, i+1
    if c == b"d":
        i += 1; out = {}
        while b[i:i+1] != b"e":
            k, i = bdecode(b, i); v, i = bdecode(b, i); out[k] = v
        return out, i+1
    j = b.index(b":", i); n = int(b[i:j]); s = j+1
    return b[s:s+n], s+n

def verify(path):
    raw = open(path, "rb").read()
    meta, _ = bdecode(raw)
    info = meta[b"info"]
    problems = []

    # --- privacy checks: these matter more than the hashes ---
    if info.get(b"private") != 1:
        problems.append("private flag missing -> DHT/PEX would expose this to the swarm")
    if b"announce" in meta or b"announce-list" in meta:
        problems.append("announce list present -> content is registered with a tracker")

    piece_len = info[b"piece length"]
    stored = info[b"pieces"]
    files = info[b"files"]
    name = info[b"name"].decode()
    # A peer creates ./<name>/ and lays files out relative to it. Resolve against
    # the root unless <name> is a real directory inside it (whole-tree torrents
    # are named after the root itself, so they resolve one level up).
    base = os.path.join(BASE, name) if os.path.isdir(os.path.join(BASE, name)) else BASE

    # --- rebuild the byte stream exactly as a client would ---
    h = hashlib.sha1(); got = bytearray(); n = 0; buf = b""
    for fe in files:
        parts = [x.decode() for x in fe[b"path"]]
        p = os.path.join(base, *parts)
        if not os.path.isfile(p):
            problems.append(f"missing source file: {p}")
            return name, problems, 0, len(files), len(stored)//20
        sz = os.path.getsize(p)
        if sz != fe[b"length"]:
            problems.append(f"length mismatch: {p} {sz} != {fe[b'length']}")
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(1 << 22), b""):
                buf += c
                while len(buf) >= piece_len:
                    got += hashlib.sha1(buf[:piece_len]).digest(); buf = buf[piece_len:]
        n += sz
    if buf:
        got += hashlib.sha1(buf).digest()

    if bytes(got) != stored:
        problems.append(f"PIECE HASH MISMATCH ({len(stored)} stored vs {len(got)} computed)")
    return name, problems, n, len(files), len(stored)//20

print("=== verifying generated torrents ===")
torrs = sorted(f for f in os.listdir(TORR) if f.endswith(".torrent"))
bad = 0; total = 0
for t in torrs:
    name, problems, n, nfiles, npieces = verify(os.path.join(TORR, t))
    total += n
    if problems:
        bad += 1
        print(f"  FAIL {t}")
        for p in problems: print(f"        {p}")
    else:
        print(f"  OK   {name:<24} {nfiles:>4} files  {n/2**30:>6.1f} GiB  {npieces:>5} pieces  "
              f"private=1, unannounceable")
print(f"\n  {len(torrs)-bad}/{len(torrs)} torrents valid, {total/2**30:.1f} GiB covered")
sys.exit(1 if bad else 0)
