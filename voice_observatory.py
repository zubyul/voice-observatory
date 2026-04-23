#!/usr/bin/env python3
"""voice-observatory - passive TUI watching macOS voice-download invariant
AND bag coverage from the voice-tree-decomposition spec.

Invariants watched:
  - say -v '?' count (total / Premium / Enhanced / Standard)
  - /private/var/MobileAsset/AssetsV2/com_apple_MobileAsset_VoiceServicesVocalizerVoice/
  - bag coverage from voice-neighbors.json (if present alongside this file)
  - live log stream on com.apple.MobileAsset events
"""
import curses
import subprocess
import time
import os
import sys
import json
import re
from collections import deque
from datetime import datetime

try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:
    HERE = os.getcwd()
NEIGHBORS = os.path.join(HERE, "voice-neighbors.json")
ASSET_DIR = ("/private/var/MobileAsset/AssetsV2/"
             "com_apple_MobileAsset_VoiceServicesVocalizerVoice")
POLL_SEC = 2.0

PATHWAYS = {
    ord('1'): ("P1 Settings (GUI)", ["open", "-a", "System Settings"]),
    ord('2'): ("P2 URL deep-link",
               ["open", "x-apple.systempreferences:com.apple.Accessibility-Settings.extension?Spoken Content"]),
    ord('3'): ("P3 AppleScript",
               ["osascript", "-e",
                'open location "x-apple.systempreferences:com.apple.Accessibility-Settings.extension?Spoken Content"']),
    ord('4'): ("P4 VoiceOver Utility",
               ["open", "-a", "/System/Library/CoreServices/VoiceOver Utility.app"]),
    ord('5'): ("P5 Configuration profiles",
               ["open", "x-apple.systempreferences:com.apple.preferences.configurationprofiles"]),
}

def voices_raw():
    try:
        return subprocess.check_output(["say", "-v", "?"], text=True, timeout=2)
    except Exception:
        return ""

def parse_installed(raw):
    names = set()
    premium = enhanced = total = 0
    for line in raw.splitlines():
        if not line.strip(): continue
        total += 1
        if "(Premium)" in line: premium += 1
        elif "(Enhanced)" in line: enhanced += 1
        m = re.match(r"^([^#]+?)\s+[a-z]{2}[_A-Z]*(?:@[^#]*)?\s*#", line)
        if m:
            names.add(m.group(1).strip())
    return names, total, premium, enhanced

def load_bags():
    try:
        with open(NEIGHBORS) as f:
            return json.load(f)
    except Exception:
        return None

def bag_stats(bags, installed):
    out = []
    for bag_name, members in bags["bags"].items():
        have = [m for m in members if m in installed]
        out.append((bag_name, len(have), len(members), members, have))
    return out

def next_target(bags, installed):
    for v in bags.get("install_order_by_poetics", []):
        if v not in installed:
            return v
    return None

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
             '(eventMessage CONTAINS[c] "VocalizerVoice")'],
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
    curses.init_pair(4, curses.COLOR_RED, -1)
    stdscr.nodelay(True)
    stdscr.timeout(int(POLL_SEC * 1000))

    bags = load_bags()
    events = deque(maxlen=500)
    log_proc = spawn_log_stream()

    raw = voices_raw()
    init_names, init_total, init_prem, init_enh = parse_installed(raw)
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

        raw = voices_raw()
        names, total, premium, enhanced = parse_installed(raw)
        assets = asset_count()
        d_total = total - init_total
        d_prem = premium - init_prem
        d_enh = enhanced - init_enh
        d_assets = assets - init_assets

        h, w = stdscr.getmaxyx()
        stdscr.erase()
        now = datetime.now().strftime("%H:%M:%S")

        header = f" voice-observatory  {now}  |  Δtotal={d_total:+d}  Δprem={d_prem:+d}  Δenh={d_enh:+d}  Δassets={d_assets:+d} "
        col = curses.color_pair(1 if (d_total>0 or d_assets>0) else 3) | curses.A_REVERSE
        stdscr.addstr(0, 0, header[:w-1], col)

        row = 2
        stdscr.addstr(row, 2, f"installed: {total}  ({premium} Premium · {enhanced} Enhanced · {total-premium-enhanced} Standard)"); row+=1
        stdscr.addstr(row, 2, f"MobileAsset dir entries: {assets}  (init {init_assets})"); row+=1

        if launched:
            stdscr.addstr(row, 2, f"LAUNCHED: {launched}", curses.color_pair(3) | curses.A_BOLD); row+=1
        row += 1

        if bags:
            stats = bag_stats(bags, names)
            complete = sum(1 for s in stats if s[1] == s[2])
            partial = sum(1 for s in stats if 0 < s[1] < s[2])
            empty = sum(1 for s in stats if s[1] == 0)
            stdscr.addstr(row, 0, f" bag coverage: {complete} full · {partial} partial · {empty} empty (of {len(stats)}) ".center(w-1, "-")); row+=1

            nxt = next_target(bags, names)
            if nxt:
                stdscr.addstr(row, 2, f"next install (poetics order): {nxt}", curses.color_pair(2) | curses.A_BOLD); row+=1
            row += 1

            for name, got, need, members, have in stats:
                if row >= h - 6: break
                if got == need:
                    color = curses.color_pair(1)
                    bar = "[" + ("#" * need) + "]"
                elif got > 0:
                    color = curses.color_pair(3)
                    bar = "[" + ("#" * got) + ("." * (need - got)) + "]"
                else:
                    color = curses.color_pair(4)
                    bar = "[" + ("." * need) + "]"
                missing = [m for m in members if m not in have]
                mstr = "OK" if got == need else "missing: " + ", ".join(missing[:2]) + (" ..." if len(missing) > 2 else "")
                detail = f"{bar} {name:<10} {got}/{need}  {mstr}"
                stdscr.addstr(row, 2, detail[:w-3], color); row+=1
        else:
            stdscr.addstr(row, 2, f"(voice-neighbors.json not found at {NEIGHBORS})", curses.color_pair(3)); row+=2

        row += 1
        stdscr.addstr(row, 0, " MobileAsset / VocalizerVoice events ".center(w-1, "-")); row+=1
        for i, ev in enumerate(list(events)[-(h-row-2):]):
            if row + i >= h - 1: break
            stdscr.addstr(row+i, 0, ev[:w-1])

        footer = " q=quit . 1=P1 Settings . 2=P2 URL . 3=P3 AppleScript . 4=P4 VoiceOver . 5=P5 profiles "
        stdscr.addstr(h-1, 0, footer[:w-1], curses.A_REVERSE)
        stdscr.refresh()

        ch = stdscr.getch()
        if ch in (ord('q'), ord('Q'), 27): break
        if ch in PATHWAYS:
            name, argv = PATHWAYS[ch]
            try:
                subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                launched = f"{name}  @ {now}"
            except Exception as e:
                launched = f"{name}  ERROR: {e}"

    if log_proc: log_proc.terminate()

if __name__ == "__main__":
    try: curses.wrapper(main)
    except KeyboardInterrupt: sys.exit(0)
