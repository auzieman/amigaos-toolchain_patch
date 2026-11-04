"""Fault-injected source cache checks; synthetic metadata is not archive acceptance."""
import hashlib,json,lzma,os,subprocess,tempfile,unittest
from pathlib import Path
SCRIPT=Path(os.environ.get('CACHE_SOURCE_SCRIPT',Path(__file__).resolve().parents[1]/'scripts/cache-port-dependency-sources.py'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class SourceCacheTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.base=Path(self.tmp.name)
  self.intake=self.base/'intake';self.indexes=self.base/'indexes';self.cache=self.base/'cache';self.bin=self.base/'bin'
  for p in [self.intake,self.indexes,self.bin]:p.mkdir()
  payload=b'known source archive';checksum=hashlib.sha256(payload).hexdigest();names=['aa-broken','zz-good']
  text=''.join(f'Package: {name}\nVersion: 1\nDirectory: pool/{name}\nChecksums-Sha256:\n {checksum} {len(payload)} {name}_1.dsc\n\n' for name in names)
  (self.indexes/'0-Sources.xz').write_bytes(lzma.compress(text.encode()))
  (self.indexes/'receipt.json').write_text(json.dumps({'source_indexes':[{'sha256':digest(self.indexes/'0-Sources.xz'),'url':'https://snapshot.example/archive/pinned/dists/trixie/main/source/Sources.xz'}]}))
  (self.intake/'source-intake-plan.json').write_text(json.dumps({'components':{n:{'version':'1'} for n in names}}))
  (self.intake/'receipt.json').write_text(json.dumps({'status':'dependency-producer-intake-planned','plan_sha256':digest(self.intake/'source-intake-plan.json'),'source_index_receipt_sha256':digest(self.indexes/'receipt.json'),'base_lock_sha256':'fixture-only'}))
  curl=self.bin/'curl';curl.write_text('''#!/usr/bin/python3
import os,sys
from pathlib import Path
with open(os.environ['CURL_CALLS'],'a') as f:f.write(sys.argv[-3]+'\\n')
if 'aa-broken' in sys.argv[-3]:sys.exit(22)
Path(sys.argv[-1]).write_bytes(b'corrupt' if os.environ.get('CORRUPT_GOOD') else b'known source archive')
''');curl.chmod(0o755)
  self.calls=self.base/'calls';self.env={**os.environ,'PATH':str(self.bin)+':'+os.environ['PATH'],'CURL_CALLS':str(self.calls)}
 def execute(self,name):
  out=self.base/name
  subprocess.run(['/usr/bin/python3',str(SCRIPT),'--intake',str(self.intake),'--source-indexes',str(self.indexes),'--cache',str(self.cache),'--output',str(out)],env=self.env,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  return json.loads((out/'receipt.json').read_text()),json.loads((out/'sources.lock.json').read_text())
 def test_failure_does_not_stop_next_source(self):
  r,lock=self.execute('first');self.assertEqual(r['status'],'partial-source-archive-acquisition');self.assertEqual(list(lock['components']),['zz-good']);self.assertEqual(r['failures'][0]['source'],'aa-broken')
 def test_verified_archive_reused(self):
  self.execute('first');self.calls.write_text('');self.execute('second');self.assertNotIn('zz-good',self.calls.read_text())
 def test_bad_bytes_never_registered(self):
  self.env['CORRUPT_GOOD']='1';r,lock=self.execute('bad');self.assertEqual(lock['components'],{});self.assertEqual(len(r['failures']),2);self.assertFalse((self.cache/'zz-good_1.dsc').exists())
if __name__=='__main__':unittest.main()
