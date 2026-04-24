# XFXFXF — causal-color chain

An 11-node Pearl structural causal model (SCM) for the **XFXFXF** ElevenLabs
voice clone of Fiona (Enhanced, macOS). Each node is rendered across three
modalities — hex color, GF(3) trit, canonical chord — so the same chain
projects into sight and sound per the crossmodal-gf3 bridge.

Deterministic: SplitMix64 with seed `seed_from_str("XFXFXF") = 0x00000652d99bde5b`.

## The chain

```
 i  name         trit   hex       role
 0  U1           +1     #7C2B7C   root (unobserved confounder)
 1  U2           +1     #FAF573   root (unobserved confounder)
 2  Fiona        +1     #AC152D   macOS Enhanced voice (Mary Somerville persona)
 3  W1           −1     #B4AAE7   .wav render 1
 4  W2            0     #8DDC6D   .wav render 2
 5  H            0     #3DA564   ElevenLabs embedding hash
 6  E           +1     #E29A1C   IVC-trained voice handle
 7  Q           −1     #352A8A   prosody query [[rate]][[pbas]][[emph]]
 8  XFXFXF        0    #AAEB5D   synthesised clone output
 9  L           −1     #3622B5   listener/audience node
10  Constraint  −1     #7EC7CB   balancer — forces Σ trit ≡ 0 (mod 3)
```

Σ trit = 0 ✓

## Artefacts

- `viewer.html` — interactive SCM. Observational rendering + Pearl Level-2
  `do()` dropdowns on every non-balancer node + three preset counterfactual
  scenarios. Constraint re-solves automatically so GF(3) conservation always
  holds. Click a row → canonical chord. [raw.githack live link](https://raw.githack.com/zubyul/voice-observatory/main/media/xfxfxf/viewer.html)
- `chain.svg` — 8-column topological DAG, one column per level.
- `chain-tour.m4a` (59 s) — Fiona narrates every node and plays its canonical
  chord between announcements.
- `chain-sonification-canonical.m4a` — one chord per node, in order, no narration.
- `chain-sonification.m4a` — 3-trits-per-node variant (hue/saturation/lightness).
- `causal_color.py` — SCM definition and SplitMix64 seed.
- `chain_sonify.py` / `chain_sonify_canonical.py` — audio renderers.
- `chain_svg.py` — SVG renderer.

## Canonical chord ratios

From `color-chord-bridge`, base A4 = 440 Hz:

| trit | root ratio | fifth ratio | octave ratio | character     |
|------|-----------:|------------:|-------------:|---------------|
| −1   | 1.00       | 1.50        | 1.68         | minor third   |
| 0    | 1.00       | 1.50        | 2.00         | unison / open |
| +1   | 1.00       | 1.58        | 2.00         | major third   |

## Pearl's three levels in the viewer

1. **Observational** (default): the chain renders as given.
2. **Interventional**: any `do` dropdown forces a node's trit; Constraint
   absorbs the delta so Σ stays ≡ 0.
3. **Counterfactual** (preset buttons):
   - "U1 had been cold"
   - "Fiona had been cool"
   - "XFXFXF flipped to warm"

   Each installs a single do(), plays the counterfactual chord, and leaves
   the chain in a conserved state.

## Provenance

- Voice: Fiona (Enhanced) / macOS `say`.
- Clone target name: **XFXFXF** (ElevenLabs Instant Voice Clone).
- Seed source: `hashlib`-less SplitMix64 of the ASCII bytes of "XFXFXF".
- GF(3) conservation law: adapted from the `crossmodal-gf3` skill.
- Colour-to-chord map: `color-chord-bridge` skill.

## Regenerate locally

```bash
python3 causal_color.py          # prints table, no side effects
python3 chain_sonify_canonical.py chain-sonification-canonical.wav
python3 chain_svg.py chain.svg
```

The `.m4a` versions are AAC-encoded via `ffmpeg` from the `.wav` renders.
