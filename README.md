# voice-observatory

Passive macOS curses TUI that observes **voice-download pathways** — the
different UI surfaces that all commute at `mobileassetd`.

Three panes:

1. **State** — `say -v "?"` total / Premium / Enhanced / Standard counts, deltas from init
2. **Invariant** — entry count in
   `/private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_VoiceServicesVocalizerVoice/`
3. **Events** — live `log stream` filtered on `com.apple.MobileAsset` + `VocalizerVoice`

The header turns green the moment a new asset / voice appears.

## Why

macOS exposes at least five paths to download TTS voices (Settings GUI,
URL deep-link, AppleScript, VoiceOver Utility, MDM profile). All five
route to the same `mobileassetd` fetch. This TUI is the route-blind
observer: it reads only the post-condition, never which key was pressed.

Keys `1`–`5` in the TUI launch the pathways; the header flip is
empirically identical regardless of choice — demonstrating path-invariance
in the voice-install diagram.

## Usage

```sh
python3 voice_observatory.py
```

Requirements: macOS, Python 3 (stdlib only — no pip install).

## Companion

This is the runtime counterpart to [bmorphism/say-mcp-server#4](https://github.com/bmorphism/say-mcp-server/pull/4),
which specifies a bounded-treewidth forest over the voices that `say-mcp-server`
recommends. That PR lets you pick voice subsets by neighborhood; this TUI
watches them get installed.

## Keys

| key | pathway                                   |
|-----|-------------------------------------------|
| `1` | Settings GUI (`open -a "System Settings"`) |
| `2` | URL deep-link (`x-apple.systempreferences:...Spoken Content`) |
| `3` | AppleScript-driven `open location`         |
| `4` | VoiceOver Utility side-door               |
| `5` | Configuration profile pane (MDM path)     |
| `q` / `Esc` | quit                              |

## License

MIT.
