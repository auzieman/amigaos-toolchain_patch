import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('compiler_provenance',Path(__file__).parents[1]/'scripts/compiler_provenance.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CompilerProvenance(unittest.TestCase):
    def test_only_current_qualified_sdk_is_reusable(self):
        policy={'qualification_status':'passed','required_gcc_major':14,'qualified_sdk_receipt_sha256':'current'}
        for evidence, expected in [({},False),({'gcc_major':8,'sdk_receipt_sha256':'current'},False),({'gcc_major':14,'sdk_receipt_sha256':'old'},False),({'gcc_major':14,'sdk_receipt_sha256':'current'},True)]:
            with self.subTest(evidence=evidence):
                self.assertEqual(m.matches_qualified_compiler({'compiler':evidence},policy),expected)
        policy['qualification_status']='pending'
        self.assertFalse(m.matches_qualified_compiler({'compiler':{'gcc_major':14,'sdk_receipt_sha256':'current'}},policy))
if __name__=='__main__':unittest.main()
