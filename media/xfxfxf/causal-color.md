# XFXFXF causal-color chain

seed = 0x00000652d99bde5b

| idx | tag    | node                      | trit | L/S/H       | hex     | modality ({tactile, auditory, haptic}) |
|-----|--------|---------------------------|------|-------------|---------|----------------------------------------|
|   0 | U1     | text_input                | +1   | 32.7 / 0.49 / 300.0° | #7C2B7C | ridged, high pitch, right / up |
|   1 | U2     | codec_parameters          | +1   | 71.7 / 0.94 /  57.5° | #FAF573 | ridged, high pitch, right / up |
|   2 | Fiona  | apple_tts_fn              | +1   | 38.0 / 0.78 / 350.6° | #AC152D | ridged, high pitch, right / up |
|   3 | W1     | fiona-phonemes.wav        | -1   | 78.7 / 0.56 / 249.2° | #B4AAE7 | rough, low pitch, left / down |
|   4 | W2     | fiona-phonemes.m4a        | +0   | 64.6 / 0.62 / 103.0° | #8DDC6D | smooth, mid pitch, center |
|   5 | H      | bag-haikus.m4a            | +0   | 44.3 / 0.46 / 142.3° | #3DA564 | smooth, mid pitch, center |
|   6 | E      | elevenlabs_embedding      | +1   | 49.8 / 0.78 /  38.3° | #E29A1C | ridged, high pitch, right / up |
|   7 | Q      | query_text                | -1   | 35.3 / 0.53 / 246.8° | #352A8A | rough, low pitch, left / down |
|   8 | XFXFXF | xfxfxf_synth              | +0   | 64.3 / 0.78 /  87.6° | #AAEB5D | smooth, mid pitch, center |
|   9 | L      | listener                  | -1   | 42.2 / 0.68 / 248.1° | #3622B5 | rough, low pitch, left / down |
|  10 | Constraint | entitlement_gate          | -1   | 64.5 / 0.43 / 183.0° | #7EC7CB | rough, low pitch, left / down |

Σ trit = 0    Σ mod 3 = 0    ✓ GF(3)-conserved

## Intervention example: do(Fiona → Samantha)
Breaks all incoming edges to node 'Fiona' (U1, U2 no longer cause Fiona).
Downstream: W1, W2, E, XFXFXF all recomputed.
Under do(Fiona=Samantha), XFXFXF would be a clone of an en_US voice, not en_GB_SC.
The name would ideally change too; naming commits to the upstream choice.

## Counterfactual example: 'If training-script had omitted Scottish phonemes'
Abduction: infer U1' = training_script_minus(Scottish phonemes).
Action: do(U1 = U1').
Prediction: E' would have weaker /x/ and /ʍ/ embedding; XFXFXF'(Q) fails to pronounce
            'loch' when Q contains it, substituting /k/ — a measurable deficit.
