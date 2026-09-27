#!/bin/bash
# retag_sweep.sh — Radio-ish Lab standardized audio metadata sweep (re-runnable).
# For EVERY mp3 deliverable (epk/mix, epk/audio, epk/promo, every EPK_Project
# segment, every Bandcamp/SoundCloud/Mixcloud/Instagram/Tracksource mirror)
# across all 10 artists, embeds that artist's own poster as attached cover art
# plus fine-print producer/developer/publisher credits. Renders to temp then
# cp -f back (in-place, inode-stable → hardlinked mirrors stay in sync) and
# inode-dedupes so mirrored hardlinks are only re-rendered once. Idempotent.
set -u
FF=/Users/bernie/Downloads/ffmpeg
TMP=/var/folders/j6/7pnzn2kd2mlfr19zxcv1nq680000gn/T/opencode
ROW=/Users/bernie/Movies/Radio-ish
PROMO="$ROW/Social_Media/promo"
CRED='Produced by Agent Mgumbe Studio and Developed by Schrödinger'\''s Breakfast for Before Hotel Management (B4) · Radio-ish Lab'
mkdir -p "$TMP"

DONE=""

# resolve <path> -> artist's cover png. Key off the canonical PROMO folder that
# appears in the real path (authoritative), not basename heuristics.
resolve() {
  local f="$1" cv=""
  case "$f" in
    *"/Habib/"*)                    cv="$PROMO/Habib/cover_1080x1920.png" ;;
    *"/Maya/"*)                     cv="$PROMO/Maya/cover_1080x1920.png" ;;
    *"/Parisa/"*)                   cv="$PROMO/Parisa/cover_1080x1920.png" ;;
    *"/SDKZ/"*)                     cv="$PROMO/SDKZ/cover_1080x1920.png" ;;
    *"/Dikier/"*)                   cv="$PROMO/Dikier/cover_1080x1920.png" ;;
    *"/El Djemba/"*)                cv="$PROMO/El Djemba/cover_1080x1920.png" ;;
    *"/Bernie/"*)                   cv="$PROMO/Bernie/cover_1080x1920.png" ;;
    *"/Alexander Zwo/"*)            cv="$PROMO/Alexander Zwo/cover_1080x1920.png" ;;
    *"/DJ Unknown/"*)               cv="$PROMO/DJ Unknown/cover_1080x1920.png" ;;
    *"/Mundz/"*)                    cv="$PROMO/Mundz/cover_1080x1920.png" ;;
  esac
  [ -f "$cv" ] && echo "$cv"
}

retag() { # retag <mp3> in place via temp+cp (preserves inode → hardlinks sync)
  local f="$1" c id tmp
  c=$(resolve "$f"); [ -n "$c" ] || { echo "  [skip:no-artist] $(basename "$f")"; return; }
  id=$(stat -Lc '%i' "$f")
  case " $DONE " in *" $id "*) echo "  [skip:dup-inode] $(basename "$f")"; return;; esac
  DONE="$DONE $id"
  tmp="$TMP/_retag_$$.mp3"
  "$FF" -y -hide_banner -ostats -i "$f" -i "$c" \
    -map 0:a -map 1:v -c:a copy -c:v mjpeg -disposition:v attached_pic -id3v2_version 3 -write_id3v1 1 \
    -metadata producer="Agent Mgumbe Studio" \
    -metadata developer="Schrödinger's Breakfast" \
    -metadata publisher="Before Hotel Management (B4)" \
    -metadata comment="$CRED" \
    -metadata album_artist="Before Hotel Management (B4)" \
    -metadata:s:v title="Album cover" \
    -metadata:s:v comment="Cover (front)" \
    "$tmp" 2>/dev/null && cp -f "$tmp" "$f" && rm -f "$tmp" \
    && echo "  [ok] $(basename "$f")"
}

# Sweep everything under Radio-ish (masters + EPK_Project + platform mirrors).
find "$ROW" -type f \( -name "*.mp3" -o -name "*.wav" \) -not -name ".*" | while IFS= read -r f; do
  case "$f" in
    *"/_archive/"*|*"/_archive_duplicates/"*|*"/qa_copies/"*|*"/_qc_tmprender/"*|*"/_processing_old/"*|*/"processing/"*__qa__*) continue;;
  esac
  case "$f" in
    *.mp3) retag "$f" ;;
    *.wav) true ;; # WAV = lossless master, tags optional
  esac
done
echo "== sweep complete =="