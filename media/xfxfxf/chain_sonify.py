#!/usr/bin/env python3
"""chain_sonify.py — render the XFXFXF causal-color chain as audio.

Uses crossmodal-gf3's 3-tone chord convention:
  trit -1 → freq ratio 0.84  (minor third down)
  trit  0 → freq ratio 1.0   (unison)
  trit +1 → freq ratio 1.26  (major third up)

Per node, we derive THREE trits from the (H, S, L) tuple computed by
causal_color.py:
  hue trit   = hue_to_trit(H)
  sat trit   = S <= 0.55 → -1, S < 0.80 → 0, else +1
  light trit = L <= 45   → -1, L <= 65   → 0, else +1

Each node sings as a 3-voice chord (base, fifth, octave) for 1.8s, with
a short silence between nodes. Total duration ≈ 11 × 2.0 ≈ 22 s.
"""
import math
import wave
import struct
import importlib.util

# Import the causal-color chain data from the neighbouring module.
spec = importlib.util.spec_from_file_location("cc", "media/xfxfxf/causal_color.py")
cc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cc)

BASE = 440.0                   # A4
RATIO = {-1: 0.84, 0: 1.0, 1: 1.26}

def sat_trit(s):
    return -1 if s <= 0.55 else (0 if s < 0.80 else 1)

def light_trit(L):
    return -1 if L <= 45 else (0 if L <= 65 else 1)

def write_wav(path, samples, sample_rate=44100):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        frames = struct.pack("<" + "h" * len(samples),
                             *[max(-32767, min(32767, int(s * 32000))) for s in samples])
        w.writeframes(frames)

def tone(freq, dur, sr=44100, attack=0.05, release=0.10):
    n = int(dur * sr)
    out = []
    a = int(attack * sr); r = int(release * sr)
    for i in range(n):
        t = i / sr
        amp = 1.0
        if i < a: amp = i / a
        if i >= n - r: amp = (n - i) / r
        out.append(amp * math.sin(2 * math.pi * freq * t))
    return out

def chord(trit_hue, trit_sat, trit_light, dur):
    f1 = BASE * RATIO[trit_hue]
    f2 = BASE * 1.5 * RATIO[trit_sat]       # fifth
    f3 = BASE * 2.0 * RATIO[trit_light]     # octave
    a = tone(f1, dur); b = tone(f2, dur); c = tone(f3, dur)
    return [(a[i] + b[i] + c[i]) / 3.0 for i in range(len(a))]

def silence(dur, sr=44100):
    return [0.0] * int(dur * sr)

def main():
    seed = cc.seed_from_str("XFXFXF")
    out = []
    print("idx | tag        | th | ts | tl | chord (Hz)")
    print("----|------------|----|----|----|------------")
    for i, (tag, node, _) in enumerate(cc.CAUSAL_CHAIN):
        L, S, H, th = cc.color_at(seed, i)
        ts = sat_trit(S); tl = light_trit(L)
        f1 = BASE * RATIO[th]
        f2 = BASE * 1.5 * RATIO[ts]
        f3 = BASE * 2.0 * RATIO[tl]
        print(f" {i:2d} | {tag:10s} | {th:+d} | {ts:+d} | {tl:+d} | {f1:.1f} / {f2:.1f} / {f3:.1f}")
        out += chord(th, ts, tl, 1.8)
        out += silence(0.25)
    # write
    path = "media/xfxfxf/chain-sonification.wav"
    write_wav(path, out)
    dur = len(out) / 44100
    print(f"\nwrote {path}  ({dur:.1f}s, {len(out)} samples)")

if __name__ == "__main__":
    main()
