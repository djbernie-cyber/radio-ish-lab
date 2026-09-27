# RELEASE CHECKLIST — Radio-ish Lab · Season One EPK

Generated from real on-disk state. Every box below is either **done (verified)** or **open (named gap)**.

## 1 · Toolchain
- [x] `ffmpeg` installed — `~/bin/ffmpeg`, static **arm64**, `ffmpeg version 4.4` — verified with `-version`
- [x] `ffprobe` installed — `~/bin/ffprobe`, static **arm64**, `ffprobe version n4.4.1` — verified with `-version`
- [x] No system install — both binaries live in `~/bin`, nothing written to `/usr/local` or `/opt`
- [x] Checksums recorded — SHA-256 of both binaries in `qc/SeasonOne_EPK_SHA256SUMS`
- [x] `ffmpeg` has the filters the EPK needs: `drawtext` (fine-print burn-in), `overlay`, `scale`

## 2 · Audio — seamless 30 s EPK loop per artist
- [x] 12/12 loops built from **real** audio on disk (multitrack master, or mastered EPK mix where no master exists)
- [x] 12/12 exact **30.000000 s** (verified with `afinfo` + `ffprobe`)
- [x] 12/12 **48 kHz / 24-bit stereo**
- [x] 12/12 **seamless** — 0.5 s equal-power crossfade, file ends on the sample it begins with; measured seam is at or below each track's own natural sample step
- [ ] **Loudness QC** — peak ≤ ~0 dBFS, −12…−16 LUFS per MASTER_README. Not run: no loudness tool present. **Blocks press release.**

## 3 · Images — cover standard
- [x] 11/12 artists: `cover_1080x1920_bw.png`, 1080×1920, **black background + white graphics**
- [x] 1/12 (Schrödinger's Breakfast): no artwork on file → typographic title card, same 1080×1920 black-bg/white-type standard
- [ ] **Schrödinger's Breakfast real artwork** — drop into `epk/promo/` and re-render to replace the card

## 4 · Video — EPK mp4 per artist
- [x] 12/12 rendered — `h264` 1080×1920 `yuv420p` + `aac` 48 kHz stereo, 30.000 s
- [x] `+faststart` for streaming
- [x] **Fine print burned in** (artist, style/genres, `RADIO-ISH LAB · SEASON ONE`, `30s seamless loop · 1080x1920`)
- [x] Every stream/duration claim verified with `ffprobe`, not assumed

## 5 · Text — fine-print publications
- [x] 12/12 `epk/text/FINE_PRINT_<TAG>_B4.md` on disk (500–800 B each)
- [x] Genres sourced from `MASTER_README.md`, not invented
- [x] **Bernie tightened** — `Vinyl Classics / Deep House`, leading with Vinyl Classics so it no longer collides with SDKZ's Deep House
- [ ] **Yogo + Mundz genres** — no roster row exists; fine print currently reads `Season One`. Supply tags → re-render fine print + mp4

## 6 · Production publications
- [x] `qc/SeasonOne_EPK_qc.md` — full stats table + 13 checks + named gaps
- [x] `qc/SeasonOne_EPK_SHA256SUMS` — SHA-256 of every deliverable
- [x] This release checklist
- [ ] **`MASTER_README.md` roster** — add Yogo (new artist) and Mundz (on disk, never listed). Roster header says 9 but 12 artists now ship.

## 7 · Press release gate
- [ ] Loudness QC (see §2)
- [ ] Yogo + Mundz genre tags (see §5)
- [ ] MASTER_README roster updated (see §6)
- [ ] Per-artist `epk/index.md` press one-pagers — the human-readable EPK MASTER_README points press to; not regenerated in this pass
- [ ] Social_Media 9:16 clips + platform uploads (Mixcloud / SoundCloud / Bandcamp / Instagram) — untouched in this pass
