# RELEASE CHECKLIST — Radio-ish Lab · Season One

Generated from real on-disk state. Every box below is either **done (verified)** or **open (named gap)**.

## 1 · Toolchain
- [x] `ffmpeg` installed — `~/bin/ffmpeg`, static **arm64**, `ffmpeg version 4.4` — verified with `-version`
- [x] `ffprobe` installed — `~/bin/ffprobe`, static **arm64**, `ffprobe version n4.4.1` — verified with `-version`
- [x] `gh` installed — `~/bin/gh`, official release **arm64**, v2.101.0 — archive SHA-256 verified
- [x] No system install — both binaries live in `~/bin`, nothing written to `/usr/local` or `/opt`
- [x] Checksums recorded — SHA-256 of both binaries in `qc/SeasonOne_EPK_SHA256SUMS`
- [x] `ffmpeg` has the filters the EPK needs: `drawtext` (fine-print burn-in), `overlay`, `scale`

## 2 · Audio — seamless 30 s EPK loop per artist
- [x] 12/12 loops built from **real** audio on disk (multitrack master, or mastered EPK mix where no master exists)
- [x] 12/12 exact **30.000000 s** (verified with `afinfo` + `ffprobe`)
- [x] 12/12 **48 kHz / 24-bit stereo**
- [x] 12/12 **seamless** — 0.5 s equal-power crossfade, file ends on the sample it begins with; measured seam is at or below each track's own natural sample step
- [x] **Loudness QC — DONE.** All 12 loops at **-14 LUFS / -1.0 dBTP**; every EPK video inside the
      `-12…-16 LUFS` gate with true peak below 0 dBTP. `qc/SeasonOne_EPK_qc.md` — 120/120 checks.
      Three defects found and fixed by this pass: three loops clipped past 0 dBTP, six sat outside
      the LUFS gate, and **Habib's loop had been cut from a silent 30 s window** near the head of
      its mix (effectively silent at -72 dBFS). All loops now 24-bit, matching the published spec.

## 3 · Full-length mixes — house standardisation
- [x] All 12 masters standardised to **one gain and one EQ** — `-14 LUFS`, true peak below 0 dBTP
- [x] Identical chain for every artist, so the catalogue is genuinely consistent, not just nominally
- [x] Pioneer XDJ-RX3 EQ for 11 artists; gentler Denon variant for DJ Unknown
- [x] `<artist>_mix.mp3` + `_mix_hq.mp3` — 48 kHz/320 kbps, **bit-identical**, encoded once
- [x] `<artist>_mix_epk.mp3` — 44.1 kHz/320 kbps, rendered from the same intermediate as the masters
- [x] **True-peak repair.** First pass left 4 masters above 0 dBTP (El Djemba +1.27, Bernie +0.83,
      Schrödinger +0.74, DJ Unknown +0.09) because the ceiling formula hit its -1.5 dB floor and
      heavily-limited material overshoots once MP3 inter-sample peaks count. All four re-rendered
      from the archived originals with the ceiling lowered by the overshoot measured.
- [x] All pre-standardisation masters preserved, never deleted — `Archive/2026-09-26_superseded/mixes/`
- [x] `qc/SeasonOne_Mix_qc.md` — per-artist trim, loudness, true peak, limiter ceiling — **96/96 checks**
- [ ] **Ear check on the three quiet sources** — Habib, Maya and Schrödinger's Breakfast have very
      quiet masters, so normalising to -14 LUFS lifts their noise floor

## 4 · Images — cover standard
- [x] 11/12 artists: `cover_1080x1920_bw.png`, 1080×1920, **black background + white graphics**
- [x] 1/12 (Schrödinger's Breakfast): no artwork on file → typographic title card, same 1080×1920 black-bg/white-type standard
- [ ] **Schrödinger's Breakfast real artwork** — drop into `epk/promo/` and re-render to replace the card
- [ ] **Yogo-specific cover** — currently a copy of the SDKZ cover

## 5 · Video — EPK mp4 per artist
- [x] 12/12 rendered — `h264` 1080×1920 `yuv420p` + `aac` 48 kHz stereo, 30.000 s
- [x] `+faststart` for streaming
- [x] **Fine print burned in** (artist, style/genres, `RADIO-ISH LAB · SEASON ONE`, `30s seamless loop · 1080x1920`)
- [x] Every stream/duration claim verified with `ffprobe`, not assumed
- [x] Post-AAC true-peak repair applied where the encode overshot (Bernie, Schrödinger)

## 6 · Text — press publications
- [x] 12/12 `epk/text/FINE_PRINT_<TAG>_B4.md` on disk (500–800 B each)
- [x] Genres sourced from `MASTER_README.md`, not invented
- [x] **Bernie tightened** — `Vinyl Classics / Deep House`, leading with Vinyl Classics so it no longer collides with SDKZ's Deep House
- [x] **12/12 press one-pagers** — `epk/index.md` hardlinked into `Season One/Artists/<Artist>/Press/`.
      Mundz, Yogo and Schrödinger were missing these; created in this pass.
- [ ] **Yogo + Mundz genres** — no confirmed roster row; fine print reads `Season One`. Supply tags → re-render fine print + mp4

## 7 · Release tree integrity
- [x] **96/96** files in `Season One/` verified as hardlinks to their working originals
- [x] 36/36 mix hardlinks intact (`mix`, `mix_hq`, `mix_epk` × 12)
- [x] 4/4 top-level Docs hardlinks intact
- [x] **Two breaks found and fixed.** The relink step only refreshed filenames already present, so
      it never added missing ones: Mundz had no `_mix.mp3` in the release tree, and Schrödinger's
      Breakfast had none of the three masters. `tools/sync_release_mix.py` now syncs rather than
      refreshes, and archives (never deletes) non-matrix files it finds.
- [x] No tracked file exceeds GitHub's 100 MB limit — push is safe
- [x] All 22 top-level folders accounted for; no empty or orphaned directories

## 8 · Production publications
- [x] `qc/SeasonOne_EPK_qc.md` — loop/video stats table + 13 checks + named gaps
- [x] `qc/SeasonOne_Mix_qc.md` — mix house standard + per-artist measured results
- [x] `qc/SeasonOne_EPK_SHA256SUMS` — **62 entries**: 12 loops + 12 EPK videos + 12 covers +
      12 fine prints + 12 press index pages + both binaries — all 62 verified OK
- [x] This release checklist
- [x] **`MASTER_README.md` roster** — all 12 artists listed, header corrected from 9

## 9 · Press release gate
- [x] Loop loudness QC (§2)
- [x] Mix house standardisation (§3)
- [x] MASTER_README roster updated (§8)
- [x] Per-artist press one-pagers (§6)
- [x] Release tree integrity, no breaks or unhandled folders (§7)
- [ ] Yogo + Mundz genre tags (§6) — blocks final fine print
- [ ] Yogo cover art and Schrödinger's Breakfast artwork (§4)
- [ ] Ear check on the three quiet-source masters (§3)
- [ ] Social_Media 9:16 clips for the other 11 artists + all platform uploads
      (Mixcloud / SoundCloud / Bandcamp / Instagram) — Yogo's clips are done
- [ ] GitHub repo published — `gh` is installed but not yet authenticated
