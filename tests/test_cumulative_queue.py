"""Exercise dependency feedback/retry decisions without compiling target code."""
import json
import runpy
import signal
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/run-core-build-queue.py'
OLD='sha256:'+'a'*64
NEW='sha256:'+'b'*64

class CumulativeQueueTest(unittest.TestCase):
 def exercise(self,install_succeeds,metadata=False):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp); (base/'work').mkdir();project=base/'project';(project/'profiles/images').mkdir(parents=True)
   (project/'profiles/images/debian-package-builder.json').write_text(json.dumps({
    'server_base':str(base),'image_id':OLD,'packages':['consumer','prerequisite','broken'],
    'package_managed_root':True,'preserve_debian_version':True,'cpus':4,'memory':'6g',
    'pids_limit':256,'source_cache':'cache','tools':'tools','sysroot':'sysroot','source_lock':'lock',
    'tools_prefix':'/usr/lib/tabor-spe-toolchain','sysroot_prefix':'/'}))
   queue=project/'queue.json';queue.write_text(json.dumps({'accumulate_build_dependencies':True,
    'max_passes':4,'attempts':[{'package':x,'iteration':'511'} for x in ['consumer','prerequisite','broken']]}))
   output=base/'work/run';calls=[]
   def run(cmd,**kwargs):
    if cmd[0]=='docker':
     package=cmd[cmd.index('--package')+1]; pre='--check-dependencies-only' in cmd
     image=cmd[cmd.index('--image-id')+1];calls.append((package,pre,image))
     ready=package!='consumer' or image==NEW
     status=('build-dependencies-satisfied-not-built' if ready else 'build-dependencies-blocked') if pre else ('failed' if package=='broken' else 'debian-packages-built-not-target-installed')
     work=base/'work'/Path(cmd[cmd.index('--work')+1]).name;work.mkdir()
     (work/'receipt.json').write_text(json.dumps({'status':status}))
     return subprocess.CompletedProcess(cmd,0 if status.startswith(('build-dependencies-satisfied','debian-packages')) else 1)
    if cmd[0]=='python3':
     dest=Path(cmd[cmd.index('--output')+1]);dest.mkdir()
     (dest/'receipt.json').write_text(json.dumps({'status':'target-libraries-installed-in-build-root' if install_succeeds else 'installation-deferred','image_id':NEW if install_succeeds else OLD}))
     return subprocess.CompletedProcess(cmd,0 if install_succeeds else 1)
    raise AssertionError(cmd)
   previous=signal.getsignal(signal.SIGTERM)
   try:
    with patch.object(sys,'argv',[str(SCRIPT),'--project',str(project),'--queue',str(queue),'--output',str(output)]),patch('subprocess.check_output',return_value='tabor-source-reader\tmetadata\n' if metadata else ''),patch('subprocess.run',side_effect=run):
     runpy.run_path(str(SCRIPT),run_name='__main__')
   finally:signal.signal(signal.SIGTERM,previous)
   return json.loads((output/'receipt.json').read_text()),calls
 def test_new_library_unlocks_prior_consumer_and_compile_failure_is_not_retried(self):
  result,calls=self.exercise(True)
  latest={x['package']:x for x in result['latest_items']}
  self.assertEqual(latest['consumer']['status'],'debian-packages-built-not-target-installed')
  self.assertEqual(latest['consumer']['iteration'],'512')
  self.assertEqual(sum(p=='broken' and not pre for p,pre,_ in calls),1)
  self.assertFalse(result['target_installation']);self.assertFalse(result['boot_image_ready'])
 def test_explicit_metadata_job_does_not_skip_builds(self):
  result,calls=self.exercise(True,metadata=True)
  self.assertTrue(any(p=='consumer' and not pre for p,pre,_ in calls))
  self.assertFalse(any(x['status']=='attempt-failed' for x in result['items']))
 def test_failed_install_keeps_parent_and_does_not_spin_on_blocked_consumer(self):
  result,calls=self.exercise(False)
  self.assertEqual(result['current_build_image'],OLD)
  self.assertEqual(sum(p=='consumer' for p,_,_ in calls),1)
  self.assertTrue(result['pending_library_receipts'])
  self.assertEqual(result['status'],'completed-with-deferred-items')

if __name__=='__main__':unittest.main()
