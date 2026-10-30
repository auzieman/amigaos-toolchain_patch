import json,subprocess,tempfile,unittest
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/'scripts/retain-iteration.py'
class Retention(unittest.TestCase):
 def test_retention_leaves_cache_and_discards_only_generated_trees(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);run=root/'work/linux-001';(run/'source').mkdir(parents=True);(run/'output').mkdir()
   (run/'receipt.json').write_text(json.dumps({'component':'linux','status':'failed'}))
   (run/'build.log').write_text('diagnostic');(run/'output/.config').write_text('CONFIG_TABOR=y\n')
   cache=root/'cache';cache.mkdir();(cache/'input').write_text('immutable')
   result=subprocess.run(['python3',str(SCRIPT),'--run',str(run),'--results',str(root/'results')],capture_output=True,text=True)
   self.assertEqual(result.returncode,0,result.stderr)
   self.assertEqual((root/'results/kernel.config').read_text(),'CONFIG_TABOR=y\n')
   self.assertFalse((run/'source').exists());self.assertFalse((run/'output').exists())
   self.assertEqual((cache/'input').read_text(),'immutable');self.assertTrue((run/'receipt.json').exists())
 def test_symlink_output_is_rejected_without_touching_reference(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);run=root/'work/linux-001';(run/'source').mkdir(parents=True)
   reference=root/'reference';reference.mkdir();(reference/'keep').write_text('original')
   (run/'output').symlink_to(reference,target_is_directory=True)
   result=subprocess.run(['python3',str(SCRIPT),'--run',str(run),'--results',str(root/'results')],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertTrue((run/'source').exists());self.assertEqual((reference/'keep').read_text(),'original')
if __name__=='__main__':unittest.main()
