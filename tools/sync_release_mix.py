#!/usr/bin/env python3
"""Sync (not just refresh) Season One/Artists/<artist>/Mix against the working masters.

The relink step inside standardise_masters.py only re-pointed filenames that were
already present in the Season One Mix folder. That left two real breaks:

  Mundz            _mix.mp3 was absent at tree-build time, so it was never linked
  Schrodinger's     the folder held only the old lab_session file, so none of the
  Breakfast         three new standardised masters were ever linked

So this does a real sync: the Season One Mix folder must contain EXACTLY the
canonical house-matrix trio, each a hardlink to the artist working copy. Anything
else found there is reported and moved to the archive rather than deleted, per
the project rule that nothing is ever removed outright.

Nothing here rewrites audio or touches inode 0 links; removing a hardlink only
drops that one name, the working copy always remains.
"""
import json, os, shutil, datetime

R     = "/Users/bernie/Movies/Radio-ish"
ARCH  = f"{R}/Archive/2026-09-26_superseded/stray_release_files"
STEM = {"SDKZ":"sdkz","Yogo":"yogo","Bernie":"bernie","Mundz":"mundz","Maya":"maya",
        "Dikier":"dikier","DJ Unknown":"dj_unknown","Alexander Zwo":"alexander_zwo",
        "Habib":"habib","Parisa":"parisa","El Djemba":"el_djemba",
        "Schrödinger’s Breakfast":"schrodingers_breakfast"}
CANON = ("_mix.mp3", "_mix_hq.mp3", "_mix_epk.mp3")

log = open("/tmp/sdkz_bw/mixsync.log", "a", buffering=1)
def say(m): print("  " + m, flush=True); log.write(m + "\n")

say(f"\n=== Season One mix sync — {datetime.date.today().isoformat()} ===")
linked = strays = missing = 0
problems = []

for artist, stem in STEM.items():
    work = f"{R}/{artist}/epk/mix"
    rel  = f"{R}/Season One/Artists/{artist}/Mix"
    if not os.path.isdir(work):
        problems.append(f"{artist}: no working epk/mix"); continue
    os.makedirs(rel, exist_ok=True)
    want = {f"{stem}{s}": f"{work}/{stem}{s}" for s in CANON}

    # 1. anything in the release folder that is not part of the matrix -> archive
    for f in sorted(os.listdir(rel)):
        if f in want: continue
        src = f"{rel}/{f}"
        if not os.path.isfile(src): continue
        ad = f"{ARCH}/{artist}"; os.makedirs(ad, exist_ok=True)
        shutil.move(src, f"{ad}/{f}")
        strays += 1
        say(f"{artist:<24} stray '{f}' -> archive (working copy untouched)")

    # 2. ensure each canonical name exists and is the SAME inode as the working copy
    for name, wsrc in want.items():
        t = f"{rel}/{name}"
        if not os.path.isfile(wsrc):
            missing += 1; problems.append(f"{artist}: working master {name} absent")
            say(f"{artist:<24} ** MISSING WORKING MASTER ** {name}"); continue
        if os.path.islink(t) or (os.path.isfile(t) and not os.path.samefile(wsrc, t)):
            if os.path.lexists(t): os.remove(t)
        if not os.path.lexists(t):
            os.link(wsrc, t)            # same filesystem, so a hardlink always works
        if os.stat(wsrc).st_ino == os.stat(t).st_ino:
            linked += 1
        else:
            problems.append(f"{artist}: {name} not a hardlink after sync")

say(f"linked/verified {linked}/{linked+missing+len(problems)} canonical masters, "
    f"archived {strays} stray release file(s), {missing} missing working master(s)")

# final independent verification straight off disk
bad = []
for artist, stem in STEM.items():
    work = f"{R}/{artist}/epk/mix"; rel = f"{R}/Season One/Artists/{artist}/Mix"
    for s in CANON:
        w, t = f"{work}/{stem}{s}", f"{rel}/{stem}{s}"
        if not (os.path.isfile(w) and os.path.isfile(t)):
            bad.append(f"{artist}/{stem}{s}: absent"); continue
        if os.stat(w).st_ino != os.stat(t).st_ino:
            bad.append(f"{artist}/{stem}{s}: not a hardlink")
say("VERIFY: all 36 mix hardlinks intact" if not bad
    else "VERIFY: " + "; ".join(bad))
for p in problems: say("  PROBLEM " + p)
json.dump({"linked": linked, "strays_archived": strays, "missing": missing,
           "problems": problems, "bad": bad},
          open("/tmp/sdkz_bw/mixsync.json", "w"), indent=1, ensure_ascii=False)
