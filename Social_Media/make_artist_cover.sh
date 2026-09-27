#!/bin/bash
# make_artist_cover.sh — Radio-ish Lab cover + banner generator
# Usage: make_artist_cover.sh <poster_image> <artist_name> <genre> <out_dir>
# Renders:
#   cover_1080x1920.png  (9:16)  — dark field, poster panel, artist name + brand
#   banner_1920x1080.png (16:9)  — poster panel right, artist name + brand left
set -u
FF=/Users/bernie/Downloads/ffmpeg
FONT=/System/Library/Fonts/Helvetica.ttc
POSTER="$1"; NAME="$2"; GENRE="$3"; OUT="$4"
CREDIT='PRODUCED BY AGENT MGUMBE STUDIO • DEVELOPED BY SCHRÖDINGER’S BREAKFAST FOR BEFORE HOTEL MANAGEMENT (B4)'
mkdir -p "$OUT"

"$FF" -y -hide_banner -f lavfi -i "color=c=0x0E0E10:s=1080x1920:d=1" -i "$POSTER" \
  -filter_complex "[1:v]scale=1080:1440[pp];[0:v][pp]overlay=0:300,drawtext=fontfile=$FONT:text='$NAME':x=(w-text_w)/2:y=52:fontsize=92:fontcolor=white:shadowcolor=black@0.8:shadowx=4:shadowy=4,drawtext=fontfile=$FONT:text='$GENRE':x=(w-text_w)/2:y=176:fontsize=40:fontcolor=0xCCCCCC,drawtext=fontfile=$FONT:text='RADIO-ISH LAB':x=(w-text_w)/2:y=1720:fontsize=48:fontcolor=white:shadowcolor=black@0.6:shadowx=2:shadowy=2,drawtext=fontfile=$FONT:text='Live from the Lab.':x=(w-text_w)/2:y=1788:fontsize=26:fontcolor=0xBBBBBB,drawtext=fontfile=$FONT:text='$CREDIT':x=(w-text_w)/2:y=1856:fontsize=15:fontcolor=0x888888" \
  -frames:v 1 "$OUT/cover_1080x1920.png" 2>/dev/null

"$FF" -y -hide_banner -f lavfi -i "color=c=0x0E0E10:s=1920x1080:d=1" -i "$POSTER" \
  -filter_complex "[1:v]scale=810:1080[pp];[0:v][pp]overlay=1110:0,drawtext=fontfile=$FONT:text='$NAME':x=(1050-text_w)/2:y=270:fontsize=120:fontcolor=white:shadowcolor=black@0.8:shadowx=4:shadowy=4,drawtext=fontfile=$FONT:text='$GENRE':x=(1050-text_w)/2:y=420:fontsize=46:fontcolor=0xCCCCCC,drawtext=fontfile=$FONT:text='RADIO-ISH LAB':x=(1050-text_w)/2:y=700:fontsize=60:fontcolor=white:shadowcolor=black@0.6:shadowx=2:shadowy=2,drawtext=fontfile=$FONT:text='Live from the Lab.':x=(1050-text_w)/2:y=790:fontsize=34:fontcolor=0xBBBBBB,drawtext=fontfile=$FONT:text='$CREDIT':x=(1050-text_w)/2:y=950:fontsize=20:fontcolor=0x888888" \
  -frames:v 1 "$OUT/banner_1920x1080.png" 2>/dev/null

ls -la "$OUT" | grep png