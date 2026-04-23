#!/usr/bin/env python3
"""chain_sonify_canonical.py — canonical color-chord-bridge rendering.

Unlike chain_sonify.py (which per crossmodal-gf3 uses 3 trits from H/S/L
to pick 3 individual pitch ratios), this follows the canonical
color-chord-bridge (which lives in the skill of the same name):

  trit -1 → (1.0, 1.5, 1.68)   root + P5 + ~m6 (cool / unresolved)
  trit  0 → (1.0, 1.5, 2.0)    root + P5 + P8  (power chord / ergodic)
  trit +1 → (1.0, 1.58, 2.0)   root + M6-ish + P8 (warm / open)

One node's hue-trit → one chord shape. Single-trit keying yields cleaner
audible distinction between cool/neutral/warm. Same 11-node causal chain.
"""
import math, wave, struct, importlib.util
spec = importlib.util.spec_from_file_location("cc", "media/xfxfxf/causal_color.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)

BASE = 440.0
RATIOS = {-1: (1.0, 1.5, 1.68), 0: (1.0, 1.5, 2.0), 1: (1.0, 1.58, 2.0)}

def tone(freq, dur, sr=44100, attack=0.04, release=0.08):
    n = int(dur * sr); a = int(attack*sr); r = int(release*sr)
    out = []
    for i in range(n):
        t = i/sr; amp = 1.0
        if i < a: amp = i/a
        if i >= n-r: amp = (n-i)/r
        out.append(amp * math.sin(2*math.pi*freq*t))
    return out

def chord(trit, dur):
    rs = RATIOS[trit]
    freqs = [BASE*rs[0], BASE*rs[1], BASE*rs[2]]
    ts = [tone(f, dur) for f in freqs]
    return [sum(ts[j][i] for j in range(3))/3.0 for i in range(len(ts[0]))]

def silence(dur, sr=44100): return [0.0]*int(dur*sr)

def write_wav(path, samples, sr=44100):
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(struct.pack("<" + "h"*len(samples),
                                  *[max(-32767, min(32767, int(s*32000))) for s in samples]))

def main():
    seed = cc.seed_from_str("XFXFXF")
    out = []
    print("idx | tag        | trit | chord (Hz)")
    print("----|------------|------|------------")
    for i, (tag, node, _) in enumerate(cc.CAUSAL_CHAIN):
        L, S, H, t = cc.color_at(seed, i)
        rs = RATIOS[t]
        freqs = [BASE*rs[0], BASE*rs[1], BASE*rs[2]]
        print(f" {i:2d} | {tag:10s} | {t:+d}   | {freqs[0]:.1f} / {freqs[1]:.1f} / {freqs[2]:.1f}")
        out += chord(t, 1.8); out += silence(0.25)
    write_wav("media/xfxfxf/chain-sonification-canonical.wav", out)
    print(f"\nwrote chain-sonification-canonical.wav ({len(out)/44100:.1f}s)")

if __name__ == "__main__": main()
