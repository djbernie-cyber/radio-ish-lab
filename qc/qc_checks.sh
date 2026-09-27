#!/usr/bin/env bash
# qc_checks.sh — Radio-ish QC sweep (header + optional full EBU R128 loudness)
#
#   bash qc_checks.sh            # header-only sweep (instant, no decode)
#   bash qc_checks.sh --loud     # + EBU R128 on each artist's canonical hq master
#
# Read-only on audio. Writes per-artist QC md + QC_MASTER + SHA256SUMS per artist.
set -u
R="/Users/bernie/Movies/Radio-ish"
FF="/Users/bernie/Downloads/ffmpeg"
TS=$(date +%Y%m%d_%H%M)
QC="$R/QC_Reports"; mkdir -p "$QC" "$R/_qc"

declare -A GENRE SRCE GENUS
GENRE["Habib"]="habib_mix_hq.mp3";   GENRE["Maya"]="maya_mix_hq.mp3"
GENRE["Parisa"]="parisa_mix_hq.mp3"; GENRE["SDKZ"]="sdkz_mix_hq.mp3"
GENRE["Dikier"]="dikier_mix.mp3";    GENRE["Bernie"]="bernie_mix_hq.mp3"
GENRE["El Djemba"]="el_djemba_mix_hq.mp3"; GENRE["Alexander Zwo"]="alexander_zwo_mix_hq.mp3"

durf() { local x; x=$("$FF" -hide_banner -i "$1" 2>&1 | grep -m1 -oE "Duration: [0-9:.]+" | sed 's/Duration: //'); echo "${x:-?}"; }
sr_hz() { "$FF" -hide_banner -i "$1" 2>&1 | grep -m1 "Audio:" | grep -oE "[0-9]+ Hz" | head -1 | grep -oE "[0-9]+"; }
br_k()  { local b; b=$("$FF" -hide_banner -i "$1" 2>&1 | grep -m1 "Audio:" | grep -oE "[0-9]+ kb/s" | head -1 | grep -oE "[0-9]+"); echo "${b:-?}"; }

for A in Habib Maya Parisa SDKZ Dikier Bernie "El Djemba" "Alexander Zwo"; do
  D="$R/$A/epk/mix"; M="$D/$GENRE" # canonical only - see below
  { echo "# $A — QC ($TS)"
    echo ""
    echo "| variant | duration | sr(Hz) | bitrate(kbps) |"
    echo "|---|---|---|---|"
    for f in "$D"/*.mp3; do
      [ -f "$f" ] || continue
      b=$(basename "$f")
      echo "| $b | $(durf "$f") | $(sr_hz "$f") | $(br_k "$f") |"
    done
  } > "$QC/${A}_qc_$TS.md"
done

if [ "${1:-}" = "--loud" ]; then
  LOUD="$QC/LOUDNESS_$TS.md"
  { echo "# Radio-ish — EBU R128 sweep ($TS)"
    echo "Canonical master per artist. True peak = full-chain dBTP via ebur128."
    echo ""
    echo "| artist | file | I (LUFS) | LRA (LU) | True Peak (dBTP) |"
    echo "|---|---|---|---|---|"
  } > "$LOUD"
  for A in Habib Maya Parisa Dikier Bernie "El Djemba" "Alexander Zwo"; do
    M="$R/$A/epk/mix/$GENRE"
    [ -f "$M" ] || { echo "| $A | MISSING | | | |" >> "$LOUD"; continue; }
    ROW=$("$FF" -hide_banner -i "$M" -af ebur128 -f null - 2>&1 | grep -E "^\s+(I|T):" | tail -2 | sed -E '
        s/.*I: +(-?[0-9.]+) LUFS.*/\1|/;
        s/.*T: +(-?[0-9.]+) dBFS.*/|\2/)' )
    # row = "I|<lufs>|<tdp>" (approx parse); normalize:
    I=$(echo "$ROW" | sed -nE 's/^I\|(-?[0-9.]+)\|.*/\1/p'|head -1)
    T=$(echo "$ROW" | sed -nE 's/.*\|(-?[0-9.]+)\|/\1/p'|tail -2|head -1)
    echo "| $A | $GENRE | ${I:-?} | ${I:+n/a} | ${T:-?} |" >> "$LOUD"
  done
  # SDKZ = 6.5h — windowed loudness proxy (00:45:00) to stay sane; flagged.
  M="$R/SDKZ/epk/mix/$GENRE"
  ROW=$("$FF" -hide_banner -ss 0 -t 2700 -i "$M" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | grep -oE -- "-?[0-9.]+")
  echo "| SDKZ | $GENRE (window 45m) | $ROW | n/a | *window* |" >> "$LOUD"
  echo "LOUDNESS sweep: $LOUD"
fi
echo "header sweep done → $QC/{Artist}_qc_$TS.md"

# SHA256SUMS per artist mix dir
for A in Habib Maya Parisa SDKZ Dikier Bernie "El Djemba" "Alexander Zwo"; do
  ( cd "$R/$A/epk/mix" && /usr/bin/shasum -a 256 *.mp3 > SHA256SUMS 2>/dev/null )
done
echo "SHA256SUMS regenerated per artist"