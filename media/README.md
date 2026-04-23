# media/

Generated artifacts.

## bag-haikus.m4a

Fiona (Enhanced) reciting the six bag-haikus from `lisp/obs_io.hy`. Generated on macOS via:

```sh
say -v "Fiona (Enhanced)" -r 175 -o bag-haikus.aiff -f bag-haikus-script.txt
afconvert -f m4af -d aac -b 48000 bag-haikus.aiff bag-haikus.m4a
```

The script (`bag-haikus-script.txt`) is the canonical text form; the audio is one materialization. To re-generate, run the commands above in `media/` — or run `PYTHONPATH=../lisp basilisp run ../lisp/observatory.lpy :haikus` to hear the same voice read it live.

Six haikus for the extended voice-tree bags (C1′, D0, E, F, G, X) that the companion PR [bmorphism/say-mcp-server#4](https://github.com/bmorphism/say-mcp-server/pull/4) introduces beyond the README's per-voice table.
