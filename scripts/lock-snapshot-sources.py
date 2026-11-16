#!/usr/bin/env python3
"""Write a source lock for Debian source packages from the frozen root's snapshot.

Run inside a frozen-root container whose apt sources also carry the matching
deb-src lines. Versions, sizes and SHA256 come from apt's signed Sources index
(`apt-get source --print-uris`), so each locked version is the one whose amd64
binaries the frozen root installs. That is what Multi-Arch: same coinstallation
needs. Every payload is downloaded once and its SHA256 checked before the
entry is written.
"""
import argparse, hashlib, json, re, subprocess, urllib.request

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output', required=True)
p.add_argument('--scope', required=True)
p.add_argument('sources', nargs='+')
a = p.parse_args()

components = {}
for src in a.sources:
    out = subprocess.run(['apt-get', 'source', '--print-uris', '--only-source', src],
                         capture_output=True, text=True, check=True).stdout
    files = []
    for url, name, size, digest in re.findall(r"^'([^']+)' (\S+) (\d+) SHA256:([0-9a-f]{64})$", out, re.M):
        with urllib.request.urlopen(url) as r:
            data = r.read()
        assert len(data) == int(size) and hashlib.sha256(data).hexdigest() == digest, (src, name)
        files.append({'filename': name, 'url': url, 'size': int(size), 'sha256': digest})
    dsc = [f['filename'] for f in files if f['filename'].endswith('.dsc')]
    assert len(dsc) == 1, (src, out)
    # showsrc can list several suites; keep the version whose .dsc apt chose.
    shown = re.findall(r'^Version: (\S+)$', subprocess.run(
        ['apt-cache', 'showsrc', '--only-source', src], capture_output=True, text=True, check=True).stdout, re.M)
    matches = {v for v in shown if dsc[0] == '%s_%s.dsc' % (src, v.split(':', 1)[-1])}
    assert len(matches) == 1, (src, shown, dsc)
    version = matches.pop()
    components[src] = {'version': version, 'dsc': dsc[0], 'files': files,
                       'reference': 'https://packages.debian.org/source/trixie/' + src}
with open(a.output, 'w', newline='\n') as f:
    json.dump({'scope': a.scope,
               'signature_verification': 'SHA256 from the snapshot\'s signed Sources index; payloads re-hashed on download',
               'components': components}, f, indent=2)
    f.write('\n')
print(' '.join('%s=%s' % (k, v['version']) for k, v in components.items()))
