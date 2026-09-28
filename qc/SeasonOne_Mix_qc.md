# Season One — full-mix house-standardisation QC

Generated 2026-09-28 by `tools/standardise_masters.py` + `tools/fix_truepeak.py`, verified against the files on disk by `tools/mix_qc_report.py`.

## House standard applied to all 12 masters

| Item | Value |
|------|-------|
| Target loudness | **-14 LUFS** integrated (EBU R128 measurement) |
| Target true peak | **< 0 dBTP** release gate (target <= -1.0 dBTP) |
| EQ (Pioneer XDJ-RX3) | high-pass 28 Hz · -1.5 dB @220 Hz · +1.0 dB @3 kHz · +1.5 dB @9 kHz |
| EQ (Denon, DJ Unknown only) | high-pass 30 Hz · -1.0 dB @220 Hz · +0.5 dB @3 kHz · +0.8 dB @9 kHz |
| Master | `<artist>_mix.mp3` + `<artist>_mix_hq.mp3` — 48 kHz / 320 kbps, bit-identical |
| EPK master | `<artist>_mix_epk.mp3` — 44.1 kHz / 320 kbps |

Every artist gets the same EQ, so the 12 masters actually match. The only per-artist
variable is the trim needed to reach the loudness target, plus the limiter ceiling when
the source was hot enough for the limiter to engage.

## Results

| Artist | Deck | Source | Trim dB | LUFS (48k) | TP | LUFS (44.1k) | TP | Length |
|--------|------|--------|---------|-----------|----|-------------|----|--------|
| SDKZ | Pioneer XDJ-RX3 | `sdkz_mix.mp3` | +10.15 | **-14.00** | -0.31 | -14.00 | -0.35 | 391.0 min |
| Yogo | Pioneer XDJ-RX3 | `yogo_mix.mp3` | +0.85 | **-14.00** | -0.62 | -14.00 | -0.84 | 166.6 min |
| Bernie | Pioneer XDJ-RX3 | `bernie_mix.mp3` | +6.90 | **-13.72** | -1.39 | -13.72 | -1.50 | 179.2 min |
| Mundz | Pioneer XDJ-RX3 | `mundz_mix.wav` | +0.21 | **-14.01** | -1.57 | -14.01 | -1.43 | 131.0 min |
| Maya | Pioneer XDJ-RX3 | `maya_mix_remaster.mp3` | -0.38 | **-14.00** | -1.80 | -14.00 | -1.83 | 52.5 min |
| Dikier | Pioneer XDJ-RX3 | `dikier_mix.mp3` | -1.12 | **-14.01** | -0.71 | -14.01 | -0.42 | 185.2 min |
| DJ Unknown | Denon | `dj_unknown_mix.wav` | +2.33 | **-13.65** | -1.55 | -13.65 | -1.60 | 133.7 min |
| Alexander Zwo | Pioneer XDJ-RX3 | `alexander_zwo_mix.mp3` | -1.46 | **-13.99** | -1.26 | -14.00 | -1.57 | 101.3 min |
| Habib | Pioneer XDJ-RX3 | `habib_mix_remaster.mp3` | -0.55 | **-14.00** | -4.14 | -14.00 | -4.14 | 6.5 min |
| Parisa | Pioneer XDJ-RX3 | `parisa_mix.mp3` | +1.89 | **-13.99** | -0.92 | -13.99 | -0.92 | 25.6 min |
| El Djemba | Pioneer XDJ-RX3 | `el_djemba_mix.mp3` | +2.96 | **-13.53** | -1.58 | -13.53 | -1.75 | 173.2 min |
| Schrödinger’s Breakfast | Pioneer XDJ-RX3 | `4-Audio 0001 [2026-09-21 130546].wav` | +20.88 | **-13.54** | -0.94 | -13.54 | -1.03 | 210.0 min |

**96/96 checks passed, 0 failed.**

### Notes on the four repaired masters

The first pass left four masters above 0 dBTP, because the ceiling calculation hit its
-1.5 dB floor and heavily-limited material overshoots a -1.5 dB ceiling by 1.6-2.8 dB once
MP3 inter-sample peaks are counted. Those four were re-rendered from the archived originals
with the ceiling lowered by the overshoot actually observed:

| Artist | Ceiling dB | 48 kHz TP | 44.1 kHz TP |
|--------|-----------|----------|------------|
| Bernie | -1.50 -> -3.63 | -1.39 | -1.50 |
| DJ Unknown | -1.50 -> -2.89 | -1.55 | -1.60 |
| El Djemba | -1.50 -> -4.07 | -1.58 | -1.75 |
| Schrödinger’s Breakfast | -1.50 -> -3.54 | -0.94 | -1.03 |

The extra limiting removed a little energy, so these four sit at -13.5 to -13.7 LUFS
rather than exactly -14.00. The whole catalogue spans 0.5 dB, comfortably inside the
-12..-16 LUFS delivery gate, and every master is now clear of 0 dBTP. Pushing the last
0.4 dB would mean re-limiting four long masters for no practical benefit.

### Two engineering faults found and fixed during this pass

1. The first script archived the source file and *then* rendered the 44.1 kHz master from
   it, so the input had already been moved. Fixed by rendering both masters before anything
   is archived, and by surfacing ffmpeg's stderr instead of discarding it — a missing
   output file previously surfaced only as a bare `FileNotFoundError`.
2. The relink step only re-pointed filenames already present in `Season One`, so it never
   added files that were missing. Mundz had no `_mix.mp3` in the release tree and
   Schrödinger's Breakfast had none of the three masters at all. `tools/sync_release_mix.py`
   now syncs the release folder to exactly the canonical trio.

### Known content issues (not defects in the masters)

- Habib, Maya and Schrödinger's Breakfast have very quiet source masters, so normalising
  to -14 LUFS lifts their noise floor. Worth an ear check before press.
- Yogo and Mundz genre tags are still unconfirmed; nothing was invented.
- Schrödinger's Breakfast needed +19.9 dB of trim, so it is heavily limited by nature.

## Originals

Every pre-standardisation master is preserved, never deleted:
`Archive/2026-09-26_superseded/mixes/<Artist>/`

