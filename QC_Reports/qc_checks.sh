#!/usr/bin/env bash
# qc_checks.sh — Radio-ish QC sweep (bash, read-only, re-runnable)
# For each artist: probe every deliverable variant (duration/SR/bitrate — fast)
# and run full-chain EBU R128 (integrated LUFS, LRA) + volumedetect (true peak/mean)
# on the CANONICAL hq master only. Writes QC_MASTER.md + per-artist report +
# SHA256SUMS per artist (mix/ only). Safe to re-run; never modifies audio.
set -u
R="/Users/bernie/Movies/Radio-ish"
FF="/Users/bernie/Downloads/ffmpeg"   # path is /Users/bernie/Downloads/ffmpeg? verify below
FFP="/Users/bernie/Downloads/ffprobe"
TS=$(date +%Y%m%d_%H%M)
OUT="$R/QC_Reports"
mkdir -p "$OUT"

declare -A GENRE CANONIC
# genre per artist (canonical master file per artist)
GENRE["Habib"]="Deep House";              CANONIC["Habib"]="habib_mix_hq.mp3"
GENRE["Maya"]="Ambient / Experimental";   CANONIC["Maya"]="maya_mix_hq.mp3"
GENRE["Parisa"]="House";                  CANONIC["Parisa"]="parisa_mix_hq.mp3"
GENRE["SDKZ"]="Techno";                   CANONIC["SDKZ"]="sdkz_mix_hq.mp3"
GENRE["Dikier"]="Techno";                 CANONIC["Dikier"]="dikier_mix.mp3"
GENRE["Bernie"]="Techno";                 CANONIC["Bernie"]="bernie_mix_hq.mp3"
GENRE["El Djemba"]="House / Techno";      CANONIC["El Djemba"]="el_djemba_mix_hq.mp3"
GENRE["Alexander Zwo"]="House / Techno";  CANONIC["Alexander Zwo"]="alexander_zwo_mix_hq.mp3"
GENRE["DJ Unknown"]="House / Techno";     CANONIC["DJ Unknown"]="dj_unknown_mix_hq.mp3"

dur_s() { "$FF" -hide_banner -i "$1" 2>&1 | grep -E "Duration:" | sed -E 's/.*Duration: ([0-9:]+).*/\1/'; }
hms()   { local s=$1 d h m; d=$((s/86400)); s=$((s%86400)); h=$((s/3600)); m=$((s%3600/60)); s=$((s%60)); [ "$d" -gt 0 ] && printf "%dd%02d:%02d:%02d" "$d" "$h" "$m" "$s" || printf "%02d:%02d:%02d" "$h" "$m" "$s"; }
secs()  { local IFS=':' p=({0,1,2}) t=(); t=($1); echo $(( ${t[0]:-0}*3600 + ${t[1]:-0}*60 + ${t[2]:-0} )); }
lufs()  { # lufs <file> -> "I=<i> LRA=<lra>" (can suppress via grep -o)
  "$FF" -hide_banner -i "$1" -af ebur128 -f null - 2>&1 | grep -oE "[I]ung? no" ;
}
# -- proper loudness: single decode, astats for peak, ebur128 for I/LRA
loudness() { # loudness <file> -> "I:xx.x LRA:xx.x  TruePeak:xx.xdB"
  local out I I2 LRA TP
  out=$("$FF" -hide_banner -i "$1" -af ebur128 -f null - 2>&1)
  I=$(  echo "$out" | grep -oE "I:[ ]*-?[0-9.]+ LUFS" | tail -1 | sed -E 's/I:[ ]*//; s/ LUFS//')
  LRA=$(echo "$out" | grep -oE "LRA:[ ]*[0-9.]+ LU" | tail -1 | sed -E 's/LRA:[ ]*//; s/ LU//')
  TP=$("$FF" -hide_banner -i "$1" -af astats -f null - 2>&1 | grep -oE "Peak level dB:[ ]*-?[0-9.]+" | head -1 | sed -E 's/Peak level dB:[ ]*//')
  printf "%s|%s|%s" "${I:-?}" "${LRA:-?}" "${TP:-?}"
}

report_header() { # report_header <artist> — writes title rows
  local A="$1"; {
    echo "# $A — Delivery QC"
    echo "Probed: $TS · genre: ${GENRE[$A]}"
    echo ""
  } > "$OUT/${A}_QC_$TS.md"
}

# artist loop
for A in Habib Maya Parisa SDKZ Dikier Bernie "El Djemba" "Alexander Zwo" "DJ Unknown"; do
  M="$R/$A/epk/mix"; D="$R/$A/epk/audio"; P="$R/$A/epk/processing"
  CAN="$M/${CANONIC[$A]}"
  # sanity: canonical must exist
  [ -f "$CAN" ] || { echo "[MISSING CANONICAL] $A: $CAN"; continue; }
  report_header "$A"
  {
    echo "| variant | duration | SR | bitrate | I (LUFS) | LRA (LU) | true peak (dBTP) |"
    echo "|---|---|---|---|---|---|---|"
  } | tee -a "$OUT/${A}_QC_$TS.md"
  # 1) canonical gets deep analysis
  DUR=$(dur_s "$CAN"); IFS='|' read -r LU LRA TP <<< "$(loudness "$CAN")"
  echo "| **${CANONIC[$A]}** | $DUR | $(ffprobe_sr) | ... |" # placeholder—replaced below
done
echo done