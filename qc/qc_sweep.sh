#!/usr/bin/env bash
# qc_sweep.sh — Radio-ish QC sweep (header probes all variants + windowed EBU R128
# on each artist's canonical master). Read-only. Safe to re-run. bash (not zsh).
set -u
R="/Users/bernie/Movies/Radio-ish"
FF="/Users/bernie/Downloads/ffmpeg"
TS=$(date +%Y%m%d_%H%M)
WIN=5400            # ebur128 window for very long sets (1h30)
OUT="$R/QC_Reports"; mkdir -p "$OUT"
TSFull=$(date '+%Y-%m-%d %H:%M')

lines() { echo "| $1 | ${2:-?} | ${3:-?} | ${4:-?} | ${5:-?} | ${6:-?} | ${7:-?} | ${8:-?} |"; }

# probe <file> -> "DUR;SR;KBPS" from ffmpeg header (fast, no decode)
probe() {
  local o d s k
  o=$("$FF" -hide_banner -i "$1" 2>&1)
  d=$(printf '%s\n' "$o" | sed -nE 's/.*Duration: ([0-9:]+)\..*/\1/p' | head -1)
  s=$(printf '%s\n' "$o" | sed -nE 's/.*Audio:.* ([0-9]{4,5}) Hz.*/\1/p' | head -1)
  k=$(printf '%s\n' "$o" | sed -nE 's/.*Audio:.* ([0-9]+) kb\/s.*/\1/p' | head -1)
  printf '%s;%s;%s' "${d:-?}" "${s:-?}" "${k:-?}"
}

# loud <file> [window] -> "I;LRA;PEAK?;"  (ebur128 I+LRA; volumedetect max)
loud() {
  local f="$1" w="${2:-}" o I LRA PK
  if [ -n "$w" ]; then o=$("$FF" -hide_banner -t "$w" -i "$f" -af ebur128 -f null - 2>&1)
  else              o=$("$FF" -hide_banner -i "$f" -af ebur128 -f null - 2>&1); fi
  I=$(printf '%s\n' "$o" | sed -nE 's/.*I: *(-?[0-9.]+) LUFS.*/\1/p' | tail -1)
  LRA=$(printf '%s\n' "$o" | sed -nE 's/.*LRA: *([0-9.]+) LU.*/\1/p' | tail -1)
  PK=$("$FF" -hide_banner -i "$f" -t "${w:-1800}" -af volumedetect -f null - 2>&1 | sed -nE 's/.*max_volume: (-?[0-9.]+) dB.*/\1/p' | head -1)
  printf '%s;%s;%s' "${I:-?}" "${LRA:-?}" "${PK:-?}"
}

MASTER="$OUT/QC_MASTER_$TS.md"
{
  echo "# Radio-ish — QC Sweep  ($TSFull)"
  echo ""
  echo "| artist | variant | duration | SR (kHz) | bitrate | I (LUFS) | LRA (LU) | peak (dB) |"
  echo "|---|---|---|---|---|---|---|---|"
} > "$MASTER"

for entry in \
  "Habib|habib_mix_hq.mp3|0" "Maya|maya_mix_hq.mp3|0" "Parisa|parisa_mix_hq.mp3|0" \
  "SDKZ|sdkz_mix_hq.mp3|1" "Dikier|dikier_mix.mp3|1" "Bernie|bernie_mix_hq.mp3|1" \
  "El Djemba|el_djemba_mix_hq.mp3|1" "Alexander Zwo|alexander_zwo_mix_hq.mp3|1"; do
  A="${entry%%|*}"; CAN="${entry#*|}" ; CAN="${CAN%%|*}"; LONG="${entry##*|}"
  D="$R/$A/epk/mix"
  [ -d "$D" ] || { echo "[skip] no mix dir $D"; continue; }
  RPT="$OUT/${A// /_}_QC_$TS.md"
  {
    echo "# $A — per-variant header QC  ($TSFull)"
    echo ""
    echo "| variant | duration | SR (kHz) | bitrate |"
    echo "|---|---|---|---|"
  } > "$RPT"
  W=""
  for f in "$D"/*.mp3; do
    [ -f "$f" ] || continue
    b=$(basename "$f"); IFS=';' read -r du sr kb <<< "$(probe "$f")"
    echo "| $b | $du | $(( ${sr:-0}/1000 )) | ${kb:-?} |" >> "$RPT"
  done
  # deep loudness on canonical
  CANF="$D/$CAN"
  if [ -f "$CANF" ]; then
    if [ "$LONG" = "1" ]; then R=$(loud "$CANF" "$WIN"); WMARK="window:$((WIN/60))m"
    else R=$(loud "$CANF"); WMARK="full"; fi
    IFS=';' read -r I LRA PK <<< "$R"
    lines "$A" "$CAN" "" "" "320" "$I" "$LRA" "$PK" >> "$MASTER"
    echo "" >> "$RPT"; echo "Canonical: **$CAN** · loudness window: $WMARK" >> "$RPT"
    echo "- Integrated (EBU R128): **${I:-?} LUFS**  ·  LRA: **${LRA:-?} LU**  ·  peak: **${PK:-?} dB**" >> "$RPT"
  else
    lines "$A" "$CAN" "MISSING" "" "" "?" "?" "?" >> "$MASTER"
  fi
  cat "$RPT"
done
echo ""; echo "=== QC_MASTER ==="; cat "$MASTER"; echo ""; echo "reports in: $OUT"
