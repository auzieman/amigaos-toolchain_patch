"""Fault-injected native cache checks; synthetic metadata is not archive trust."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(os.environ.get('NATIVE_CACHE_SCRIPT', Path(__file__).resolve().parents[1] / 'scripts/cache-frozen-native-archives.py'))
sys.path.insert(0, str(SCRIPT.parent))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class NativeCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.audit = self.base / 'audit'
        self.audit.mkdir()
        self.cache = self.base / 'cache'
        self.cache.mkdir()
        self.payload = b'known archive'
        self.filename = 'fixture_1_amd64.deb'
        self.lock = self.base / 'lock.json'
        self.lock.write_text(json.dumps({'repositories': [{'url': 'https://snapshot.debian.org/archive/debian/20261102T220000Z/'}]}))
        (self.audit / 'NativePackages').write_text(
            'Package: fixture\nVersion: 1\nArchitecture: amd64\nFilename: pool/main/f/fixture/' + self.filename +
            '\nSHA256: ' + hashlib.sha256(self.payload).hexdigest() + '\n\n')
        (self.audit / 'receipt.json').write_text(json.dumps({
            'base_lock_sha256': sha(self.lock),
            'native_packages_sha256': sha(self.audit / 'NativePackages'),
        }))

    def execute(self, download, version='1'):
        output = self.base / 'output'
        args = [str(SCRIPT), '--audit', str(self.audit), '--lock', str(self.lock),
                '--cache', str(self.cache), '--output', str(output),
                '--exact-file-cdn', 'fixture='+version]
        with patch.object(sys, 'argv', args), patch('subprocess.run', side_effect=download) as calls:
            runpy.run_path(str(SCRIPT), run_name='__main__')
        return json.loads((output / 'receipt.json').read_text()), calls

    def test_verified_cache_needs_no_network(self):
        (self.cache / self.filename).write_bytes(self.payload)
        receipt, calls = self.execute(lambda *a, **k: self.fail('Network contacted'))
        self.assertEqual(receipt['items'][0]['status'], 'reused')
        calls.assert_not_called()

    def test_cdn_failure_falls_back_to_same_pinned_snapshot_file(self):
        seen = []
        def download(cmd, **kwargs):
            url, destination = cmd[-3], Path(cmd[-2])
            self.assertFalse(destination.exists())
            seen.append(url)
            destination.write_bytes(self.payload)
            return subprocess.CompletedProcess(cmd, 1 if len(seen) == 1 else 0)
        receipt, calls = self.execute(download)
        self.assertEqual(receipt['status'], 'cached')
        self.assertEqual(len(seen), 2)
        self.assertIn('deb.debian.org/debian/pool/', seen[0])
        self.assertIn('snapshot.debian.org/archive/debian/20261102T220000Z/pool/', seen[1])
        self.assertEqual((self.cache / self.filename).read_bytes(), self.payload)

    def test_wrong_hash_is_not_published(self):
        def download(cmd, **kwargs):
            Path(cmd[-2]).write_bytes(b'wrong bytes')
            return subprocess.CompletedProcess(cmd, 0)
        with self.assertRaises(AssertionError):
            self.execute(download)
        self.assertFalse((self.cache / self.filename).exists())

    def test_epoch_cache_alias_reuses_pool_filename_without_network(self):
        package_index=self.audit/'NativePackages'
        package_index.write_text(package_index.read_text().replace('Version: 1\n','Version: 1:1\n'))
        proof=self.audit/'receipt.json'
        record=json.loads(proof.read_text());record['native_packages_sha256']=sha(package_index)
        proof.write_text(json.dumps(record))
        original=self.cache/self.filename;original.write_bytes(self.payload)
        receipt,calls=self.execute(lambda *a,**k:self.fail('Network contacted'),version='1:1')
        canonical=self.cache/'fixture_1%3a1_amd64.deb'
        calls.assert_not_called()
        self.assertEqual(canonical.read_bytes(),self.payload)
        self.assertEqual(canonical.stat().st_ino,original.stat().st_ino)
        self.assertEqual(receipt['items'][0]['filename'],canonical.name)

if __name__ == '__main__':
    unittest.main()
