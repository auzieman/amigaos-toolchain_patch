import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('sdk_mount',Path(__file__).resolve().parents[1]/'scripts/shared_sdk_mount.py')
sdk=importlib.util.module_from_spec(spec);spec.loader.exec_module(sdk)

class MountContract(unittest.TestCase):
    def test_same_filesystem_bind_detected_by_exact_mountpoint(self):
        with patch.object(sdk.Path,'read_text',return_value='42 1 8:1 /sdk /sdk ro,relatime - ext4 /dev/sda rw\n'):
            self.assertEqual(sdk.exact_mounts('/sdk'),[['ro','relatime']])

    def test_repeated_preparation_does_not_mount_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'a/b/sdk';p.mkdir(parents=True)
            with patch.object(sdk,'exact_mounts',return_value=[['ro']]),patch.object(sdk.subprocess,'run') as run:
                for _ in range(10):sdk.ensure_read_only(p,{})
                run.assert_not_called()

    def test_duplicate_mounts_rejected_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'a/b/sdk';p.mkdir(parents=True)
            with patch.object(sdk,'exact_mounts',return_value=[['ro'],['ro']]),patch.object(sdk.subprocess,'run') as run:
                with self.assertRaises(AssertionError):sdk.ensure_read_only(p,{})
                run.assert_not_called()

    def test_worker_never_creates_missing_or_writable_mount(self):
        for mounts in [[],[['rw']]]:
            with patch.object(sdk,'exact_mounts',return_value=mounts),patch.object(sdk.subprocess,'run') as run:
                with self.assertRaises(AssertionError):sdk.require_read_only('/sdk')
                run.assert_not_called()

if __name__=='__main__':unittest.main()
