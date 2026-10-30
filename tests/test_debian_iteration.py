"""Check cache rejection and fresh-run patch replay with a tiny extraction fixture."""
import hashlib,json,os
from pathlib import Path
import subprocess,tempfile,unittest
RUNNER=Path(__file__).resolve().parents[1]/'scripts/debian-iterate.py'
class Iteration(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.project=self.root/'project';self.cache=self.root/'cache';self.bin=self.root/'bin'
  for p in [self.project/'profiles',self.project/'patches/linux',self.cache,self.bin]:p.mkdir(parents=True)
  data=b'fixture source descriptor';(self.cache/'fixture.dsc').write_bytes(data)
  f={'filename':'fixture.dsc','size':len(data),'sha256':hashlib.sha256(data).hexdigest()}
  (self.project/'profiles/debian-trixie.lock.json').write_text(json.dumps({'components':{'linux':{'version':'fixture','dsc':'fixture.dsc','files':[f]}}}))
  (self.project/'patches/linux/series').write_text('board.patch\n')
  (self.project/'patches/linux/board.patch').write_text('--- a/board\n+++ b/board\n@@ -1 +1 @@\n-old\n+new\n')
  # Extraction fixture only; the real Debian dpkg-source path is exercised by lab builds.
  tool=self.bin/'dpkg-source';tool.write_text('#!/usr/bin/env python3\nimport sys\nfrom pathlib import Path\np=Path(sys.argv[-1]);p.mkdir();(p/"board").write_text("old\\n")\n');tool.chmod(0o755)
 def run_at(self,name):
  return subprocess.run(['python3',str(RUNNER),'--project',str(self.project),'--cache',str(self.cache),'--work',str(self.root/name),'--component','linux','--mode','prepare','--image-id','sha256:'+'b'*64],env={**os.environ,'PATH':str(self.bin)+os.pathsep+os.environ['PATH']},capture_output=True,text=True)
 def test_each_run_repatches_clean_source_and_refuses_reuse(self):
  for name in ['one','two']:
   result=self.run_at(name);self.assertEqual(result.returncode,0,result.stderr)
   self.assertEqual((self.root/name/'source/board').read_text(),'new\n')
   self.assertEqual(json.loads((self.root/name/'receipt.json').read_text())['status'],'prepared')
  self.assertNotEqual(self.run_at('one').returncode,0)
  self.assertEqual((self.cache/'fixture.dsc').read_bytes(),b'fixture source descriptor')
 def test_bad_cache_stops_before_extraction(self):
  (self.cache/'fixture.dsc').write_bytes(b'corrupt')
  self.assertNotEqual(self.run_at('bad').returncode,0)
  receipt=json.loads((self.root/'bad/receipt.json').read_text())
  self.assertEqual(receipt['status'],'failed');self.assertFalse((self.root/'bad/source').exists())
if __name__=='__main__':unittest.main()
