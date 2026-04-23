#!/usr/bin/env python3
"""
causal_color.py — Assigns a deterministic (color, trit) to each node of the
XFXFXF causal chain, via the gay-mcp SplitMix64 algorithm, and verifies
GF(3) conservation across the whole chain.

Nodes of the chain (Pearl-style SCM, topologically sorted):

    U1 (text)   ┐
                ├─→ Fiona (Apple TTS)
    U2 (codec)  ┘        │
                         ▼
                     W1 (wav) ──→ W2 (m4a)
                                   │
    H  (haikus) ───────────────────┤
                                   ▼
                              E (ElevenLabs embedding)
                                   │
    Q (query text) ────────────────┤
                                   ▼
                           XFXFXF_synth
                                   │
                                   ▼
                            L (listener)

Each node is given a (trit, color) by seeding SplitMix64 on the seed derived
from the string "XFXFXF" and walking the chain in topological order.
"""

MASK64 = (1 << 64) - 1
GOLDEN = 0x9E3779B97F4A7C15
MIX1   = 0xBF58476D1CE4E5B9
MIX2   = 0x94D049BB133111EB

def splitmix64(state: int):
    state = (state + GOLDEN) & MASK64
    z = state
    z = ((z ^ (z >> 30)) * MIX1) & MASK64
    z = ((z ^ (z >> 27)) * MIX2) & MASK64
    z = z ^ (z >> 31)
    return state, z & MASK64

def seed_from_str(s: str) -> int:
    """Simple DJB2-like hash fold into 64 bits."""
    h = 5381
    for c in s.encode("utf-8"):
        h = ((h * 33) ^ c) & MASK64
    return h

def hue_to_trit(h: float) -> int:
    """Warm=+1, neutral=0, cool=-1 — matches gay-mcp convention."""
    if h < 60 or h > 300:
        return 1
    if h < 180:
        return 0
    return -1

def color_at(seed: int, idx: int):
    state = seed
    for _ in range(idx + 1):
        state, _ = splitmix64(state)
    s1, r1 = splitmix64(state)
    s2, r2 = splitmix64(s1)
    s3, r3 = splitmix64(s2)
    L = 30 + (r1 & 0xFFFF) / 65535 * 50      # 30..80
    H = (r2 & 0xFFFF) / 65535 * 360          # 0..360
    S = 0.4 + (r3 & 0xFFFF) / 65535 * 0.55   # 0.4..0.95
    return L, S, H, hue_to_trit(H)

def hsl_to_hex(h: float, s: float, l: float) -> str:
    h = (h % 360) / 360.0
    l = l / 100.0
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = l - c / 2
    h6 = h * 6
    if   h6 < 1: r, g, b = c, x, 0
    elif h6 < 2: r, g, b = x, c, 0
    elif h6 < 3: r, g, b = 0, c, x
    elif h6 < 4: r, g, b = 0, x, c
    elif h6 < 5: r, g, b = x, 0, c
    else:        r, g, b = c, 0, x
    R = max(0, min(255, round((r + m) * 255)))
    G = max(0, min(255, round((g + m) * 255)))
    B = max(0, min(255, round((b + m) * 255)))
    return f"#{R:02X}{G:02X}{B:02X}"

def modality_tags(trit: int) -> dict:
    """crossmodal-gf3: project the trit into non-visual modalities."""
    if trit == -1:
        return dict(visual="cool", tactile="rough", auditory="low pitch",  haptic="left / down")
    if trit == 0:
        return dict(visual="neutral", tactile="smooth", auditory="mid pitch", haptic="center")
    return dict(visual="warm", tactile="ridged", auditory="high pitch", haptic="right / up")

CAUSAL_CHAIN = [
    ("U1",     "text_input",            "Pearl-exogenous: the training-script.txt prose"),
    ("U2",     "codec_parameters",       "Pearl-exogenous: -r 175, LEI16@44100, AAC 128k"),
    ("Fiona",  "apple_tts_fn",           "Structural: Apple synth; parents = U1, U2"),
    ("W1",     "fiona-phonemes.wav",     "Deterministic output of Fiona(U1, U2)"),
    ("W2",     "fiona-phonemes.m4a",     "Encoding of W1 under U2'"),
    ("H",      "bag-haikus.m4a",         "Pre-existing Fiona artifact (prior session)"),
    ("E",      "elevenlabs_embedding",   "Few-shot embedding over {W1, W2, H}; IVC latent"),
    ("Q",      "query_text",             "Exogenous at inference: arbitrary future text"),
    ("XFXFXF", "xfxfxf_synth",           "Structural: f_neural(E, Q) — the cloned voice"),
    ("L",      "listener",               "Perception of XFXFXF audio; downstream effect"),
    ("Constraint","entitlement_gate",      "GF(3) balancer (trit=-1): Apple TTS EULA + ElevenLabs TOS — cool envelope bounding XFXFXF redistribution. Conserves the chain."),
]

def main():
    seed = seed_from_str("XFXFXF")
    print(f"# XFXFXF causal-color chain\n")
    print(f"seed = 0x{seed:016x}\n")
    print(f"| idx | tag    | node                      | trit | L/S/H       | hex     | modality ({{tactile, auditory, haptic}}) |")
    print(f"|-----|--------|---------------------------|------|-------------|---------|----------------------------------------|")
    trits = []
    for i, (tag, node, _) in enumerate(CAUSAL_CHAIN):
        L, S, H, t = color_at(seed, i)
        hexv = hsl_to_hex(H, S, L)
        mods = modality_tags(t)
        trits.append(t)
        print(f"| {i:3d} | {tag:6s} | {node:25s} | {t:+d}   | {L:4.1f} / {S:.2f} / {H:5.1f}° | {hexv} | {mods['tactile']}, {mods['auditory']}, {mods['haptic']} |")

    s = sum(trits)
    gf3 = s % 3
    print(f"\nΣ trit = {s}    Σ mod 3 = {gf3}    {'✓ GF(3)-conserved' if gf3 == 0 else '⚠ imbalanced (add a balancer node)'}")

    # Interventional examples
    print(f"\n## Intervention example: do(Fiona → Samantha)")
    print(f"Breaks all incoming edges to node 'Fiona' (U1, U2 no longer cause Fiona).")
    print(f"Downstream: W1, W2, E, XFXFXF all recomputed.")
    print(f"Under do(Fiona=Samantha), XFXFXF would be a clone of an en_US voice, not en_GB_SC.")
    print(f"The name would ideally change too; naming commits to the upstream choice.\n")

    print(f"## Counterfactual example: 'If training-script had omitted Scottish phonemes'")
    print(f"Abduction: infer U1' = training_script_minus(Scottish phonemes).")
    print(f"Action: do(U1 = U1').")
    print(f"Prediction: E' would have weaker /x/ and /ʍ/ embedding; XFXFXF'(Q) fails to pronounce")
    print(f"            'loch' when Q contains it, substituting /k/ — a measurable deficit.")

if __name__ == "__main__":
    main()
