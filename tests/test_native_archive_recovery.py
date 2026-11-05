"""Actual apt choices, frozen origins and primary-failure recovery boundaries."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import tempfile
import unittest
from native_archive_recovery import requests_for_failure
from apt_archive_cache import prepare, refresh

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.prefix = 'https://snapshot.debian.org/archive/debian/20261102T220000Z/'
        self.index = self.base / 'Packages'
        self.index.write_text(
            'Package: byacc\nVersion: 1:2\nArchitecture: amd64\nFilename: pool/main/b/byacc/byacc_2_amd64.deb\n\n'
            'Package: headers\nVersion: 1+deb1\nArchitecture: all\nFilename: pool/main/h/headers/headers_1+deb1_all.deb\n\n'
            'Package: target\nVersion: 1\nArchitecture: powerpcspe\nFilename: pool/main/t/target/target_1_powerpcspe.deb\n\n')
        self.log = self.base / 'sbuild.log'

    def requests(self, lines, stage='install-deps'):
        self.log.write_text(lines + '\nFail-Stage: ' + stage + '\n')
        return requests_for_failure(self.log, self.index, [{'url': self.prefix}])

    def test_actual_alternative_and_arch_all_requests(self):
        lines = ('E: Failed to fetch ' + self.prefix + 'pool/main/b/byacc/byacc_2_amd64.deb 504\n'
                 'E: Failed to fetch ' + self.prefix + 'pool/main/h/headers/headers_1%2bdeb1_all.deb 503\n'
                 'E: Package installation failed')
        self.assertEqual(self.requests(lines), ['byacc=1:2', 'headers=1+deb1'])

    def test_secondary_explainer_download_does_not_retry_conflict(self):
        lines = ('E: Package installation failed\nE: Failed to fetch ' +
                 self.prefix + 'pool/main/b/byacc/byacc_2_amd64.deb 503')
        self.assertEqual(self.requests(lines), [])

    def test_compilation_failure_does_not_trigger_acquisition_retry(self):
        self.assertEqual(self.requests('E: Failed to fetch ' + self.prefix +
                         'pool/main/b/byacc/byacc_2_amd64.deb 503', 'build'), [])

    def test_unknown_origin_file_and_target_not_recovered_as_native(self):
        lines = '\n'.join('E: Failed to fetch ' + url + ' 503' for url in [
            'https://other.invalid/pool/main/b/byacc/byacc_2_amd64.deb',
            self.prefix + 'pool/main/b/byacc/byacc_3_amd64.deb',
            self.prefix + 'pool/main/t/target/target_1_powerpcspe.deb'])
        self.assertEqual(self.requests(lines), [])

    def test_failed_worker_receives_new_pool_files(self):
        import os
        cache, seed = self.base / 'cache', self.base / 'seed'
        seed.mkdir()
        worker = prepare(cache, 'job', seed, os.getuid(), os.getgid())
        (worker / 'retained.deb').write_bytes(b'prior download')
        (cache / 'pool' / 'recovered.deb').write_bytes(b'new verified download')
        self.assertFalse((worker / 'recovered.deb').exists())
        self.assertEqual(refresh(cache, worker), 1)
        self.assertEqual((worker / 'recovered.deb').read_bytes(), b'new verified download')
        self.assertEqual((cache / 'pool' / 'retained.deb').read_bytes(), b'prior download')

if __name__ == '__main__':
    unittest.main()
