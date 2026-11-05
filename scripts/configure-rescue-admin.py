#!/usr/bin/env python3
"""Enable operator-key root SSH in an offline rescue root; never exports secrets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--root',type=Path,required=True)
p.add_argument('--receipt',type=Path,required=True)
a=p.parse_args()
assert os.geteuid()==0 and not a.receipt.exists()
root=a.root.resolve()
def path(name):
    result=root/name
    assert result.resolve().is_relative_to(root)
    return result
key=path('home/tabor/.ssh/authorized_keys').read_bytes()
assert key.startswith(b'ssh-ed25519 ') and key.count(b'\n')==1
shadow=path('etc/shadow').read_text()
account=next(line.split(':') for line in shadow.splitlines() if line.startswith('tabor:'))
# Existing random/discarded password hash keeps the account usable for keys.
# SSH password authentication stays disabled for every account.
assert re.fullmatch(r'\$6\$[A-Za-z0-9./$]+',account[1])
updated=re.sub(r'^root:[^:]*:',lambda _: 'root:'+account[1]+':',shadow,flags=re.M)
assert updated!=shadow or shadow.startswith('root:'+account[1]+':')
config=path('etc/ssh/sshd_config').read_text()
assert 'PasswordAuthentication no' in config and 'AuthenticationMethods publickey' in config
assert 'PermitRootLogin no' in config or 'PermitRootLogin prohibit-password' in config
config=config.replace('PermitRootLogin no','PermitRootLogin prohibit-password')
config=config.replace('AllowUsers tabor\n','AllowUsers tabor root\n')
# This reduced rescue OpenSSH was built without PAM.
config='\n'.join(line for line in config.splitlines() if not line.startswith('UsePAM '))+'\n'
directory=path('root/.ssh');directory.mkdir(parents=True,exist_ok=True)
os.chown(directory,0,0);directory.chmod(0o700)
authorized=directory/'authorized_keys';authorized.write_bytes(key);os.chown(authorized,0,0);authorized.chmod(0o600)
path('etc/shadow').write_text(updated);path('etc/shadow').chmod(0o600)
path('etc/ssh/sshd_config').write_text(config);path('etc/ssh/sshd_config').chmod(0o600)
a.receipt.parent.mkdir(parents=True,exist_ok=True)
receipt={'status':'rescue-key-only-root-admin-configured',
         'public_key_sha256':hashlib.sha256(key).hexdigest(),
         'password_authentication':False,'new_private_keys_added':False,
         'su_or_sudo_installed':False,'runtime_verified':False}
a.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
