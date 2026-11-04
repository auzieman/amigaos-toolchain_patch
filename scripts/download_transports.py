"""Explicit exact-file transport; never selects versions or downloads indexes."""
import re
from urllib.parse import urlsplit

def exact_file_cdn(snapshot_url):
    u=urlsplit(snapshot_url)
    if u.scheme!='https' or u.netloc!='snapshot.debian.org' or u.query or u.fragment:
        raise ValueError('Expected the original frozen Snapshot file URI')
    m=re.fullmatch(r'/archive/(debian|debian-security)/(\d{8}T\d{6}Z)/(pool/.+)',u.path)
    if not m or '..' in m[3].split('/'):
        raise ValueError('Only pinned pool files are eligible, never suite metadata')
    return 'https://deb.debian.org/'+m[1]+'/'+m[3]
