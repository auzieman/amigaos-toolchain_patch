"""Exercise source isolation and rejected inputs using a real tiny Git repository."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

RUNNER = Path(__file__).resolve().parents[1] / 'scripts/kernel-build.py'

class Preparation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.inputs = self.root / 'inputs'
        self.source = self.inputs / 'linux'
        self.source.mkdir(parents=True)
        self.git('init', '-q')
        self.git('config', 'user.name', 'Fixture')
        self.git('config', 'user.email', 'fixture@example.invalid')
        (self.source / 'board.txt').write_text('old\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'baseline')
        commit = self.git('rev-parse', 'HEAD').strip()
        (self.inputs / 'board.patch').write_text('--- a/board.txt\n+++ b/board.txt\n@@ -1 +1 @@\n-old\n+new\n')
        (self.inputs / 'config').write_text('CONFIG_PPC=y\n')
        def item(name):
            return {'path': name, 'sha256': hashlib.sha256((self.inputs/name).read_bytes()).hexdigest()}
        self.profile = self.root / 'profile.json'
        self.profile.write_text(json.dumps({'commit': commit, 'source': 'linux',
                                           'patches': [item('board.patch')], 'copies': [],
                                           'config': item('config')}))
        self.work = self.root / 'run'

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.source), *args], text=True)

    def run_prepare(self):
        return subprocess.run(['python3', str(RUNNER), '--profile', str(self.profile),
                               '--inputs', str(self.inputs), '--work', str(self.work),
                               '--prepare-only', '--image-id', 'sha256:'+'a'*64],
                              capture_output=True, text=True)

    def test_committed_input_only_and_no_reuse(self):
        (self.source / 'untracked.txt').write_text('private draft')
        result = self.run_prepare()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.work/'source/board.txt').read_text(), 'new\n')
        self.assertEqual((self.source/'board.txt').read_text(), 'old\n')
        self.assertFalse((self.work/'source/untracked.txt').exists())
        receipt = json.loads((self.work/'receipt.json').read_text())
        self.assertEqual(receipt['status'], 'prepared')
        self.assertFalse(receipt['boot_tested'])
        self.assertNotEqual(self.run_prepare().returncode, 0)

    def test_hash_mismatch_retains_failure(self):
        (self.inputs/'board.patch').write_text('changed')
        self.assertNotEqual(self.run_prepare().returncode, 0)
        receipt = json.loads((self.work/'receipt.json').read_text())
        self.assertEqual(receipt['status'], 'failed')
        self.assertIn('hash mismatch', receipt['error'])
        self.assertEqual((self.source/'board.txt').read_text(), 'old\n')

    def test_patch_conflict_stops(self):
        p=self.inputs/'board.patch'
        p.write_text(p.read_text().replace('-old', '-absent'))
        profile=json.loads(self.profile.read_text())
        profile['patches'][0]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
        self.profile.write_text(json.dumps(profile))
        self.assertNotEqual(self.run_prepare().returncode, 0)
        self.assertEqual(json.loads((self.work/'receipt.json').read_text())['status'], 'failed')
        self.assertEqual((self.work/'source/board.txt').read_text(), 'old\n')

if __name__ == '__main__':
    unittest.main()
