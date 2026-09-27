# RADIO-ISH LAB — MASTER PRODUCTION INDEX

> One house, one standard. Every artist EPK follows the same architecture so any
> deliverable can be found, verified, and shipped to press or socials in minutes.
> Target quality bar: **Mixmag-grade production & delivery.**

## Artist Roster (12)

| # | Artist | Role / Style | Mix deliverables | Status |
|---|--------|--------------|------------------|--------|
| 1 | Habib | Deep house & melodic techno · 8 original tracks + DJ set | `habib_mix(_hq/_epk).mp3` | LIVE |
| 2 | Maya | Experimental ambient electronica | `maya_mix(_hq/_epk).mp3` | LIVE |
| 3 | Parisa | 2004-era nostalgic electronic | `parisa_mix(_hq/_epk).mp3` | LIVE |
| 4 | SDKZ | AfroHouse / AfroBeats / Deep House | `sdkz_mix(_hq/_clean/_epk).mp3` | LIVE |
| 5 | Dikier | Extended live techno sessions | `dikier_mix(_hq/_epk).mp3` | LIVE |
| 6 | Bernie | Vinyl Classics / Deep House · producer & co-founder · Ableton live sessions | `bernie_mix(_hq/_epk).mp3` | LIVE |
| 7 | Schrödinger's Breakfast | Garage / Bass / Electro | `schr(mix/…)` | LIVE |
| 8 | El Djemba | Ableton-recorded DJ set | `el_djemba_mix(_hq/_epk).mp3` | LIVE |
| 9 | Alexander Zwo | Ableton-recorded DJ set | `alexander_zwo_mix(_hq/_epk).mp3` | LIVE |
| 10 | DJ Unknown | Ableton-recorded DJ set | `dj_unknown_mix(_hq/_epk).mp3` | LIVE |
| 11 | Mundz | Genre tag pending | `mundz_mix(_hq/_epk).mp3` | LIVE |
| 12 | Yogo | Season One · new artist · genre tag pending | — | LIVE |

> **EPK media status (2026-09-26):** all 12 artists ship a verified EPK stack —
> `epk/audio/<TAG>_B4_30s_loop.wav` (30.000000 s, 48 kHz, seamless),
> `epk/promo/cover_1080x1920_bw.png` (1080×1920, black background + white graphics),
> `epk/video/<TAG>_B4_EPK_30s.mp4` (h264 1080×1920 + aac 48 kHz stereo, 30.000 s, fine print burned in),
> `epk/text/FINE_PRINT_<TAG>_B4.md`.
> QC evidence: `qc/SeasonOne_EPK_qc.md` · `qc/SeasonOne_EPK_SHA256SUMS` · `qc/SeasonOne_Release_Checklist.md`.

## Master Folder Architecture

```
Radio-ish/
├── MASTER_README.md          <- this file
├── EPK_Audio_Workflow.md     <- mastering/QA convention (single source of truth)
├── BRAND_GUIDELINES.md       <- brand voice, handles, watermarks, hashtags
├── epk_lab_promotion.md      <- label pitch / promotion one-pager
│
├── Season One/               <- THE RELEASE TREE (see Season One/README.md)
│   ├── README.md             <- release standard, canonical filenames, open items
│   ├── Artists/{Artist}/
│   │   ├── EPK/Audio|Cover|Video/   <- loop_30s.wav · cover_1080x1920_bw.png · <TAG>_B4_EPK_30s.mp4
│   │   ├── Mix/                     <- mix / mix_hq / mix_epk
│   │   └── Press/                   <- FINE_PRINT_<TAG>_B4.md + index.md
│   ├── QC/                  <- QC report, SHA256SUMS, release checklist
│   └── Docs/                <- hardlinks of the four top-level docs
│
├── Social_Media/             <- platform-ready audio + video + captions
│   ├── SOCIAL_PLAYBOOK.md    <- platform specs & posting system
│   ├── Bandcamp/  Mixcloud/  SoundCloud/  Instagram/  Tracksource/
│   └── promo/                <- per-artist 9:16 clips + cover stills
├── Advertising/              <- ad copy one-pagers + campaign concepts
├── EPK_Project/              <- lab mix builds + segments
│
├── {Artist}/epk/             <- WORKING folders (source of truth, ~97 GB)
│   ├── index.md              <- human-readable EPK (send to press)
│   ├── audio/                <- original recordings (source of truth) + B4_30s_loop.wav
│   ├── processing/           <- intermediates (_raw.wav, _hq stems)
│   ├── mix/                  <- DELIVERABLES (mix/_hq/_epk)
│   ├── promo/                <- cover art + EPK mp4 source stills
│   ├── video/                <- original footage + <TAG>_B4_EPK_30s.mp4
│   └── _archive/             <- superseded/test/duplicate files (never deleted)
│
├── Archive/                  <- cross-season superseded files (never deleted)
└── qc/                       <- generated QA reports + checksums
```

> **Working vs release.** `{Artist}/epk/` is the source of truth and keeps the heavy
> material. `Season One/` is the delivery view: every file in it is a **hardlink** to the
> canonical working file, so it costs no extra disk and cannot drift.

## Deliverable Matrix (what “done” means)

Every artist **must** publish to `epk/mix/`:
- `{artist}_mix.mp3`  — 48kHz / 320kbps mastered master (identical to `_hq`)
- `{artist}_mix_hq.mp3` — 48kHz / 320kbps mastered master
- `{artist}_mix_epk.mp3` — 44.1kHz / 320kbps EPK master (CD / streamers)

Tags: artist name · Radio-ish Lab · year · genre · LC/MASTER version note.

## Find It Fast

- Press kit per artist → `{Artist}/epk/index.md`
- Mastered audio → `{Artist}/epk/mix/`
- Social video → `Social_Media/promo/{Artist}/`
- Platform uploads → `Social_Media/{Bandcamp|Mixcloud|SoundCloud|Instagram}/`
- QC evidence → `qc/{Artist}.md` + `qc/SHA256SUMS`

## QC / Delivery Rules

1. Never ship a mix without `QC: OK` in `qc/` (peak ≤ ~0 dBFS, −12…−16 LUFS, full length intact).
2. Never delete originals — move superseded files to `{Artist}/epk/_archive/`.
3. Identical duplicates on disk are allowed but must be hard-linked (zero space waste).
4. Filenames: `{YYYY-MM-DD HH-MM-SS}` timestamps; mix suffix `_mix[_hq|_epk|_clean]`.
5. Every deliverable tagged with ID3 artist/album/year/genre.

---
*Generated 2026-09-14 · updated 2026-09-19 · 9 artists · 1 standard · Mixmag-grade QA.*