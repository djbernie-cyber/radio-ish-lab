# Radio-ish — QC MASTER (real EBU R128, 2026-09-14)

| artist | genre | canonical hq | I (LUFS) | LRA (LU) | loudness pass |
|---|---|---|---|---|---|
| Habib | Deep House | habib_mix_hq.mp3 | **-33.1** | 13.6 | full |
| Maya | Ambient | maya_mix_hq.mp3 | **-30.1** | 7.1 | full |
| Parisa | House | parisa_mix_hq.mp3 | **-15.3** | 3.7 | full |
| SDKZ | Techno | sdkz_mix_hq.mp3 | **-25.6** | 6.1 | 90-min window |
| Dikier | Techno | dikier_mix_hq.mp3 | **-13.2** | 6.8 | 90-min window |
| Bernie | Techno | bernie_mix_hq.mp3 | **-19.3** | 8.0 | full |
| El Djemba | House/Techno | el_djemba_mix_hq.mp3 | **-15.3** | 4.1 | 90-min window |
| Alexander Zwo | House/Techno | alexander_zwo_mix_hq.mp3 | **-12.0** | 3.8 | full |

## Mundz (added 17 Sep) — real EBU R128

onboarded through the same chain as the other 8; canon is the Ableton
152305 wav (hardlinked from Live Recordings, 2,079,584,336 B, in-place
non-destructive). hq master `Mundz/epk/mix/mundz_mix_hq.mp3` is the
loudnorm-realized canon (48 kHz/320, I measured on window). Canonical
promo `EPK_Project/Mundz/mundz_30s.mp3` was EBU-verified on disk:

| asset | I (LUFS, real, window) |
|---|---|
| mundz_mix_hq.mp3 | −12.8 |
| mundz_30s.mp3 | −13.9 |

BH hash: `EPK_Project/Mundz/SHA256SUMS`. Master ent -> EPK does not
re-record; re-cut promos from the hq canon.
| Mundz | Live/Deep-Tech | mundz_mix_hq.mp3 | Mundz/mundz_30s.mp3 | −13.9 |

## DJ Unknown (added 19 Sep) — real EBU R128

Onboarded through the same chain as the other artists. Canon is
`DJ Unknown/epk/mix/dj_unknown_mix_hq.mp3` — master of the concatenated
Ableton set (0001 + 0003, raw sources hardlinked in `epk/audio/`, 24-bit
44.1k). EBU I −15.3 LUFS (full length), sample peak −0.76 dBFS. 30s promo
`EPK_Project/DJ Unknown/dj_unknown_30s.mp3` verified I −14.6. Hash evidence in
`QC_Reports/DJ Unknown_SHA256SUMS` + `EPK_Project/DJ Unknown/SHA256SUMS`.

| artist | genre | canonical hq | I (LUFS) |
|---|---|---|---|
| DJ Unknown | House/Techno | dj_unknown_mix_hq.mp3 | −15.3 |
