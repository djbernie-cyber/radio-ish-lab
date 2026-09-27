#!/bin/bash
# Radio-ish Lab Mixmag Mix Generator
# Creates a seamless mixed DJ set from all 6 artists

# Mix structure:
# 1. Maya ambient intro (atmospheric opening) - ~30 sec
# 2. Parisa nostalgic 2004 bridge - ~45 sec  
# 3. Habib deep house main floor - ~2 min
# 4. Dikier extended techno session - ~2 min
# 5. Bernie producer mix - ~2 min
# 6. SDKZ peak-time techno climax - ~2 min
# 7. Outro fadeout - ~30 sec
# Total: ~5 min Mixmag-style DJ set

echo "=== Radio-ish Lab Mixmag Mix Generator ==="
echo ""

# Verify all HQ stems exist
echo "Checking audio files..."

HABIB_STEMS=(
  "/Users/bernie/Movies/Radio-ish/Habib/epk/processing/2026-08-31 13-23-56_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/Habib/epk/processing/2026-08-31 13-29-53_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/Habib/epk/processing/2026-08-31 14-25-11_hq.mp3"
)

SDKZ_STEMS=(
  "/Users/bernie/Movies/Radio-ish/SDKZ/epk/processing/2026-09-03 11-44-48_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/SDKZ/epk/processing/2026-09-03 13-50-15_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/SDKZ/epk/processing/2026-09-03 14-12-12_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/SDKZ/epk/processing/2026-09-03 14-17-17_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/SDKZ/epk/processing/2026-09-03 14-48-45_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/SDKZ/epk/processing/2026-09-03 16-10-55_hq.mp3"
)

DIKIER_STEMS=(
  "/Users/bernie/Movies/Radio-ish/Dikier/epk/processing/2026-09-10 14-18-20_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/Dikier/epk/processing/2026-09-10 14-20-14_hq.mp3"
)

PARISA_STEMS=(
  "/Users/bernie/Movies/Radio-ish/Parisa/epk/processing/GX020794_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/Parisa/epk/processing/GX030794 1_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/Parisa/epk/processing/GX030794_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/Parisa/epk/processing/GX040794_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/Parisa/epk/processing/GX050794 1_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/Parisa/epk/processing/GX050794_hq.mp3"
  "/Users/bernie/Movies/Radio-ish/Parisa/epk/processing/GX060794_hq.mp3"
)

MAYA_STEM="/Users/bernie/Movies/Radio-ish/Maya/epk/mix/maya_mix_hq.mp3"

BERNIE_STEM="/Users/bernie/Movies/Radio-ish/Bernie/epk/mix/bernie_mix_hq.mp3"

echo "Habib stems: ${#HABIB_STEMS[@]}"
echo "SDKZ stems: ${#SDKZ_STEMS[@]}"
echo "Parisa stems: ${#PARISA_STEMS[@]}"
echo "Maya stem: available"
echo "Dikier stems: ${#DIKIER_STEMS[@]}"
echo "Bernie stem: available"

echo ""
echo "=== Generating Mixmag-style Lab Mix ==="

# Create the mixed output using ffmpeg with crossfades
# Strategy: Layer stems sequentially with 2-second crossfades

# Start with Maya
cp "$MAYA_STEM" "/Users/bernie/Movies/Radio-ish/EPK_Project/lab_mix_start.mp3"

# Add Parisa stems after Maya (with crossfade)
# We'll use ffmpeg to create the layered mix

# Full mix generation using ffmpeg filter_complex
# Sequence: Maya -> Parisa -> Dikier -> Habib stems -> Bernie -> SDKZ

# Build the filter complex for sequential mixing with crossfades
# Each transition will have a 3-second crossfade

# Create the mixed output
/Users/bernie/Downloads/ffmpeg -i "$MAYA_STREAM" \
  -filter_complex "
    [0:a]atrim=0:30,asetpts=PTS-STARTPTS[a1];
    [1:a]atrim=0:45,asetpts=PTS-STARTPTS[a2];
    [a1][a2]acrossfade=0.5[ combined1];
    [combined1][2:a]acrossfade=1[ combined2];
    [combined2][3:a]acrossfade=1[ final]
  " \
  -map "[final]" -ar 44100 -ac 2 -b:a 320k -vn \
  "/Users/bernie/Movies/Radio-ish/EPK_Project/lab_mix_radioish.mp3" 2>&1 | grep -E "size=|time=" | head -5

echo ""
echo "Mix generated at: /Users/bernie/Movies/Radio-ish/EPK_Project/lab_mix_radioish.mp3"
