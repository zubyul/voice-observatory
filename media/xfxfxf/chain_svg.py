#!/usr/bin/env python3
"""chain_svg.py — render the XFXFXF causal chain as an SVG diagram.
Uses the same (H, S, L, trit, hex) per node as causal_color.py.
"""
import importlib.util, textwrap
spec = importlib.util.spec_from_file_location("cc", "media/xfxfxf/causal_color.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)

# Topological layers
LAYERS = [
    ("U1", "U2"),          # layer 0: exogenous text + codec
    ("Fiona",),            # layer 1
    ("W1", "W2", "H"),     # layer 2: recordings
    ("E",),                # layer 3: embedding
    ("Q",),                # layer 4: query
    ("XFXFXF",),           # layer 5
    ("L",),                # layer 6
    ("Constraint",),       # layer 7: balancer (cross-cutting frame)
]

# Edges: parent → child
EDGES = [
    ("U1", "Fiona"), ("U2", "Fiona"),
    ("Fiona", "W1"), ("W1", "W2"),
    ("W1", "E"), ("W2", "E"), ("H", "E"),
    ("E", "XFXFXF"), ("Q", "XFXFXF"),
    ("XFXFXF", "L"),
    # Constraint is a cross-cutting frame — draw dashed edges to E and L
    ("Constraint", "E"), ("Constraint", "L"),
]

# Compute positions
SCENE_W = 900; SCENE_H = 520
pad_x = 70; pad_y = 40
W = SCENE_W - 2*pad_x
H = SCENE_H - 2*pad_y
positions = {}
seed = cc.seed_from_str("XFXFXF")
data = {}
for i, (tag, node, desc) in enumerate(cc.CAUSAL_CHAIN):
    L_, S_, H_, t = cc.color_at(seed, i)
    hex_ = cc.hsl_to_hex(H_, S_, L_)
    data[tag] = dict(idx=i, L=L_, S=S_, H=H_, trit=t, hex=hex_, node=node, desc=desc)

for li, layer in enumerate(LAYERS):
    x = pad_x + (W * li) / (len(LAYERS) - 1)
    n = len(layer)
    for ni, tag in enumerate(layer):
        y = pad_y + (H * (ni + 0.5)) / n if n > 1 else pad_y + H/2
        positions[tag] = (x, y)

def arrow(x1, y1, x2, y2, dashed=False):
    import math
    # arrow head
    dx, dy = x2 - x1, y2 - y1
    d = math.sqrt(dx*dx + dy*dy) or 1
    ux, uy = dx/d, dy/d
    # shrink to circle edges (r=24)
    r = 24
    x1s, y1s = x1 + ux*r, y1 + uy*r
    x2s, y2s = x2 - ux*r, y2 - uy*r
    # arrow-head
    head = 8
    hx, hy = -uy, ux
    h1x, h1y = x2s - ux*head + hx*head*0.5, y2s - uy*head + hy*head*0.5
    h2x, h2y = x2s - ux*head - hx*head*0.5, y2s - uy*head - hy*head*0.5
    style = ('stroke="#555" stroke-width="1.5" fill="none"'
             + (' stroke-dasharray="6,4"' if dashed else ''))
    return (f'<line x1="{x1s:.1f}" y1="{y1s:.1f}" x2="{x2s:.1f}" y2="{y2s:.1f}" {style}/>'
            f'<polygon points="{x2s:.1f},{y2s:.1f} {h1x:.1f},{h1y:.1f} {h2x:.1f},{h2y:.1f}" fill="#555" opacity="0.7"/>')

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{SCENE_W}" height="{SCENE_H}" viewBox="0 0 {SCENE_W} {SCENE_H}" font-family="-apple-system, Helvetica Neue, sans-serif">')
parts.append(f'<rect width="100%" height="100%" fill="#fbfbfa"/>')
parts.append(f'<text x="{SCENE_W/2}" y="24" text-anchor="middle" font-size="14" fill="#444" font-weight="600">XFXFXF causal-color chain · 11 nodes · Σtrit = 0 (mod 3) ✓</text>')

# edges first
for a, b in EDGES:
    x1, y1 = positions[a]; x2, y2 = positions[b]
    dashed = (a == "Constraint")
    parts.append(arrow(x1, y1, x2, y2, dashed=dashed))

# nodes
trit_sym = {-1: "−", 0: "○", 1: "+"}
trit_stroke = {-1: "stroke-dasharray=\"2,3\"", 0: "stroke-dasharray=\"6,3\"", 1: ""}
for tag, (x, y) in positions.items():
    d = data[tag]
    stroke_style = trit_stroke[d["trit"]]
    label = tag
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="22" fill="{d["hex"]}" stroke="#333" stroke-width="1.6" {stroke_style} opacity="0.9"/>')
    parts.append(f'<text x="{x:.1f}" y="{y+5:.1f}" text-anchor="middle" font-size="11" fill="#111" font-weight="600">{label}</text>')
    parts.append(f'<text x="{x:.1f}" y="{y+42:.1f}" text-anchor="middle" font-size="9.5" fill="#444">{d["hex"]} {trit_sym[d["trit"]]}</text>')
    parts.append(f'<text x="{x:.1f}" y="{y+55:.1f}" text-anchor="middle" font-size="9" fill="#777">{d["node"]}</text>')

# legend
ly = SCENE_H - 30
parts.append(f'<g font-size="10" fill="#555">')
parts.append(f'<text x="{pad_x}" y="{ly}">trit border:  solid=+1  dashed=0  dotted=−1       Constraint edges dashed (cross-cutting frame)</text>')
parts.append(f'</g>')
parts.append('</svg>')

open("media/xfxfxf/chain.svg", "w").write("\n".join(parts))
print("wrote media/xfxfxf/chain.svg")
