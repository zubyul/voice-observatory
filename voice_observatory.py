#!/usr/bin/env python3
"""voice-observatory — passive TUI watching macOS voice-download invariant.

Mirrors dmaynor/airdrop-observatory style: stdlib-only curses, three
panes (state, invariant, log). Press 1-5 to launch a pathway; observer
reports which one reached the invariant first.
"""
import curses
import subprocess
import time
import os
import sys
from collections import deque
from datetime import datetime

ASSET_DIR = ("/private/var/MobileAsset/AssetsV2/"
             "com_apple_MobileAsset_VoiceServicesVocalizerVoice")
POLL_SEC = 2.0

PATHWAYS = {
    ord('1'): ("P1 Settings (GUI)",
               ["open", "-a", "System Settings"]),
    ord('2'): ("P2 URL deep-link",
               ["open",
                "x-apple.systempreferences:com.apple.Accessibility-Settings.extension?Spoken Content"]),
    ord('3'): ("P3 AppleScript",
               ["osascript", "-e",
                'open location "x-apple.systempreferences:com.apple.Accessibility-Settings.extension?Spoken Content"']),
    ord('4'): ("P4 VoiceOver Utility",
               ["open", "-a", "/System/Library/CoreServices/VoiceOver Utility.app"]),
    ord('5'): ("P5 open MDM profile picker",
               ["open", "x-apple.systempreferences:com.apple.preferences.configurationprofiles"]),
}

def voices_counts():
    try:
        out = subprocess.check_output(["say", "-v", "?"], text=True, timeout=2)
        lines = [l for l in out.splitlines() if l.strip()]
        total = len(lines)
        prem = sum(1 for l in lines if "Premium" in l)
        enh = sum(1 for l in lines if "Enhanced" in l)
        return total, prem, enh
    except Exception:
        return 0, 0, 0

def asset_count():
    try:
        return len(os.listdir(ASSET_DIR))
    except FileNotFoundError:
        return 0

def spawn_log_stream():
    try:
        return subprocess.Popen(
            ["/usr/bin/log", "stream", "--style=compact",
             "--predicate",
             '(subsystem == "com.apple.MobileAsset") OR '
             '(eventMessage CONTAINS[c] "VocalizerVoice") OR '
             '(eventMessage CONTAINS[c] "voice download")'],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1)
    except FileNotFoundError:
        return None

def main(stdscr):
    curses.curs_set(0)
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_CYAN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    stdscr.nodelay(True)
    stdscr.timeout(int(POLL_SEC * 1000))

    events = deque(maxlen=500)
    log_proc = spawn_log_stream()
    init_total, init_prem, init_enh = voices_counts()
    init_assets = asset_count()
    launched = None

    while True:
        if log_proc and log_proc.stdout:
            while True:
                try:
                    line = log_proc.stdout.readline()
                except Exception:
                    break
                if not line: break
                events.append(line.rstrip())

        total, prem, enh = voices_counts()
        assets = asset_count()
        d_total = total - init_total
        d_assets = assets - init_assets
        d_prem = prem - init_prem
        d_enh = enh - init_enh

        h, w = stdscr.getmaxyx()
        stdscr.erase()
        now = datetime.now().strftime("%H:%M:%S")

        header = f" voice-observatory · {now} · Δtotal={d_total:+d} Δassets={d_assets:+d} Δprem={d_prem:+d} Δenh={d_enh:+d} "
        col = curses.color_pair(1 if (d_total > 0 or d_assets > 0) else 3) | curses.A_REVERSE
        stdscr.addstr(0, 0, header[:w-1], col)

        stdscr.addstr(2, 2, f"say -v ? total   : {total}   (init {init_total})")
        stdscr.addstr(3, 2, f"  Premium        : {prem}   (init {init_prem})", curses.color_pair(1))
        stdscr.addstr(4, 2, f"  Enhanced       : {enh}   (init {init_enh})", curses.color_pair(2))
        stdscr.addstr(5, 2, f"MobileAsset dir  : {assets} entries   (init {init_assets})")
        stdscr.addstr(6, 2, f"asset dir path   : {ASSET_DIR}")
        if launched:
            stdscr.addstr(8, 2, f"LAUNCHED: {launched}", curses.color_pair(3) | curses.A_BOLD)

        stdscr.addstr(10, 0, " MobileAsset / VocalizerVoice events ".center(w-1, "─"))
        start_row = 11
        for i, ev in enumerate(list(events)[-(h-start_row-2):]):
            if start_row + i >= h - 1: break
            stdscr.addstr(start_row + i, 0, ev[:w-1])

        footer = " q=quit · 1=P1(GUI) · 2=P2(URL) · 3=P3(AppleScript) · 4=P4(VoiceOver) · 5=P5(profiles) "
        stdscr.addstr(h-1, 0, footer[:w-1], curses.A_REVERSE)
        stdscr.refresh()

        ch = stdscr.getch()
        if ch in (ord('q'), ord('Q'), 27):
            break
        if ch in PATHWAYS:
            name, argv = PATHWAYS[ch]
            try:
                subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                launched = f"{name}  @ {now}"
            except Exception as e:
                launched = f"{name}  ERROR: {e}"

    if log_proc:
        log_proc.terminate()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
