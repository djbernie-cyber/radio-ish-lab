# SEASON ONE — Radio-ish Lab release tree

The delivery-facing view of Season One. **Every file here is a hardlink** to the canonical
file in the artist's working folder (`../<Artist>/epk/…`), per the project's own rule 3
("identical duplicates on disk are allowed but must be hard-linked"). Same inode, so this
tree costs **zero extra disk** and cannot drift out of sync with the source.

Working files — multitrack masters, stems, raw session audio and footage (~97 GB) — stay in
`<Artist>/epk/{audio,processing,video}/` and are deliberately **not** duplicated here.

## Layout

```
Season One/
├── Artists/
│   └── <Artist>/
│       ├── EPK/
│       │   ├── Audio/    <TAG>_B4_30s_loop.wav        seamless 30.000000 s · 48 kHz · 24-bit stereo
│       │   ├── Cover/    cover_1080x1920_bw.png        1080×1920 · black background + white graphics
│       │   └── Video/    <TAG>_B4_EPK_30s.mp4          h264 1080×1920 yuv420p + aac 48 kHz · 30.000 s
│       ├── Mix/         <artist>_mix{,_hq,_epk}.mp3    mastered deliverables, house-standardised
│       └── Press/       FINE_PRINT_<TAG>_B4.md         burned-in fine print, verbatim
│                        index.md                        press one-pager
├── QC/                  SeasonOne_EPK_qc.md             measured stats table + 13 checks
│                        SeasonOne_Mix_qc.md             full-mix house standard + per-artist results
│                        SeasonOne_EPK_SHA256SUMS        SHA-256 of every deliverable + both binaries
│                        SeasonOne_Release_Checklist.md  verified vs open items
└── Docs/                MASTER_README.md · BRAND_GUIDELINES.md
                         EPK_Audio_Workflow.md · epk_lab_promotion.md
```

## The release standard (identical for all 12 artists)

| Deliverable | Spec |
|-------------|------|
| Seamless loop | exactly **30.000000 s**, 48 kHz, 24-bit stereo. Seamless *by construction*: the window's `A[0.5:30.5]` is crossfaded with `A[0:0.5]`, so the file ends on the sample it begins with. Measured seam sits at or below each track's own natural sample step. |
| Cover | 1080×1920, **black background + white graphics** |
| EPK video | h264 1080×1920 `yuv420p` + aac 48 kHz stereo, 30.000 s, `+faststart`, fine print burned into the lower third |
| Fine print | artist · style/genres · `RADIO-ISH LAB · SEASON ONE` · `30s seamless loop · 1080x1920` |

Genre tags come from `Docs/MASTER_README.md` — nothing is invented. Bernie is deliberately
**Vinyl Classics / Deep House** (tightened so it does not collide with SDKZ's Deep House).

## Mix house standard

All 12 full-length masters were standardised on 2026-09-28 so the catalogue is genuinely
consistent, not just nominally: one gain, one EQ, applied identically to every artist.

| Deliverable | Spec |
|-------------|------|
| Loudness | **-14 LUFS** integrated (EBU R128) |
| True peak | **below 0 dBTP** (release gate); 10 of 12 also meet `<= -1.0 dBTP` |
| EQ — Pioneer XDJ-RX3 | high-pass 28 Hz · -1.5 dB @220 Hz · +1.0 dB @3 kHz · +1.5 dB @9 kHz |
| EQ — Denon (DJ Unknown only) | high-pass 30 Hz · -1.0 dB @220 Hz · +0.5 dB @3 kHz · +0.8 dB @9 kHz |
| Master | `<artist>_mix.mp3` + `<artist>_mix_hq.mp3` — 48 kHz / 320 kbps, bit-identical |
| EPK master | `<artist>_mix_epk.mp3` — 44.1 kHz / 320 kbps |

Only the trim differs per artist, and only because each source arrived at a different level.
Per-artist trim, measured loudness, true peak and limiter ceiling: `QC/SeasonOne_Mix_qc.md`
(**96/96 checks passed**). Pre-standardisation masters are preserved, never deleted, under
`../Archive/2026-09-26_superseded/mixes/`.

`mix` and `mix_hq` are bit-identical by the house matrix; they are encoded once and installed
under both names rather than being two separate encodes that could drift.

## Canonical filenames

One loop and one EPK mp4 per artist; older builds were moved (never deleted) to
`../Archive/2026-09-26_superseded/`.

| Artist | Tag | Loop | EPK video |
|--------|-----|------|-----------|
| SDKZ | `SDKZ` | `SDKZ_B4_30s_loop.wav` | `SDKZ_B4_EPK_30s.mp4` |
| Yogo | `YOGO` | `YOGO_B4_30s_loop.wav` | `YOGO_B4_EPK_30s.mp4` |
| Bernie | `BERNIE` | `BERNIE_B4_30s_loop.wav` | `BERNIE_B4_EPK_30s.mp4` |
| Mundz | `MUNDZ` | `MUNDZ_B4_30s_loop.wav` | `MUNDZ_B4_EPK_30s.mp4` |
| Maya | `MAYA` | `MAYA_B4_30s_loop.wav` | `MAYA_B4_EPK_30s.mp4` |
| Dikier | `DIKIER` | `DIKIER_B4_30s_loop.wav` | `DIKIER_B4_EPK_30s.mp4` |
| DJ Unknown | `DJ_UNKNOWN` | `DJ_UNKNOWN_B4_30s_loop.wav` | `DJ_UNKNOWN_B4_EPK_30s.mp4` |
| Alexander Zwo | `ALEXANDER_ZWO` | `ALEXANDER_ZWO_B4_30s_loop.wav` | `ALEXANDER_ZWO_B4_EPK_30s.mp4` |
| Habib | `HABIB` | `HABIB_B4_30s_loop.wav` | `HABIB_B4_EPK_30s.mp4` |
| Parisa | `PARISA` | `PARISA_B4_30s_loop.wav` | `PARISA_B4_EPK_30s.mp4` |
| El Djemba | `EL_DJEMBA` | `EL_DJEMBA_B4_30s_loop.wav` | `EL_DJEMBA_B4_EPK_30s.mp4` |
| Schrödinger's Breakfast | `SCHRODINGERS_BREAKFAST` | `SCHRODINGERS_BREAKFAST_B4_30s_loop.wav` | `SCHRODINGERS_BREAKFAST_B4_EPK_30s.mp4` |

## Open items before press release

- **Loudness QC — DONE.** All 12 loops are mastered to **-14 LUFS / -1.0 dBTP** and every
  EPK video is within the `-12..-16 LUFS` gate with true peak below 0 dBTP.
  See `QC/SeasonOne_EPK_qc.md` (120/120 checks) and `QC/SeasonOne_EPK_SHA256SUMS`.
  Three defects were found and fixed by this pass: three loops were clipping past
  0 dBTP, six sat outside the LUFS gate, and **Habib's loop had been cut from a
  silent 30 s window in the head of its mix** — it was effectively silent at
  -72 dBFS. All loops are now 24-bit, matching the spec published in the fine print.
- **Yogo + Mundz genre tags** — no confirmed roster row yet, so their fine print reads `Season One`.
- **Yogo cover** is currently a copy of the SDKZ cover; no Yogo-specific artwork supplied.
- **Schrödinger's Breakfast cover artwork** — none in the project; the EPK uses a typographic title card. Drop real artwork in and re-render.
- **Mix house standardisation — DONE.** All 12 full-length masters standardised to one gain and
  one EQ at -14 LUFS with every true peak below 0 dBTP. Four masters came out of the first pass
  above 0 dBTP (El Djemba +1.27, Bernie +0.83, Schrödinger +0.74, DJ Unknown +0.09) because the
  ceiling calculation hit its floor and heavily-limited material overshoots once MP3
  inter-sample peaks are counted; all four were re-rendered from the archived originals with the
  ceiling lowered by the overshoot measured. See `QC/SeasonOne_Mix_qc.md` (96/96).
- **Press one-pagers — DONE.** The three artists that had no `index.md` (Mundz, Yogo,
  Schrödinger's Breakfast) now have one, hardlinked from the working folder like the other nine.
- **Release tree integrity — DONE.** All 96 files in this tree verified as hardlinks to their
  working originals. Two gaps were found and closed: Mundz had no `_mix.mp3` here, and
  Schrödinger's Breakfast had none of the three masters, because the relink step only refreshed
  filenames that already existed. `tools/sync_release_mix.py` now syncs rather than refreshes.
- **Habib / Maya / Schrödinger's Breakfast** source masters are extremely quiet
  (loudest 30 s window -35.5 / -27.8 / -26.0 dBFS RMS), so normalising to -14 LUFS
  raises the noise floor. Worth an ear check before press.
- **Social_Media** — Yogo's 9:16 clips and a 16:9 promo cut are done in
  `Social_Media/promo/Yogo/`; the other 11 artists' clips and all platform
  uploads (Mixcloud / SoundCloud / Bandcamp / Instagram) are still outstanding.
