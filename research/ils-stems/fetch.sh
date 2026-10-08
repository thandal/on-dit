#!/bin/sh
# Download the CEFC-ORFEO transcripts (no audio) into DIR and unzip them.
# Usage: sh fetch.sh DIR
# The audio isn't downloaded: score_audio.py fetches just the clips it needs.
set -e
dir=${1:?usage: sh fetch.sh DIR}
mkdir -p "$dir"
curl -sS -o "$dir/cefc-no-audio.zip" \
  https://repository.ortolang.fr/api/content/cefc-orfeo/latest/cefc-no-audio.zip
unzip -q -o "$dir/cefc-no-audio.zip" -d "$dir/cefc"
echo "transcripts in $dir/cefc"
