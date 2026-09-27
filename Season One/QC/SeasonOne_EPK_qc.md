# Season One — EPK QC report

**Generated:** 2026-09-27  

**Scope:** 12 artists · 120/120 checks passed

**Toolchain:** `~/bin/ffmpeg` 4.4 / `~/bin/ffprobe` n4.4.1 (arm64, no system install)


> This report supersedes the earlier version, which described 16-bit loops and
> pre-fix EPK renders. All figures below were measured on the current files.


## Loudness standard

`MASTER_README.md` gates release audio at **-12..-16 LUFS** and **true peak <= ~0 dBFS**.
Loops are mastered to **-14 LUFS / -1.0 dBTP**. EPK videos carry small extra
attenuation because AAC and MP3 encoding add inter-sample overshoot.


## Per-artist results

| Artist | Loop | LUFS | TP | Video | LUFS | TP | Cover |
|---|---|---|---|---|---|---|---|
| SDKZ | 8,640,158 B 24-bit | -14.00 | -6.34 | 1,802,365 B | -14.02 | -5.50 | cover_1080x1920_bw.png |
| Yogo | 8,640,102 B 24-bit | -14.01 | -7.29 | 1,800,019 B | -14.04 | -5.81 | cover_1080x1920_bw.png |
| Bernie | 8,640,102 B 24-bit | -14.02 | -1.00 | 1,717,872 B | -14.74 | -1.38 | cover_1080x1920_bw.png |
| Mundz | 8,640,102 B 24-bit | -14.00 | -4.58 | 1,763,084 B | -14.03 | -3.64 | cover_1080x1920_bw.png |
| Maya | 8,640,342 B 24-bit | -14.00 | -6.00 | 1,832,283 B | -14.03 | -5.30 | cover_1080x1920_bw.png |
| Dikier | 8,640,102 B 24-bit | -14.00 | -2.69 | 1,818,788 B | -14.02 | -2.80 | cover_1080x1920_bw.png |
| DJ Unknown | 8,640,102 B 24-bit | -14.00 | -3.69 | 1,793,294 B | -14.02 | -2.91 | cover_1080x1920_bw.png |
| Alexander Zwo | 8,640,102 B 24-bit | -14.00 | -8.92 | 1,778,830 B | -14.08 | -5.18 | cover_1080x1920_bw.png |
| Habib | 8,640,324 B 24-bit | -14.31 | -0.99 | 1,672,819 B | -14.31 | -0.99 | cover_1080x1920_bw.png |
| Parisa | 8,640,102 B 24-bit | -13.99 | -3.47 | 1,771,443 B | -14.00 | -3.44 | cover_1080x1920_bw.png |
| El Djemba | 8,640,102 B 24-bit | -14.00 | -1.15 | 1,790,586 B | -14.06 | -1.25 | cover_1080x1920_bw.png |
| Schrödinger’s Breakfast | 8,640,102 B 24-bit | -14.00 | -1.90 | 1,102,733 B | -16.03 | -2.17 | SCHRODINGERS_BREAKFAST_titlecard_1080x1920.png |

## Checks

- [x] SDKZ: loop 48 kHz stereo
- [x] SDKZ: loop 30.000000 s exactly
- [x] SDKZ: loop LUFS in -12..-16
- [x] SDKZ: loop true peak <= -1.0 dBTP
- [x] SDKZ: loop 24-bit (8.64 MB)
- [x] SDKZ: cover 1080x1920 PNG
- [x] SDKZ: video 1080x1920 h264
- [x] SDKZ: video 30.000 s
- [x] SDKZ: video audio 48 kHz stereo aac
- [x] SDKZ: fine print present
- [x] YOGO: loop 48 kHz stereo
- [x] YOGO: loop 30.000000 s exactly
- [x] YOGO: loop LUFS in -12..-16
- [x] YOGO: loop true peak <= -1.0 dBTP
- [x] YOGO: loop 24-bit (8.64 MB)
- [x] YOGO: cover 1080x1920 PNG
- [x] YOGO: video 1080x1920 h264
- [x] YOGO: video 30.000 s
- [x] YOGO: video audio 48 kHz stereo aac
- [x] YOGO: fine print present
- [x] BERNIE: loop 48 kHz stereo
- [x] BERNIE: loop 30.000000 s exactly
- [x] BERNIE: loop LUFS in -12..-16
- [x] BERNIE: loop true peak <= -1.0 dBTP
- [x] BERNIE: loop 24-bit (8.64 MB)
- [x] BERNIE: cover 1080x1920 PNG
- [x] BERNIE: video 1080x1920 h264
- [x] BERNIE: video 30.000 s
- [x] BERNIE: video audio 48 kHz stereo aac
- [x] BERNIE: fine print present
- [x] MUNDZ: loop 48 kHz stereo
- [x] MUNDZ: loop 30.000000 s exactly
- [x] MUNDZ: loop LUFS in -12..-16
- [x] MUNDZ: loop true peak <= -1.0 dBTP
- [x] MUNDZ: loop 24-bit (8.64 MB)
- [x] MUNDZ: cover 1080x1920 PNG
- [x] MUNDZ: video 1080x1920 h264
- [x] MUNDZ: video 30.000 s
- [x] MUNDZ: video audio 48 kHz stereo aac
- [x] MUNDZ: fine print present
- [x] MAYA: loop 48 kHz stereo
- [x] MAYA: loop 30.000000 s exactly
- [x] MAYA: loop LUFS in -12..-16
- [x] MAYA: loop true peak <= -1.0 dBTP
- [x] MAYA: loop 24-bit (8.64 MB)
- [x] MAYA: cover 1080x1920 PNG
- [x] MAYA: video 1080x1920 h264
- [x] MAYA: video 30.000 s
- [x] MAYA: video audio 48 kHz stereo aac
- [x] MAYA: fine print present
- [x] DIKIER: loop 48 kHz stereo
- [x] DIKIER: loop 30.000000 s exactly
- [x] DIKIER: loop LUFS in -12..-16
- [x] DIKIER: loop true peak <= -1.0 dBTP
- [x] DIKIER: loop 24-bit (8.64 MB)
- [x] DIKIER: cover 1080x1920 PNG
- [x] DIKIER: video 1080x1920 h264
- [x] DIKIER: video 30.000 s
- [x] DIKIER: video audio 48 kHz stereo aac
- [x] DIKIER: fine print present
- [x] DJ_UNKNOWN: loop 48 kHz stereo
- [x] DJ_UNKNOWN: loop 30.000000 s exactly
- [x] DJ_UNKNOWN: loop LUFS in -12..-16
- [x] DJ_UNKNOWN: loop true peak <= -1.0 dBTP
- [x] DJ_UNKNOWN: loop 24-bit (8.64 MB)
- [x] DJ_UNKNOWN: cover 1080x1920 PNG
- [x] DJ_UNKNOWN: video 1080x1920 h264
- [x] DJ_UNKNOWN: video 30.000 s
- [x] DJ_UNKNOWN: video audio 48 kHz stereo aac
- [x] DJ_UNKNOWN: fine print present
- [x] ALEXANDER_ZWO: loop 48 kHz stereo
- [x] ALEXANDER_ZWO: loop 30.000000 s exactly
- [x] ALEXANDER_ZWO: loop LUFS in -12..-16
- [x] ALEXANDER_ZWO: loop true peak <= -1.0 dBTP
- [x] ALEXANDER_ZWO: loop 24-bit (8.64 MB)
- [x] ALEXANDER_ZWO: cover 1080x1920 PNG
- [x] ALEXANDER_ZWO: video 1080x1920 h264
- [x] ALEXANDER_ZWO: video 30.000 s
- [x] ALEXANDER_ZWO: video audio 48 kHz stereo aac
- [x] ALEXANDER_ZWO: fine print present
- [x] HABIB: loop 48 kHz stereo
- [x] HABIB: loop 30.000000 s exactly
- [x] HABIB: loop LUFS in -12..-16
- [x] HABIB: loop true peak <= -1.0 dBTP
- [x] HABIB: loop 24-bit (8.64 MB)
- [x] HABIB: cover 1080x1920 PNG
- [x] HABIB: video 1080x1920 h264
- [x] HABIB: video 30.000 s
- [x] HABIB: video audio 48 kHz stereo aac
- [x] HABIB: fine print present
- [x] PARISA: loop 48 kHz stereo
- [x] PARISA: loop 30.000000 s exactly
- [x] PARISA: loop LUFS in -12..-16
- [x] PARISA: loop true peak <= -1.0 dBTP
- [x] PARISA: loop 24-bit (8.64 MB)
- [x] PARISA: cover 1080x1920 PNG
- [x] PARISA: video 1080x1920 h264
- [x] PARISA: video 30.000 s
- [x] PARISA: video audio 48 kHz stereo aac
- [x] PARISA: fine print present
- [x] EL_DJEMBA: loop 48 kHz stereo
- [x] EL_DJEMBA: loop 30.000000 s exactly
- [x] EL_DJEMBA: loop LUFS in -12..-16
- [x] EL_DJEMBA: loop true peak <= -1.0 dBTP
- [x] EL_DJEMBA: loop 24-bit (8.64 MB)
- [x] EL_DJEMBA: cover 1080x1920 PNG
- [x] EL_DJEMBA: video 1080x1920 h264
- [x] EL_DJEMBA: video 30.000 s
- [x] EL_DJEMBA: video audio 48 kHz stereo aac
- [x] EL_DJEMBA: fine print present
- [x] SCHRODINGERS_BREAKFAST: loop 48 kHz stereo
- [x] SCHRODINGERS_BREAKFAST: loop 30.000000 s exactly
- [x] SCHRODINGERS_BREAKFAST: loop LUFS in -12..-16
- [x] SCHRODINGERS_BREAKFAST: loop true peak <= -1.0 dBTP
- [x] SCHRODINGERS_BREAKFAST: loop 24-bit (8.64 MB)
- [x] SCHRODINGERS_BREAKFAST: cover 1080x1920 PNG
- [x] SCHRODINGERS_BREAKFAST: video 1080x1920 h264
- [x] SCHRODINGERS_BREAKFAST: video 30.000 s
- [x] SCHRODINGERS_BREAKFAST: video audio 48 kHz stereo aac
- [x] SCHRODINGERS_BREAKFAST: fine print present

**120/120 passed**


## Known gaps

- **Yogo + Mundz genre tags** are unconfirmed, so their fine print reads `Season One`.
- **Yogo cover** is currently a copy of the SDKZ cover; no Yogo-specific artwork supplied.
- **Schrodinger's Breakfast** has no cover artwork; the EPK uses a typographic title card.
- **Mundz + Schrodinger's Breakfast** have no `index.md` press one-pager.
- **Habib / Maya / Schrodinger's Breakfast** source masters are very quiet
  (loudest 30 s window -35.5 / -27.8 / -26.0 dBFS RMS), so normalising to -14 LUFS
  raises the noise floor. Worth an ear check before press.
- **Yogo source recordings** are hardlinked into `Yogo/epk/video/` from `~/Movies/`.
