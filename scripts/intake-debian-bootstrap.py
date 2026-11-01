#!/usr/bin/env python3
"""Cache selected Debian Trixie source inputs serially; no extraction or build."""
import argparse, hashlib, html, json, re, urllib.parse, urllib.request
from pathlib import Path
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--cache', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('packages', nargs='+')
a = p.parse_args(); a.cache.mkdir(parents=True, exist_ok=True)
assert not a.output.exists(), 'Use a fresh lock output'
sha = lambda data: hashlib.sha256(data).hexdigest()
components = {}
for package in a.packages:
    assert re.fullmatch(r'[a-z0-9][a-z0-9+.-]*', package)
    page = 'https://packages.debian.org/source/trixie/' + package
    data = urllib.request.urlopen(page, timeout=45).read().decode()
    url = html.unescape(re.search(r'href="([^"]+\.dsc)"', data)[1]).replace('http:', 'https:')
    def fetch(address):
        parsed = urllib.parse.urlparse(address)
        assert parsed.scheme == 'https' and parsed.hostname in ['deb.debian.org', 'security.debian.org']
        name = urllib.parse.unquote(parsed.path.rsplit('/', 1)[1])
        assert Path(name).name == name
        path = a.cache / name
        if not path.exists():
            temporary = path.with_name(path.name + '.partial')
            with urllib.request.urlopen(address, timeout=90) as src, temporary.open('xb') as dest:
                while chunk := src.read(1024 * 1024): dest.write(chunk)
            temporary.replace(path)
        return path
    dsc = fetch(url); text = dsc.read_text()
    files = [{'filename': dsc.name, 'url': url, 'size': dsc.stat().st_size, 'sha256': sha(dsc.read_bytes())}]
    block = re.search(r'^Checksums-Sha256:\n((?: [^\n]+\n)+)', text, re.M)[1]
    for line in block.splitlines():
        digest, size, name = line.split()
        address = url.rsplit('/', 1)[0] + '/' + urllib.parse.quote(name)
        path = fetch(address)
        assert path.stat().st_size == int(size) and sha(path.read_bytes()) == digest, path
        files.append({'filename': name, 'url': address, 'size': int(size), 'sha256': digest})
    components[package] = {'version': re.search(r'^Version: (.+)$', text, re.M)[1],
                            'dsc': dsc.name, 'files': files, 'reference': page}
    print(package, components[package]['version'], flush=True)
a.output.write_text(json.dumps({'scope': 'Trixie Essential/bootstrap source intake',
    'signature_verification': 'HTTPS DSC and payload SHA256; independent archive OpenPGP chain not yet verified',
    'components': components}, indent=2) + '\n')
