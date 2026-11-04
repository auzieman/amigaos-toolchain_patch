import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from download_transports import exact_file_cdn
class TransportTests(unittest.TestCase):
 def test_pool_uri_keeps_exact_filename(self):
  self.assertEqual(exact_file_cdn('https://snapshot.debian.org/archive/debian/20261102T220000Z/pool/main/j/json-c/json-c_0.18+ds-1.dsc'),'https://deb.debian.org/debian/pool/main/j/json-c/json-c_0.18+ds-1.dsc')
 def test_security_archive_is_preserved(self):
  self.assertEqual(exact_file_cdn('https://snapshot.debian.org/archive/debian-security/20261102T220000Z/pool/updates/main/a/a.deb'),'https://deb.debian.org/debian-security/pool/updates/main/a/a.deb')
 def test_metadata_and_other_origins_rejected(self):
  for url in ['https://snapshot.debian.org/archive/debian/20261102T220000Z/dists/trixie/Release','https://example.org/archive/debian/20261102T220000Z/pool/a.deb','https://snapshot.debian.org/archive/debian/20261102T220000Z/pool/../a.deb']:
   with self.assertRaises(ValueError):exact_file_cdn(url)
if __name__=='__main__':unittest.main()
