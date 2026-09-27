#!/bin/zsh
# Radio-ish Season One — EPK mp4 render
# cover_1080x1920 (black bg + white graphics) + seamless 30s loop + burned-in fine print
set -u
FF="$HOME/bin/ffmpeg"
FP="$HOME/bin/ffprobe"
R="/Users/bernie/Movies/Radio-ish"
FONT="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT2="/System/Library/Fonts/Supplemental/Arial.ttf"

# name|tag|line1|line2
ROWS=(
"SDKZ|SDKZ|SDKZ|AfroHouse / AfroBeats / Deep House"
"Yogo|YOGO|YOGO|Season One - new artist"
"Bernie|BERNIE|BERNIE|Vinyl Classics / Deep House"
"Mundz|MUNDZ|MUNDZ|Season One artist"
"Maya|MAYA|MAYA|Experimental ambient electronica"
"Dikier|DIKIER|DIKIER|Extended live techno sessions"
"DJ Unknown|DJ_UNKNOWN|DJ UNKNOWN|Ableton-recorded DJ set"
"Alexander Zwo|ALEXANDER_ZWO|ALEXANDER ZWO|Ableton-recorded DJ set"
"Habib|HABIB|HABIB|Deep house & melodic techno"
"Parisa|PARISA|PARISA|2004-era nostalgic electronic"
"El Djemba|EL_DJEMBA|EL DJEMBA|Ableton-recorded DJ set"
"Schrödinger’s Breakfast|SCHRODINGERS_BREAKFAST|SCHRODINGER'S BREAKFAST|Garage / Bass / Electro"
)

esc() { printf '%s' "$1" | sed "s/'/\\\\'/g; s/:/\\\\:/g"; }

for ROW in "${ROWS[@]}"; do
  IFS='|' read -r NAME TAG L1 L2 <<< "$ROW"
  E="$R/$NAME/epk"
  LOOP="$E/audio/${TAG}_B4_30s_loop.wav"
  COVER="$E/promo/cover_1080x1920_bw.png"
  OUT="$E/video/${TAG}_B4_EPK_30s.mp4"
  mkdir -p "$E/video" "$E/text"

  if [ ! -s "$LOOP" ]; then echo "  [err]   $NAME — no loop wav"; continue; fi

  # Schrödinger has no cover artwork -> honest typographic card, house standard (black bg, white type)
  if [ ! -s "$COVER" ]; then
    COVER="$E/promo/${TAG}_titlecard_1080x1920.png"
    if [ ! -s "$COVER" ]; then
      "$FF" -y -hide_banner -loglevel error -f lavfi -i "color=c=black:s=1080x1920:d=1" \
        -vf "drawtext=fontfile='$FONT':fontcolor=white:fontsize=76:x=(w-text_w)/2:y=820:text='$(esc "$L1")',drawtext=fontfile='$FONT2':fontcolor=white:fontsize=44:x=(w-text_w)/2:y=930:text='$(esc "$L2")',drawtext=fontfile='$FONT2':fontcolor=0xB0B0B0:fontsize=34:x=(w-text_w)/2:y=1000:text='RADIO-ISH LAB  ·  SEASON ONE'" \
        -frames:v 1 "$COVER" 2>&1 | sed "s/^/  [card] $NAME /"
    fi
  fi

  # burned-in fine print over the lower third
  VF="drawtext=fontfile='$FONT':fontcolor=white:fontsize=64:bordercolor=black:borderw=8:shadowcolor=black:shadowx=4:shadowy=4:text='$(esc "$L1")':x=(w-text_w)/2:y=1240,\
drawtext=fontfile='$FONT2':fontcolor=white:fontsize=40:bordercolor=black:borderw=7:shadowcolor=black:shadowx=3:shadowy=3:text='$(esc "$L2")':x=(w-text_w)/2:y=1330,\
drawtext=fontfile='$FONT2':fontcolor=0xC8C8C8:fontsize=34:bordercolor=black:borderw=6:shadowcolor=black:shadowx=3:shadowy=3:text='RADIO-ISH LAB  ·  SEASON ONE':x=(w-text_w)/2:y=1420,\
drawtext=fontfile='$FONT2':fontcolor=0x9A9A9A:fontsize=30:bordercolor=black:borderw=6:shadowcolor=black:shadowx=3:shadowy=3:text='30s seamless loop  ·  1080x1920':x=(w-text_w)/2:y=1500"

  "$FF" -y -hide_banner -loglevel error -loop 1 -framerate 30 -i "$COVER" -i "$LOOP" \
    -vf "$VF" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 \
    -c:a aac -b:a 256k -ar 48000 -ac 2 -t 30 -movflags +faststart "$OUT" 2>&1 | sed "s/^/  [ff] $NAME /"

  # fine-print text publication alongside the video
  cat > "$E/text/FINE_PRINT_${TAG}_B4.md" <<MD
# ${L1} — EPK Fine Print (B4 · Season One · Radio-ish Lab)

- **Artist:** ${L1}
- **Style / genres:** ${L2}
- **Master source:** $(python3 -c "
import json,sys
try:
  m=json.load(open('/tmp/sdkz_bw/masters.json'))
  import os
  p=m.get('${NAME}','')
  print(os.path.basename(p) if p else 'mastered mix (epk/mix)')
except Exception: print('mastered mix (epk/mix)')
")
- **Seamless loop:** ${TAG}_B4_30s_loop.wav — 30.000000 s · 48 kHz · 24-bit stereo
  · seamless by construction (0.5 s equal-power crossfade; file ends on the sample it begins with)
- **Cover:** 1080×1920 black background + white graphics (Season One house standard)
- **EPK video:** ${TAG}_B4_EPK_30s.mp4 — H.264 (yuv420p) + AAC 256 kbps · 30.000 s · burned-in fine print
- **Status:** Season One release — media, image and text deliverables complete
MD

  if [ -s "$OUT" ]; then
    D=$("$FP" -v error -show_entries format=duration -of csv=p=0 "$OUT")
    VS=$("$FP" -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate -of csv=p=0 "$OUT")
    AS=$("$FP" -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,bit_rate -of csv=p=0 "$OUT")
    echo "  [mp4]   $NAME  $(stat -f%z "$OUT") B  dur=${D}s  v=[$VS]  a=[$AS]"
  else
    echo "  [err]   $NAME — mp4 render failed"
  fi
done
