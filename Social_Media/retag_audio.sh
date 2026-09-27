#!/bin/bash
# retag_audio.sh — Radio-ish Lab standardized audio metadata sweep (re-runnable).
# For every mp3 deliverable across all 10 artists' epk dirs + EPK_Project +
# every platform mirror (Bandcamp/SoundCloud/Mixcloud/Instagram/promo), embeds
# the artist's own poster (cover_1080x1920.png) as attached cover art and the
# fine-print producer/developer/publisher credits into the ID3v2 tags. Renders
# to a temp file then cp -f in place so hardlink mirror groups stay in sync;
# inode-deduped so mirrored hardlinks are re-rendered only once.
set -u
FF=/Users/bernie/Downloads/ffmpeg
TMP=/var/folders/j6/7pnzn2kd2mlfr19zxcv1nq680000gn/T/opencode
R=/Users/bernie/Movies/Radio-ish
CRED='Produced by Agent Mgumbe Studio and Developed by Schrödinger'\''s Breakfast for Before Hotel Management (B4)'
mkdir -p "$TMP"
SEED=""

ART_DIRS=( "Alexander Zwo" "Bernie" "Dikier" "DJ Unknown" "El Djemba" "Habib" "Maya" "Parisa" "SDKZ" "Mundz" )

# map any file under the lab to its artist cover, keyed on the *real* artist
# folder that appears in the path (not basename regex → no false hits)
cover_for() { # cover_for <file> -> cover png
  local f="$1" a cv
  for a in "${ART_DIRS[@]}"; do
    case "$f" in
      *"$a"*) cv="$R/Social_Media/promo/$a/cover_1080x1920.png"; [ -f "$cv" ] && { echo "$cv"; return; };;
    esac
  done
}

retag() { # retag <mp3> — embed poster + credits in place (temp + cp, inode-dedup)
  local f="$1" c id tmp
  c=$(cover_for "$f") || { echo "  [skip:no-cover] $(basename "$f")"; return; }
  id=$(stat -Lf '%i' "$f")
  case " $SEED " in *" $id "*) echo "  [skip:dup-inode] $(basename "$f")"; return;; esac
  SEED="$SEED $id"
  tmp="$TMP/_retag_$$.mp3"
  "$FF" -y -hide_banner -nostats -i "$f" -i "$c" \
    -map 0:a -map 1:v -c:a copy -c:v mjpeg -disposition:v attached_pic -id3v2_version 3 \
    -metadata producer="Agent Mgumbe Studio" \
    -metadata developer="Schrödinger's Breakfast" \
    -metadata publisher="Before Hotel Management (B4)" \
    -metadata comment="$CRED" \
    -metadata:s:v title="Album cover" -metadata:s:v comment="Cover (front)" \
    "$tmp" 2>/dev/null && cp -f "$tmp" "$f" && rm -f "$tmp" \
    && echo "  [ok] $(basename "$f")"
}

# sweep: every mp3 under each artist's epk + EPK_Project + Social_Media mirrors
find "$R" -type f -name "*.mp3" -not -name ".*" | while IFS= read -r f; do
  case "$f" in
    */.DS_Store*|*/_archive*|*/_archive_duplicates*|*/Tracksource/*|*/qa_copies/*|*/processing_archive/*) continue;;
  esac
  retag "$f"
done
echo done
