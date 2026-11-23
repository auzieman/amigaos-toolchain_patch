#!/usr/bin/env python3
# Replica-local: source closure for a powerpcspe cross build. For each wanted source, read
# Build-Depends (arch qualifiers evaluated for powerpcspe, cross: :native deps and arch:all/
# Multi-Arch foreign packages come from the build host and are skipped), map binaries to their
# source with apt-cache, and recurse into sources that are neither built nor host-only.
# Run in a frozen-root container with deb-src enabled. Args: built.txt locked.txt src...
import re, subprocess, sys
def sh(*a): return subprocess.run(a, capture_output=True, text=True).stdout
built = set(open(sys.argv[1]).read().split()); locked = set(open(sys.argv[2]).read().split())
def field(txt, name):
    m = re.search(r'^%s:(.*(?:\n[ \t].*)*)' % name, txt, re.M); return m.group(1) if m else ''
def deps(src):
    t = sh('apt-cache', 'showsrc', '--only-source', src).split('\n\n')[0]
    out = []
    for f in ('Build-Depends', 'Build-Depends-Arch'):
        for alt in field(t, f).replace('\n', ' ').split(','):
            first = alt.split('|')[0].strip()
            if not first: continue
            m = re.match(r'([a-z0-9][a-z0-9+.-]*)(:[a-z]+)?\s*(\([^)]*\))?\s*(\[[^]]*\])?\s*(<.*>)?', first)
            if not m: continue
            name, q, _, arch, prof = m.groups()
            if arch:
                al = arch[1:-1].split(); neg = al[0].startswith('!')
                hit = any(a.lstrip('!') in ('powerpcspe', 'linux-any', 'any') for a in al)
                if neg == hit: continue
            if prof and '!nocheck' in prof: continue
            out.append((name, q))
    return out
info = {}
def binfo(b):
    if b not in info:
        t = sh('apt-cache', 'show', '--no-all-versions', b)
        src = (field(t, 'Source').split() or [field(t, 'Package').strip()])[0] if t else None
        info[b] = (src, field(t, 'Architecture').strip(), field(t, 'Multi-Arch').strip())
    return info[b]
need, seen, todo, tools = {}, set(), list(sys.argv[3:]), {}
DEPTH = int(__import__('os').environ.get('DEPTH', '1')); level = {x: 0 for x in todo}
while todo:
    s = todo.pop(0)
    if s in seen: continue
    seen.add(s)
    for b, q in deps(s):
        src, arch, ma = binfo(b)
        if src is None: continue  # virtual (debhelper-compat etc.); provider is a host tool
        if q == ':native' or arch == 'all' or ma in ('foreign', 'allowed'): continue
        if not b.startswith('lib') and not b.endswith('-dev') and b not in ('xkb-data',): tools.setdefault(b, set()).add(s); continue
        if src in built: continue
        need.setdefault(src, set()).add(s)
        if src not in seen and level[s] + 1 < DEPTH: level.setdefault(src, level[s] + 1); todo.append(src)
for b in sorted(tools): print('%-28s %-8s <- %s' % (b, 'TOOL?', ' '.join(sorted(tools[b]))))
for src in sorted(need):
    print('%-28s %-8s <- %s' % (src, 'locked' if src in locked else 'NEW', ' '.join(sorted(need[src]))))
