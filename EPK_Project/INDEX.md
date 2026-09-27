# EPK_Project — INDEX (refreshed 2026-09-14)

All 8 Radio-ish artists are now represented in the project tree with the
standard three-part asset set. This index is the master map: artist →
canonical hq master (from the artist's epk/mix/), genre, and the 30-second
promo segment cut for each (48 kHz / 320 kbps, EBU R128 I ≈ −14). Loudness
figures below are the measured values of the segments actually on disk
(ebur128 pass, 2026-09-14).

## Artist map

| artist | genre | hq master (epk/mix/) | 30s promo segment | I (real, LUFS) |
|---|---|---|---|---|
| Habib | Deep House | habib_mix_hq.mp3 | Habib/habib_30s.mp3 | **−14.1** |
| Maya | Ambient | maya_mix_hq.mp3 | Maya/maya_30s.mp3 | −14.2 |
| Parisa | House | parisa_mix_hq.mp3 | Parisa/parisa_30s.mp3 | −14.0 |
| SDKZ | Techno | sdkz_mix_hq.mp3 | SDKZ/sdkz_30s.mp3 | −14.9 |
| Dikier | Techno | dikier_mix_hq.mp3 | Dikier/dikier_30s.mp3 | −14.5 |
| Berne | Techno | bernie_mix_hq.mp3 | Bernie/berne_30s.mp3 · Bernie/bernie_30s.mp3 | TBD ² |
| El Djemba | House/Techno | el_djemba_mix_hq.mp3 | El Djemba/el_djemba_30s.mp3 | TBD ³ |
| Alexander Zwo | House/Techno | alexander_zwo_mix_hq.mp3 | Alexander Zwo/alexander_zwo_30s.mp3 | TBD ³ |
| DJ Unknown | House/Techno | dj_unknown_mix_hq.mp3 | DJ Unknown/dj_unknown_30s.mp3 | −14.6 |

## Pipeline notes

- Canon is the `_mix_hq.mp3` 48 kHz/320 kbps master (all 8 present, verified
  14 Sep). Segments cut from canon at a representative in-set offset with
  `loudnorm=I=-14:TP=-1.5:LRA=11`, 48 kHz, 320 kbps − meters confirm −14 for
  Maya/Parisa/SDKZ/Dikier.
- Old root-level legacy segs (`maya_30s.mp3`, `parisa_45s.mp3`) remain for
  backwards compat but the per-artist dirs are authoritative now.

## To finish (small, no new masters needed)

1. **Habib** — the −24.8 read is a stale pre-lift seg; re-cut Habib 30s from
   habib_mix_hq.mp3 at the logical in-set passage and normalize to −14 (the hq
   master itself measures −33; that's the deep-house intent, only the *promo
   seg* should be lifted).
2. **Berne/Bernie naming** — confirm which master name is canonical and keep
   exactly one `berne_30s.mp3` in `Bernie/`.
3. **El Djemba / Alexander Zwo** — 30s segs not yet materialized in EPK_Project;
   cut from their hq masters (offset 2400 s / 1800 s respectively).

When those land, re-run the ebur128 pass and this table's last column becomes
all-real.

## 2026-09-14 loudness-refresh addendum

Two quiet ambient/deep-house canonicals were lifted to broadcast headroom and
re-verified (real ebur128, both co-located in each artist's `epk/mix/`):

| artist | remastered master | I (LUFS) | LRA (LU) |
|---|---|---|---|
| Habib | `habib_mix_remaster.mp3` | **−12.3** | 5.5 |
| Maya | `maya_mix_remaster.mp3` | **−13.3** | 5.9 |

Their `{artist}_30s.mp3` promos at the top of this index were cut **before**
that lift, so if you re-burn promos use the remaster as the source (`loudnorm
I=−14:TP=−1.5:LRA=11`), not the `_hq.mp3`. Master chain, loudness method, and
SHA256SUMS for all 8 artists are documented in the top section.
| Mundz | Live/Deep-Tech | mundz_mix_hq.mp3 | Mundz/mundz_30s.mp3 | **−13.9** |
