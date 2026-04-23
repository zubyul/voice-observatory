# media/xfxfxf/ — cloning Fiona (Enhanced) into ElevenLabs as XFXFXF

## What this is

A training bundle for creating an **Instant Voice Clone** on ElevenLabs
whose reference voice is Apple's `say -v "Fiona (Enhanced)"` —
macOS's Scottish-English voice, which the [bmorphism/say-mcp-server
README](https://github.com/bmorphism/say-mcp-server) maps to the
**Mary Somerville** mathematician persona.

The resulting cloned voice is named **XFXFXF**.

## Contents

- `training-script.txt` — ~170 s of phonetically varied English,
  engineered to stress-test Fiona: Harvard calibration set, rainbow
  passage, Scottish-specific phonemes (`/x/` in "loch", aspirated
  `/ʍ/` in "wheesht"), slow/fast rate bands, ±4 semitone pitch
  shifts, emphasis on specific words, digit + Greek-letter sequences.
- `fiona-phonemes.wav` — 44.1 kHz 16-bit LPCM, generated via
  `say -v "Fiona (Enhanced)" -r 175 --data-format=LEI16@44100`.
- `fiona-phonemes.m4a` — 128 kbps AAC version for easier upload.
- `upload-xfxfxf.sh` — `curl`s the ElevenLabs `/v1/voices/add` endpoint
  with both this sample and the existing `../bag-haikus.m4a`,
  requesting the name `XFXFXF` and labels
  `{language: en_GB_SC, accent: scottish, gender: female,
     source: apple-tts-2x-synthesis}`.
  Requires `ELEVENLABS_API_KEY` env var.

## Conceptual frame: what does cloning *this* voice mean

**Fiona (Enhanced) is already a synthesis.** Apple's on-device TTS is
a unit-selection / neural hybrid trained on recordings of a real
Scottish-English speaker. The voice ID `com.apple.voice.enhanced.en-scotland.Fiona`
is the concatenative manifest; the phoneme inventory and prosodic
model are Apple's, the raw recordings are licensed.

**ElevenLabs IVC works through few-shot speaker-embedding extraction.**
Per the ElevenLabs docs, "the model uses your audio sample as a
conditioning signal at inference time, adjusting its output to match
the target voice without any model weight updates". It listens to the
~1.5 min sample, extracts an embedding that captures formant shape,
prosody, and accent, and then conditions generation on it.

**So XFXFXF = a synthesis of a synthesis.** The ElevenLabs neural model
learns the statistical signature of Apple's concatenative synthesis —
including its unit boundaries, its phoneme-interpolation artifacts,
its licensing-era acoustic environment. XFXFXF is not Mary Somerville
and not the original Scottish speaker; it's an embedding of Fiona-
qua-voice, now portable to any language / text / prosody ElevenLabs
supports (70+ locales through `eleven_multilingual_v2`).

**Why push `say` to its limits in the sample?** Because IVC's quality
ceiling is the reference audio (per the ElevenLabs docs). Fiona is
constrained by:
- a fixed prosodic grammar (Apple's `[[pbas]]`, `[[rate]]`,
  `[[emph]]`, `[[slnc]]` directives)
- a sampling rate determined by the `--data-format` we pass
- a speaker-specific phoneme inventory (missing sounds get
  substituted by the nearest phoneme in her inventory)

The training script exploits all three: every `[[rate]]` band, both
`[[pbas]]` extremes, all three `[[emph]]` levels, the longest and
shortest `[[slnc]]` pauses, plus Scottish-specific phonemes that
stress her inventory edges. This gives the ElevenLabs embedding the
widest possible view of Fiona's voice-manifold.

## Expected outcome

Once uploaded:
- XFXFXF can synthesize **arbitrary text in 70+ languages** while
  retaining Fiona's Scottish timbre — something `say` cannot do.
- The cloned voice is hostable as an ElevenLabs API voice-ID;
  downstream tools (the voice-observatory `say-narrate` fn, the
  bmorphism/say-mcp-server integration, etc.) could be pointed at
  XFXFXF via its ElevenLabs voice-ID as a drop-in for Fiona.
- XFXFXF's output will carry Apple's TTS artifacts in subtle ways
  (slightly stiffer unit transitions, boundary-rich formant sweeps)
  that a human listener attuned to TTS can probably detect.

## Legal / ethical note

Apple's licensed voices have TOS. The Mary Somerville persona was
added to Fiona by bmorphism's README. This clone is a *personal
experiment* on a synthesized voice; redistributing the cloned voice
or using it commercially may implicate Apple's TTS EULA. The audio
in this directory is the output of `say` running on the user's own
Mac, created specifically for this experiment. Judgment and consent
belong to the operator.

## To use

```sh
export ELEVENLABS_API_KEY=xi-...
./upload-xfxfxf.sh
```

Returns a `voice_id` printed to stdout; use that ID in subsequent
`POST /v1/text-to-speech/{voice_id}` calls.
