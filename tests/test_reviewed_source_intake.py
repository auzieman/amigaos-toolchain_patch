"""Synthetic frozen metadata tests; no source download or target execution."""
import hashlib
import json
import lzma
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(os.environ.get('INTAKE_SCRIPT', Path(__file__).resolve().parents[1] / 'scripts/plan-port-dependency-intake.py'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

class ReviewedIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.audit = self.base / 'audit'
        self.indexes = self.base / 'indexes'
        self.audit.mkdir()
        self.indexes.mkdir()
        source = 'Package: existing\nVersion: 1\n\n'
        other = 'Package: hidden\nVersion: 2\n\n'
        (self.audit / 'Sources').write_text(source)
        (self.audit / 'SpePackages').write_text('')
        (self.audit / 'NativePackages').write_text('')
        (self.audit / 'dependency-report.yaml').write_text('report: []\n')
        (self.audit / 'receipt.json').write_text(json.dumps({
            'status': 'debian-dependency-audit-completed',
            'base_lock_sha256': 'fixture',
            'native_packages_sha256': sha(self.audit / 'NativePackages'),
            'report_sha256': sha(self.audit / 'dependency-report.yaml'),
        }))
        archive = self.indexes / '0-Sources.xz'
        archive.write_bytes(lzma.compress((source + other).encode()))
        (self.indexes / 'receipt.json').write_text(json.dumps({
            'base_lock_sha256': 'fixture',
            'source_indexes': [{'sha256': sha(archive)}],
        }))

    def run_intake(self, manifest, allowed):
        path = self.base / 'reviewed.json'
        path.write_text(json.dumps(manifest))
        output = self.base / 'output'
        result = subprocess.run([
            '/usr/bin/python3', str(SCRIPT), '--audit', str(self.audit),
            '--source-indexes', str(self.indexes), '--output', str(output),
            '--only-producers', *allowed, '--reviewed-producers', str(path),
        ], capture_output=True, text=True)
        return result, output

    def test_explicit_hidden_and_existing_sources_keep_frozen_versions(self):
        reasons = {'existing': 'Required target library', 'hidden': 'Declared prerequisite behind first solver error'}
        result, output = self.run_intake(reasons, list(reasons))
        self.assertEqual(result.returncode, 0, result.stderr)
        plan = json.loads((output / 'source-intake-plan.json').read_text())['components']
        self.assertEqual({n: x['version'] for n, x in plan.items()}, {'existing': '1', 'hidden': '2'})
        self.assertEqual(plan['hidden']['reason'], reasons['hidden'])
        candidates = (output / 'candidate-Sources').read_text()
        self.assertIn('Package: existing', candidates)
        self.assertIn('Package: hidden', candidates)

    def test_unknown_source_rejected(self):
        result, output = self.run_intake({'absent': 'Cannot invent a source'}, ['absent'])
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((output / 'source-intake-plan.json').exists())

    def test_manifest_cannot_expand_reviewed_scope(self):
        result, output = self.run_intake({'hidden': 'Not allowlisted'}, ['existing'])
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((output / 'source-intake-plan.json').exists())

if __name__ == '__main__':
    unittest.main()
