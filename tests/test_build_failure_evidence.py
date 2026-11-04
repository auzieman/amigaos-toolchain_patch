import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_failure_evidence import archive_failures
class AcquisitionEvidenceTests(unittest.TestCase):
 def test_fetch_error_before_long_summary_is_retained(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'sbuild.log';p.write_text('E: Failed to fetch https://snapshot.example/file 504 Gateway Timeout\n'+'summary details\n'*900+'Fail-Stage: install-deps\n')
   self.assertTrue(archive_failures(p));self.assertNotIn('Failed to fetch',''.join(p.read_text().splitlines(True)[-700:]))
 def test_source_error_is_not_acquisition(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'sbuild.log';p.write_text('main.c:4: error: invalid type\nFail-Stage: build\n')
   self.assertEqual(archive_failures(p),[])
if __name__=='__main__':unittest.main()
