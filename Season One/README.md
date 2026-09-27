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
│       ├── Mix/         <artist>_mix{,_hq,_epk}.mp3    mastered deliverables
│       └── Press/       FINE_PRINT_<TAG>_B4.md         burned-in fine print, verbatim
│                        index.md                        press one-pager (where it exists)
├── QC/                  SeasonOne_EPK_qc.md             measured stats table + 13 checks
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

- **Loudness QC** — peak ≤ ~0 dBFS, −12…−16 LUFS. Not run; no loudness tool on this machine. This is the gate MASTER_README sets.
- **Yogo + Mundz genre tags** — no roster row yet, so their fine print reads `Season One`.
- **Schrödinger's Breakfast cover artwork** — none in the project; the EPK uses a typographic title card (same black-bg/white-type standard). Drop real artwork in and re-render.
- **Yogo has no `Mix/`** — no mastered mix mp3 exists yet.
- **Mundz + Schrödinger's Breakfast have no `index.md`** press one-pager.
- **Social_Media** 9:16 clips and platform uploads (Mixcloud / SoundCloud / Bandcamp / Instagram) are untouched and still live at `../Social_Media/`.
