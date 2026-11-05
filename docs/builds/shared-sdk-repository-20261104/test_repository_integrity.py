import unittest,tempfile,sys,subprocess
from pathlib import Path
sys.path.insert(0,'/tmp/tabor-repository-proof-scripts')
from sbuild_local_repository import prepare
class RepositoryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name);self.extras=self.base/'extras';self.extras.mkdir();pkg=self.base/'pkg';(pkg/'DEBIAN').mkdir(parents=True);(pkg/'DEBIAN/control').write_text('Package: local-repository-fixture\nVersion: 1\nArchitecture: all\nMaintainer: test <test@localhost>\nDescription: repository integrity fixture\n');subprocess.run(['dpkg-deb','--build',str(pkg),str(self.extras/'fixture.deb')],stdout=subprocess.DEVNULL,check=True)
 def tearDown(self):
  for p in self.base.rglob('*'):
   if p.is_dir():p.chmod(0o755)
  self.temp.cleanup()
 def test_reuse(self):
  a,r=prepare(self.extras,self.base/'repo');b,s=prepare(self.extras,self.base/'repo');self.assertEqual(a,b);self.assertEqual(r,s);self.assertIn('Package: local-repository-fixture',(a/'Packages').read_text())
 def test_tamper_rejected(self):
  a,r=prepare(self.extras,self.base/'repo');(a/'fixture.deb').chmod(0o644);(a/'fixture.deb').write_bytes(b'corrupt')
  with self.assertRaises(AssertionError):prepare(self.extras,self.base/'repo')
if __name__=='__main__':unittest.main()
