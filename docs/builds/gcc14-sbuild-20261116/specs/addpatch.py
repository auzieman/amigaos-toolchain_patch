#!/usr/bin/env python3
"""Replica-local: copy source_patch from the project's own spec into a local spec."""
import json, sys
s = json.load(open(sys.argv[1])); s['source_patch'] = json.load(open(sys.argv[2]))['source_patch']; json.dump(s, open(sys.argv[1], 'w'), indent=2)
