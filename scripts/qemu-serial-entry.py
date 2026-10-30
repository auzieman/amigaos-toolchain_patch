#!/usr/bin/env python3
"""Keep the container PTY transparent; let the guest handle serial line editing."""
import os
import sys
import tty
import termios

if len(sys.argv) < 2:
    raise SystemExit('Usage: qemu-serial-entry.py QEMU [arguments...]')
if os.isatty(0):
    tty.setraw(0)
    attrs = termios.tcgetattr(0)
    # QEMU enables OPOST again; clear its translation bits as well.
    attrs[1] = 0
    termios.tcsetattr(0, termios.TCSANOW, attrs)
os.execvp(sys.argv[1], sys.argv[1:])
