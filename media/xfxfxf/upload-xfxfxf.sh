#!/bin/bash
# upload-xfxfxf.sh — create an Instant Voice Clone on ElevenLabs named XFXFXF
# using the two audio samples in this directory.
#
# Requires: ELEVENLABS_API_KEY env var.
# Docs: https://elevenlabs.io/docs/api-reference/voices/ivc/create

set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${ELEVENLABS_API_KEY:?set ELEVENLABS_API_KEY first (xi-... or sk-...)}"

# Files: two samples (phonemes training + bag-haikus recitation)
FILE1="$HERE/fiona-phonemes.m4a"
FILE2="$HERE/../bag-haikus.m4a"

[ -r "$FILE1" ] || { echo "missing: $FILE1"; exit 2; }
[ -r "$FILE2" ] || { echo "missing: $FILE2"; exit 2; }

# Combined duration (should be ~1.5–2 min; IVC optimum)
DUR=$(afinfo "$FILE1" | awk -F": " '/estimated duration/ {print $2; exit}')
DUR2=$(afinfo "$FILE2" | awk -F": " '/estimated duration/ {print $2; exit}')
echo "sample 1 ≈ $DUR ; sample 2 ≈ $DUR2"

echo "creating Instant Voice Clone 'XFXFXF'..."
curl -sSfL -X POST https://api.elevenlabs.io/v1/voices/add \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -F "name=XFXFXF" \
  -F "description=Cloned from macOS Fiona (Enhanced) / Mary Somerville persona — phonetically diverse training + six bag-haikus." \
  -F "labels={\"language\":\"en_GB_SC\",\"accent\":\"scottish\",\"gender\":\"female\",\"source\":\"apple-tts-2x-synthesis\"}" \
  -F "remove_background_noise=false" \
  -F "files=@$FILE1" \
  -F "files=@$FILE2" \
  | tee /tmp/xfxfxf-response.json

echo
echo "voice_id: $(python3 -c 'import json,sys; print(json.load(open("/tmp/xfxfxf-response.json")).get("voice_id"))')"
