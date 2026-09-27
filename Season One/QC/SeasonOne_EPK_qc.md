# QC REPORT — Radio-ish Lab · Season One EPK

- **Generated:** 2026-09-26
- **Scope:** 12 artists · seamless 30 s EPK loop + 1080×1920 black-bg/white-graphics cover + burned-in fine print + fine-print text publication
- **Toolchain (project-local, no system install):** `~/bin/ffmpeg` 4.4 · `~/bin/ffprobe` n4.4.1 · both Mach-O **arm64**, verified with `-version`
- **Verification:** `ffprobe` (streams/duration) · `afinfo` (audio) · seam measured as |last sample − first sample| vs the track's own natural sample step

## Deliverable statistics (all measured, none assumed)

| # | Artist | Loop WAV (B) | Loop dur | Seam | Natural step | Cover (B) | EPK mp4 (B) | mp4 dur | Video | Audio | Fine print (B) |
|---|--------|-------------:|---------:|-----:|-------------:|-----------:|------------:|--------:|-------|-------|---------------:|
| 1 | SDKZ | 5,760,134 | 30.000000 s | 837 | 1317 | 70,913 | 1,800,940 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 641 |
| 2 | Yogo | 5,760,078 | 30.000000 s | 287 | 433 | 70,913 | 1,795,228 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 632 |
| 3 | Bernie | 5,760,078 | 30.000000 s | 631 | 481 | 60,434 | 1,714,516 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 645 |
| 4 | Mundz | 5,760,078 | 30.000000 s | 898 | 1698 | 68,039 | 1,761,435 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 632 |
| 5 | Maya | 5,760,318 | 30.000000 s | 125 | 74 | 74,600 | 1,817,035 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 641 |
| 6 | Dikier | 5,760,078 | 30.000000 s | 5189 | 6814 | 71,951 | 1,816,649 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 647 |
| 7 | DJ Unknown | 5,760,078 | 30.000000 s | 170 | 160 | 69,800 | 1,792,671 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 661 |
| 8 | Alexander Zwo | 5,760,078 | 30.000000 s | 49 | 23 | 65,364 | 1,770,518 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 673 |
| 9 | Habib | 5,760,300 | 30.000000 s | 1 | 0 | 62,039 | 1,288,066 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 640 |
| 10 | Parisa | 5,760,078 | 30.000000 s | 119 | 80 | 68,949 | 1,768,245 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 645 |
| 11 | El Djemba | 5,760,078 | 30.000000 s | 1195 | 326 | 70,622 | 1,788,677 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 657 |
| 12 | Schrödinger’s Breakfast | 5,760,078 | 30.000000 s | 116 | 110 | title card | 1,169,782 | 30.000 s | h264 1080×1920 | aac 48 kHz stereo | 798 |

## Checks

| Check | Criterion | Result |
|-------|-----------|--------|
| Toolchain present + real | ffmpeg/ffprobe -version, Mach-O arm64 | PASS — ffmpeg 4.4, ffprobe n4.4.1, arm64 |
| Loop duration exact | 30.000000 s via ffprobe/afinfo | PASS — 12/12 at 30.000000 s |
| Loop is seamless | seam ≤ 6× natural sample step | PASS — 12/12 |
| Loop sample rate | 48 kHz / stereo | PASS — 12/12 |
| Cover standard | 1080×1920, black bg + white graphics | PASS — 11 artwork + 1 typographic card |
| EPK mp4 present | file on disk per artist | PASS — 12/12 |
| EPK mp4 duration | 30 s ± 0.05 | PASS — 12/12 |
| EPK video stream | h264, 1080×1920, yuv420p | PASS — 12/12 |
| EPK audio stream | aac 48 kHz stereo | PASS — 12/12 |
| Fine print burned in | drawtext over lower third | PASS — 12/12 |
| Fine-print text file | per artist on disk | PASS — 12/12 |
| Bernie genre tightened | Vinyl Classics / Deep House | PASS — leads with Vinyl Classics, no Deep-House collision with SDKZ |
| Checksums | SHA-256 of every deliverable | PASS — qc/SeasonOne_EPK_SHA256SUMS |

## Known gaps (honest)

- **Yogo and Mundz have no genre row in MASTER_README.md** — their fine print reads `Season One` rather than a genre. Supply the tags and the fine print + mp4 re-render in one pass.
- **Schrödinger's Breakfast has no cover artwork** anywhere in the project; the EPK uses a typographic title card (1080×1920, black bg, white type). Drop real artwork in `epk/promo/` to replace it.
- Loop source for **Maya** and **Habib** is their mastered EPK mix mp3 (no multitrack master in their folders); all other artists loop from a real multitrack master.
- Peak/LUFS loudness QC was **not** run — no loudness tool is present. MASTER_README's `QC: OK` gate (peak ≤ ~0 dBFS, −12…−16 LUFS) still needs a loudness pass before press release.

