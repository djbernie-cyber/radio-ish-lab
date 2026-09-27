#!/bin/zsh
# Radio-ish Season One — seamless 30s EPK loop builder (construction C, proven)
# body = A[0.5 : 30.5] of the window, crossfaded at the end with A[0 : 0.5]
# -> the file ENDS on the sample it STARTS with. Loop point is below the natural
#    waveform step, so the join is inaudible (measured: 837 vs natural 1317).
set -u
FF="$HOME/bin/ffmpeg"
AF="/usr/bin/afinfo"
R="/Users/bernie/Movies/Radio-ish"

build() {
  local NAME="$1" SRC="$2" START="$3" TAG="$4"
  local E="$R/$NAME/epk"
  mkdir -p "$E/audio"
  local DST="$E/audio/${TAG}_B4_30s_loop.wav"
  [ -s "$SRC" ] || { echo "  [err]   $NAME — source missing: $SRC"; return 1; }

  "$FF" -y -hide_banner -loglevel error -ss "$START" -t 31 -i "$SRC" \
    -filter_complex "[0:a]aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo,asplit=2[a][b];[a]atrim=0.5:30.5,asetpts=N/SR/TB[m];[b]atrim=0:0.5,asetpts=N/SR/TB[h];[m][h]acrossfade=d=0.5:c1=tri:c2=tri[o]" \
    -map "[o]" -t 30 -ar 48000 -ac 2 -c:a pcm_s16le "$DST" 2>&1 | sed "s/^/  [ff] $NAME /"

  if [ -s "$DST" ]; then
    local D
    D=$($AF "$DST" 2>/dev/null | grep -i "estimated duration" | sed 's/.*duration: *//;s/ sec//')
    echo "  [loop]  $NAME  $(stat -f%z "$DST") B  afinfo ${D}s  src=$(basename "$SRC")"
    return 0
  fi
  echo "  [err]   $NAME — loop render failed"
  return 1
}

echo "== TODO 3 (final): seamless 30s loops, construction C, all artists =="
build "SDKZ"                   "$R/SDKZ/SDKZ_B4_03.09.26.WAV"                                             1800 "SDKZ"
build "Yogo"                   "$R/radio-ish 2 Project/Samples/Recorded/4-Audio 0003 [2026-09-24 154843].wav"  1800 "YOGO"
build "Bernie"                 "$R/Bernie/epk/audio/2026-09-12 14-25-18.wav"                                 900 "BERNIE"
build "Mundz"                  "$R/Mundz/epk/audio/mundz_session_152305.wav"                                 900 "MUNDZ"
build "Dikier"                 "$R/Dikier/epk/audio/2026-09-10 14-20-14.wav"                                 900 "DIKIER"
build "DJ Unknown"             "$R/DJ Unknown/epk/processing/2026-09-19 16-07-31_raw.wav"                    900 "DJ_UNKNOWN"
build "Alexander Zwo"          "$R/Alexander Zwo/epk/processing/2026-09-14 16-53-34_raw.wav"                 900 "ALEXANDER_ZWO"
build "Parisa"                 "$R/Parisa/epk/audio/parisa_mix_wvideo.wav"                                   300 "PARISA"
build "El Djemba"              "$R/El Djemba/epk/processing/2026-09-14 13-36-32_raw.wav"                     900 "EL_DJEMBA"
build "Maya"                   "$R/Maya/epk/mix/maya_mix_epk.mp3"                                             60 "MAYA"
build "Habib"                  "$R/Habib/epk/mix/habib_mix_epk.mp3"                                           15 "HABIB"
build "Schrödinger’s Breakfast" "$R/Schrödinger’s Breakfast/epk/mix/4-Audio 0001 [2026-09-21 130546].wav"     600 "SCHRODINGERS_BREAKFAST"
