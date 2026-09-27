# RADIO-ISH LAB — SOCIAL MEDIA PLAYBOOK

> Short-form engine for the Lab. One asset set, rendered once, shipped everywhere.
> Everything below is production-ready: use the generator in `make_social_clips.sh`
> and the caption packs in per-artist `Social_Media/promo/{Artist}/captions.md`.

## 1. Platform Matrix

| Platform | Format | Ratio / Size | Length | FPS | File | Audio |
|----------|--------|--------------|--------|-----|------|-------|
| TikTok | MP4 H.264 | 9:16 1080×1920 | 15–60 s (100% with new features) | 30 | clip_tiktok.mp4 | AAC 44.1–48k |
| Instagram Reels | MP4 H.264 | 9:16 1080×1920 | ≤90 s | 30 | clip_reels.mp4 | AAC |
| YouTube Shorts | MP4 H.264 | 9:16 1080×1920 | ≤60 s | 30 | clip_shorts.mp4 | AAC |
| Snapchat Snap | MP4 H.264 | 9:16 1080×1920 | ≤60 s | 30 | clip_snap.mp4 | AAC |
| X (Twitter) | MP4 | 16:9 or 9:16 | ≤140 s | 30 | clip_x.mp4 | AAC |
| Facebook | MP4 | 16:9 1920×1080 | ≤120 s | 30 | clip_fb.mp4 | AAC |
| Bandcamp / SoundCloud / Mixcloud | MP3 320k / 244k | — | full mixes | — | `epk/mix/*_epk.mp3` | original |

Conversion command for any source → platform MP4 (9:16):
```bash
/Users/bernie/Downloads/ffmpeg -y -ss 00:18:00 -t 30 -i "source.mov" \
  -vf "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos,fps=30" \
  -af "alimiter=limit=0.9:level=false" -c:v h264 -crf 20 -preset faster -c:a aac -b:a 192k \
  "Social_Media/promo/{Artist}/clip_tiktok.mp4"
```

## 2. Content Pillars (80/20 split)
1. **The Set** — audio-visual performance cuts from the live sessions (80%).
2. **The Studio** — work-in-progress / gear / desk b-roll.
3. **The House** — label moments, artist collabs, event/press features.
4. **Teasers** — upcoming mix drops with sound-on hook, "this Sunday".

## 3. Posting Cadence
- **Daily engine:** 1 short-form clip/day rotating artists (TikTok + Reels + Shorts + Snap).
- **The Drop:** on mix release — clip teaser day −1, full mix on Bandcamp/SoundCloud/Mixcloud, follow-up "spotlight" clip day +2.
- **Weekly:** 1× 16:9 live-session moment on X/FB from the same clip set.
- **Monthly:** 1 artist feature across all platforms + newsletter block (see Advertising/).

## 4. Hooks (first 2 seconds = the whole game)
- Sound-on visual. Open on a moving frame, no fade-in. Text lands at ~0.5–1.0 s.
- Hook line bank:
  - "6 hours. 1 take. Zero re-takes." (SDKZ)
  - "One set. One take. The whole night." (El Djemba / Alexander Zwo)
  - "2004 called. It wants its groove back." (Parisa)
  - "Mastered to 320k. Mixed to move." (any)
  - "POV: it's 2AM and this mix doesn't stop." (generic)
- Fast cut at ~1.5 s; keep the most "air-drop" moment of the mix within 8 s.

## 5. Caption Pack Templates
Per artist folder: `Social_Media/promo/{Artist}/captions.md`. Pattern:
```
[HOOK LINE]

Full mix → link in bio
🎛 Radio-ish Lab • {artist} • {YYYY-MM-DD}
#RadioishLab #LiveFromTheLab #Techno ...
```
Platform notes:
- TikTok: caption as text overlay + 3–8 hashtags.
- Snapchat: 1–2 hashtag stickers; keep caption ≤40 chars before a cut.
- Instagram: caption + 5–10 hashtags; add location tag.
- YouTube Shorts: title ≤70 chars + 5 hashtags.

## 6. Asset Naming
All clips from `make_social_clips.sh`:
`{Artist}/{artist}_{YYYY-MM-DD}_{platform}.mp4` plus `cover_1080x1920.png`, `banner_1920x1080.png`, `captions.md`.

## 7. KPIs (Mixmag-grade)
- Reach/clip, hook-retention (0–2 s), Avg watch %, profile visits, link clicks, follows/100 views.
- Monthly review: keep clips with hook-retention ≥ 55%; cut release cadence to matches.
- Sound quality gate: teaser audio must pass QC (see EPK_Audio_Workflow.md) — never post raw.