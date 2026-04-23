# lisp/ — Basilisp ⊕ Hy double-wrap

A companion implementation of the voice-observatory invariant-reporter in
two stacked Lisps over Python:

```
┌──────────────────────────────────────────┐
│  observatory.lpy   (Basilisp / Clojure)   │  ← pure bag-math + reducer
│    - installed-set, bag-coverage          │
│    - summarize, next-install              │
│    - render-line, main let                │
└────────────┬─────────────────────────────┘
             │ (ns (:import hy obs_io))
             ▼
┌──────────────────────────────────────────┐
│  obs_io.hy   (Hy / Python-flavoured Lisp) │  ← side-effects + parsing
│    - voices-raw via subprocess            │
│    - parse-voice-line, parse-voices       │
│    - load-neighbors (json)                │
│    - asset-count (filesystem)             │
│    - say-narrate (subprocess)             │
└────────────┬─────────────────────────────┘
             │ (import subprocess os re json)
             ▼
         Python stdlib → macOS
```

## Why two Lisps

- **Basilisp** gives Clojure syntax — immutable data, persistent sets/maps,
  seq-abstraction — so the bag-math is easy to read, reason about, and
  REPL-drive from CIDER.
- **Hy** sits close to Python, so subprocess / filesystem / JSON / curses
  work without fighting the host semantics. It's the only Lisp dialect I
  wanted to write `[f (open path "r")]` in.
- The split is strict: `observatory.lpy` never performs I/O; `obs_io.hy`
  never does list-comprehensions or domain logic. All data crossing the
  boundary is plain Python (list / dict / str) so neither side cares what
  the other is written in.

## Running

```sh
./run.sh              # prints one coverage frame and exits
./run.sh :narrate     # same, plus Fiona (Enhanced) speaks the summary
```

Requires `uv`. The script bootstraps `/tmp/voice-obs-venv` with
`basilisp` + `hy` on first run; subsequent runs reuse it.

Or directly:

```sh
PYTHONPATH=. /tmp/voice-obs-venv/bin/basilisp run observatory.lpy
```

## Example output

```
installed: 208 voices; MobileAsset dir: 0 entries
bag coverage: 9 full · 8 partial · 2 empty (of 19)
next install (poetics): Amelie (Premium)

[###] B0         3/3  OK
[###] B1         3/3  OK
[##.] B3.2       2/3  missing: Amelie (Premium)
...
[...] D0         0/3  empty
```

## Extending

- To reimplement the Python TUI in this stack: move curses.wrapper-style
  drawing into `obs_io.hy` and have `observatory.lpy` reduce over an
  events channel the Hy side feeds.
- To add a Basilisp nREPL for CIDER: bind `basilisp.contrib.nrepl-server`
  at the top of `observatory.lpy` (see upstream Basilisp docs).
