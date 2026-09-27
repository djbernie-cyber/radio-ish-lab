# RADIO-ISH EPK AUDIO MASTERING WORKFLOW
# Ableton Live 12 Suite + FFmpeg CLI
# All artists: Habib, Maya, Parisa, SDKZ, Dikier, Bernie, El Djemba, Alexander Zwo, DJ Unknown

## PROJECT SETUP
1. Open Ableton Live 12 Suite
2. Create new project: 48kHz sample rate, 32-bit float
3. Save as: Radio-ish_EPK_Set.abltx
4. Set project tempo: 128 BPM (techno/house standard)

## STEM IMPORT ORDER

### SDKZ Stems (6 tracks - Track 1-6):
Track 1: 2026-09-03 11-44-48.mp3 (00:01:96, 33 kb/s - Intro)
Track 2: 2026-09-03 13-50-15.mp3
Track 3: 2026-09-03 14-12-12.mp3
Track 4: 2026-09-03 14-17-17.mp3
Track 5: 2026-09-03 14-48-45.mp3 (01:18:54, 157 kb/s - Main track - HAS LEAKAGE)
Track 6: 2026-09-03 16-10-55.mp3

### Habib Stems (8 tracks):
Track 7-14: 8 MP3 files from /Habib/epk/audio/

### Parisa Stems (7 tracks):
Track 15-21: 7 MP3 files from /Parisa/epk/audio/ (recorded July 2004)

### Maya:
Track: 2026-09-05 15-01-00.mp3 (from /Maya/epk/mix/)

### Dikier Stems (2 tracks - from Ableton Live Recordings):
Track 1: 2026-09-10 14-18-20.wav (00:02:05 - Short session clip)
Track 2: 2026-09-10 14-20-14.wav (03:03:07 - Extended recording)
Source: Live Recordings/2026-05-07 200247 Temp Project/2026-09-10 134626 Temp Project/Samples/Recorded/

### Bernie (Producer/Co-Founder - full mix session):
Track: 2026-09-07 14-50-28.wav (02:59:13 - from /Bernie/epk/processing/, extracted from OBS .mov)

## SDKZ LEAKAGE REMOVAL PROCESS (Critical)

### Step 1: Ableton EQ Eight (on Track 5 - 2026-09-03 14-48-45.mp3)
- High Pass Filter: 80 Hz, 12 dB/octave (remove sub rumble)
- Low Mid Cut: 200-300 Hz, -6 dB (reduce room noise)
- High Mid Cut: 3-5 kHz, -6 dB (reduce bleed high-end)
- Presence Boost: 4 kHz +6 dB (bring forward main mix)

### Step 2: Ableton Noise Gate (on Track 5)
- Threshold: -30 dB (adjusted to cut background bleed)
- Attack: 5 ms (preserve transients)
- Release: 150 ms
- Ratio: 1:1 soft knee
- Key Input: External side-chain from Track 1-4 (clean stems)

### Step 3: Ableton Compressor (Track 5, Glue)
- Ratio: 3:1
- Threshold: -18 dB
- Attack: 20 ms
- Release: 250 ms
- Makeup: +6 dB

### Step 4: Ableton Limiter (Master Track)
- Ceiling: -0.5 dB True Peak
- Output: 0 dB

## FFMPEG CLEANUP PIPELINE

### Bernie Processing — B4 Radio Live session (2026-08-03):

```bash
# NOTE: This session belongs to BERNIE (B4 Radio live set 2026-08-03), NOT SDKZ.
# Raw: /Users/bernie/Movies/Radio-ish/Bernie/epk/processing/2026-08-03 14-52-37_raw.wav
#      (+ copy in /Users/bernie/Movies/Radio-ish/Bernie/epk/audio/)
# Step 1: Copy raw session WAV into EPK
# Source: /Users/bernie/Desktop/Recording_2026-08-03_14h52m37s.wav  (3h 00m, 48kHz, 16-bit)

# Step 2: Full mastering chain on raw mix (HQ 48kHz export)
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/Bernie/epk/processing/2026-08-03 14-52-37_raw.wav" \
  -af "afftdn=nr=1.2:nf=-25,highpass=f=40,acompressor=threshold=-16dB:ratio=2.5:attack=15:release=200:makeup=1.5,equalizer=f=225:t=q:w=1.5:g=-3,equalizer=f=450:t=q:w=1.5:g=-2,alimiter=limit=0.9:level=false" \
  -ar 48000 -ac 2 -b:a 320k -vn \
  "/Users/bernie/Movies/Radio-ish/Bernie/epk/mix/bernie_mix_hq.mp3"

# Step 3: Replace all mix variants with mastered source
cp sdkz_mix_hq.mp3 sdkz_mix.mp3
cp sdkz_mix_hq.mp3 sdkz_mix_clean.mp3
```

> Note: `alimiter` limit accepts normalized gain (0.9 = -0.9dBFS ceiling); do NOT add post-limiter makeup gain (causes +1.5dB clipping).

### Habib Processing:

```bash
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/Habib/epk/mix/habib_mix.mp3" \
  -filter_complex "afftdn=nr=0.7:nf=0.01,eq=low_f=40:high_f=15000" \
  -ar 48000 -ac 2 -b:a 256k -vn \
  "/Users/bernie/Movies/Radio-ish/Habib/epk/mix/habib_mix_epk.mp3"
```

### Parisa Processing (2004 era recordings):

```bash
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/Parisa/epk/audio/GX020794.mp3" \
  -filter_complex "afftdn=nr=0.9:nf=0.03,eq=low_f=50:high_f=14000,volume=1.1" \
  -ar 44100 -ac 2 -b:a 192k -vn \
  "/Users/bernie/Movies/Radio-ish/Parisa/epk/audio/GX020794_clean.mp3"

# Process all 7 Parisa tracks similarly
```

### Maya Processing:

```bash
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/Maya/epk/mix/2026-09-05 15-01-00.mp3" \
  -af "afftdn=nr=0.5:nf=0.05" \
  -ar 44100 -ac 2 -b:a 192k -vn \
  "/Users/bernie/Movies/Radio-ish/Maya/epk/mix/maya_mix_epk.mp3"
```

### Dikier Processing:

```bash
# Step 1: Convert WAV stems to MP3
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/Dikier/epk/audio/2026-09-10 14-18-20.wav" \
  -ar 48000 -ac 2 -b:a 320k -vn \
  "/Users/bernie/Movies/Radio-ish/Dikier/epk/audio/2026-09-10 14-18-20.mp3"

/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/Dikier/epk/audio/2026-09-10 14-20-14.wav" \
  -ar 48000 -ac 2 -b:a 320k -vn \
  "/Users/bernie/Movies/Radio-ish/Dikier/epk/audio/2026-09-10 14-20-14.mp3"

# Step 2: Noise reduction + EQ on each stem
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/Dikier/epk/audio/2026-09-10 14-18-20.mp3" \
  -af "afftdn=nr=1.2:nf=-25,highpass=f=50,lowpass=f=15000,volume=1.05" \
  -ar 48000 -ac 2 -b:a 320k -vn \
  "/Users/bernie/Movies/Radio-ish/Dikier/epk/processing/2026-09-10 14-18-20_hq.mp3"

# Step 3: Create mix
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/Dikier/epk/processing/2026-09-10 14-18-20_hq.mp3" \
  -i "/Users/bernie/Movies/Radio-ish/Dikier/epk/processing/2026-09-10 14-20-14_hq.mp3" \
  -filter_complex "[0:a]asetpts=PTS-STARTPTS[a1];[1:a]asetpts=PTS-STARTPTS[a2];[a1][a2]concat=n=2:v=0:a=1[out];[out]alimiter=limit=0.9[outm]" \
  -map "[outm]" -ar 44100 -ac 2 -b:a 320k -vn \
  "/Users/bernie/Movies/Radio-ish/Dikier/epk/mix/dikier_mix.mp3"

# Step 4: EPK mastering chain
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/Dikier/epk/mix/dikier_mix.mp3" \
  -af "afftdn=nr=0.8:nf=-30,highpass=f=40,lowpass=f=16000,alimiter=limit=0.9:level=false,volume=0.85" \
  -ar 44100 -ac 2 -b:a 320k -vn \
  "/Users/bernie/Movies/Radio-ish/Dikier/epk/mix/dikier_mix_epk.mp3"
```

### Bernie Processing (Producer mix session):

```bash
# Step 1: Extract audio from OBS .mov to raw WAV
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/2026-09-07 14-50-28.mov" \
  -vn -ar 48000 -ac 2 \
  "/Users/bernie/Movies/Radio-ish/Bernie/epk/processing/2026-09-07 14-50-28_raw.wav"

# Step 2: Convert original to MP3
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/Bernie/epk/processing/2026-09-07 14-50-28_raw.wav" \
  -vn -ar 48000 -ac 2 -b:a 320k \
  "/Users/bernie/Movies/Radio-ish/Bernie/epk/audio/2026-09-07 14-50-28.mp3"

# Step 3: HQ mastered mix (48kHz)
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/Bernie/epk/processing/2026-09-07 14-50-28_raw.wav" \
  -af "afftdn=nr=1.2:nf=-25,highpass=f=40,acompressor=threshold=-16dB:ratio=2.5:attack=15:release=200:makeup=1.5,equalizer=f=225:t=q:w=1.5:g=-3,equalizer=f=450:t=q:w=1.5:g=-2,alimiter=limit=0.9:level=false" \
  -ar 48000 -ac 2 -b:a 320k -vn \
  "/Users/bernie/Movies/Radio-ish/Bernie/epk/mix/bernie_mix_hq.mp3"

# Step 4: EPK mastered mix (44.1kHz)
cp bernie_mix_hq.mp3 bernie_mix.mp3
/Users/bernie/Downloads/ffmpeg -i bernie_mix.mp3 \
  -af "afftdn=nr=0.8:nf=-30,alimiter=limit=0.9:level=false" \
  -ar 44100 -ac 2 -b:a 320k -vn \
  "/Users/bernie/Movies/Radio-ish/Bernie/epk/mix/bernie_mix_epk.mp3"
```

### El Djemba Processing (Ableton-recorded set):

```bash
# Step 1: Copy raw Ableton Live recording (24-bit 44.1kHz) from
#   /Users/bernie/Music/Ableton/Live Recordings/2026-05-07 200247 Temp Project/2026-09-14 121817 Temp Project/Samples/Recorded/4-Audio 0001 [2026-09-14 133632].wav
#   to epk/audio/2026-09-14 13-36-32.wav and epk/processing/2026-09-14 13-36-32_raw.wav

# Step 2: HQ mastered mix (48kHz) + EPK mastered mix (44.1kHz)
/Users/bernie/Downloads/ffmpeg -i ".../El Djemba/epk/processing/2026-09-14 13-36-32_raw.wav" \
  -af "afftdn=nr=1.2:nf=-25,highpass=f=40,acompressor=threshold=-16dB:ratio=2.5:attack=15:release=200:makeup=1.5,equalizer=f=225:t=q:w=1.5:g=-3,equalizer=f=450:t=q:w=1.5:g=-2,alimiter=limit=0.85:level=false" \
  -ar 48000 -ac 2 -b:a 320k -vn \
  ".../El Djemba/epk/mix/el_djemba_mix_hq.mp3"
# same chain at -ar 44100 -> el_djemba_mix_epk.mp3; cp hq -> el_djemba_mix.mp3
```

### Alexander Zwo Processing (Ableton-recorded set):

```bash
# Step 1: Copy raw Ableton Live recording (24-bit 44.1kHz) from
#   .../4-Audio 0003 [2026-09-14 165334].wav
#   to epk/audio/2026-09-14 16-53-34.wav and epk/processing/2026-09-14 16-53-34_raw.wav

# Step 2: HQ mastered mix (48kHz) + EPK mastered mix (44.1kHz)
# NOTE: hot source -> use alimiter=limit=0.70 to hold peak <= ~0 dBFS after MP3 encode
/Users/bernie/Downloads/ffmpeg -i ".../Alexander Zwo/epk/processing/2026-09-14 16-53-34_raw.wav" \
  -af "afftdn=nr=1.2:nf=-25,highpass=f=40,acompressor=threshold=-16dB:ratio=2.5:attack=15:release=200:makeup=1.5,equalizer=f=225:t=q:w=1.5:g=-3,equalizer=f=450:t=q:w=1.5:g=-2,alimiter=limit=0.70:level=false" \
  -ar 48000 -ac 2 -b:a 320k -vn \
  ".../Alexander Zwo/epk/mix/alexander_zwo_mix_hq.mp3"
# same chain at -ar 44100 -> alexander_zwo_mix_epk.mp3; cp hq -> alexander_zwo_mix.mp3
```

### DJ Unknown Processing (Ableton-recorded set):

```bash
# Step 1: Copy raw Ableton Live recordings (24-bit 44.1kHz) from
#   .../2026-09-19 142513 Temp Project/Samples/Recorded/
#   4-Audio 0001 [2026-09-19 152055].wav  -> epk/audio/2026-09-19 15-20-55.wav (36:46)
#   4-Audio 0002 [2026-09-19 152134].wav  -> epk/audio/2026-09-19 15-21-34.wav (06:19, overlapping early take)
#   4-Audio 0003 [2026-09-19 160731].wav  -> epk/audio/2026-09-19 16-07-31.wav (1:36:55)
#   processing 0001+0003 hardlinked as _raw.wav. Set = concat(0001, 0003) = 02:13:41.
#   0002 overlaps the 0001 window -> excluded from master, kept in audio/.

# Step 2: HQ mastered mix (48kHz) + EPK mastered mix (44.1kHz)
# source quiet (-19.4 / -17.1 LUFS) -> add volume=3.5dB before limiter, alimiter=limit=0.85
/Users/bernie/Downloads/ffmpeg -i ".../DJ Unknown/epk/processing/2026-09-19 15-20-55_raw.wav" \
  -i ".../DJ Unknown/epk/processing/2026-09-19 16-07-31_raw.wav" \
  -filter_complex "[0:a]asetpts=PTS-STARTPTS[a1];[1:a]asetpts=PTS-STARTPTS[a2];[a1][a2]concat=n=2:v=0:a=1[raw];[raw]afftdn=nr=1.2:nf=-25,highpass=f=40,volume=3.5dB,acompressor=threshold=-16dB:ratio=2.5:attack=15:release=200:makeup=1.5,equalizer=f=225:t=q:w=1.5:g=-3,equalizer=f=450:t=q:w=1.5:g=-2,alimiter=limit=0.85:level=false[out]" \
  -map "[out]" -ar 48000 -ac 2 -b:a 320k -vn \
  ".../DJ Unknown/epk/mix/dj_unknown_mix_hq.mp3"
# same chain at -ar 44100 -> dj_unknown_mix_epk.mp3; hardlink hq -> dj_unknown_mix.mp3
# Result: EBU I -15.3 LUFS · LRA 5.8 · sample peak -0.76 dBFS
```

## MIX MASTERING CHAIN (Ableton Save as Preset)

Save this chain as "EPK_Master" for all future exports:

```
Chain:
[1] EQ Eight: High Pass 40Hz, Cut 200-250Hz
[2] Compressor: Ratio 2.5:1, Threshold -16dB, Attack 15ms, Release 200ms
[3] EQ Eight: Subtractive EQ - Cut 300-600Hz (room modes)
[4] Exciter: Add subtle air (0-15 kHz, 5% mix)
[5] Limiter: Ceiling -0.5dB, True Peak ON
[6] Gain: +1.5dB make-up (to compensate limiter)
```

## EXPORT SETTINGS (All Artists)

### Format: MP3
- Bit Rate: 320 kbps (maximum quality)
- Sample Rate: 44.1 kHz (Mixmag standard)
- Channels: Stereo (Joint-Side mode)
- ID3 Tags: Artist, Title, Year, Comments

### Export Path Template:
```
/Users/bernie/Movies/{artist}/epk/mix/{artist}_mix_epk.mp3
```

## QUALITY ASSURANCE CHECKLIST

### Pre-Export Checks:
- [ ] No clipping on master bus (keep below -6 dB)
- [ ] SDKZ leakage removed via noise gate + FFT DN
- [ ] All tracks harmonically balanced (use Ableton Spectrum)
- [ ] Volume levels consistent (-14 LUFS target)
- [ ] No digital artifacts from noise reduction

### Post-Export Checks (ffmpeg):
```bash
# Verify audio specs
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/SDKZ/epk/mix/sdkz_mix_clean.mp3" \
  -show_entries stream=codec_name,bit_rate,sample_rate,channels \
  -of csv=p=0

# Check for silence artifacts
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/SDKZ/epk/mix/sdkz_mix_clean.mp3" \
  -af "astats" -f null - 2>&1 | grep -E "mean_level|max_level"

# Compare original vs cleaned (ABX test)
/Users/bernie/Downloads/ffmpeg -i "/Users/bernie/Movies/Radio-ish/SDKZ/epk/mix/sdkz_mix.mp3" \
  -i "/Users/bernie/Movies/Radio-ish/SDKZ/epk/mix/sdkz_mix_clean.mp3" \
  -filter_comlex "abx=count=10" -f wav -
```

## MIXXX CLI INTEGRATION (Optional)

For additional harmonic mixing analysis:

```bash
# Install mixxx if not present
brew install mixxx  # or use package manager

# Analyze key and BPM of all stems
mixxx --analyze "/Users/bernie/Movies/Radio-ish/SDKZ/epk/audio/*.mp3"
mixxx --analyze "/Users/bernie/Movies/Radio-ish/Habib/epk/audio/*.mp3"
mixxx --analyze "/Users/bernie/Movies/Radio-ish/Parisa/epk/audio/*.mp3"
mixxx --analyze "/Users/bernie/Movies/Radio-ish/Maya/epk/audio/*.mp3"

# Export hotcues and metadata for Ableton reference
mixxx --export-cues "/Users/bernie/Movies/Radio-ish/SDKZ/epk/" 2>/dev/null
```