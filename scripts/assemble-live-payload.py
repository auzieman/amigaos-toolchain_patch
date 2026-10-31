#!/usr/bin/env python3
"""Combine verified rescue components and provision a key-only lab account, without host keys."""
import argparse,hashlib,json,secrets,shutil,subprocess,tarfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','hardware-results','ssh-results','crypt-results','base-results',
          'debian-cache','toolchain-cache','authorized-key','output']:
    p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);root=a.output/'payload';root.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
metadata={};sources={}
for component in [a.hardware_results,a.ssh_results]:
    manifest=json.loads((component/'payload-manifest.json').read_text())
    sources[str(component)]=sha(component/'receipt.json')
    for f in manifest['files']:
        name=f['path'];source=(component/'payload'/name).resolve()
        assert source.is_relative_to((component/'payload').resolve()) and sha(source)==f['sha256']
        dest=root/name;assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest);metadata[name]={k:v for k,v in f.items() if k!='sha256'}

def put(name,data,mode=0o644,uid=0,gid=0):
    dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(data.encode() if isinstance(data,str) else data)
    metadata[name]={'path':name,'mode':mode,'uid':uid,'gid':gid}

key=a.authorized_key.read_text().strip()
assert key.startswith('ssh-ed25519 ') and '\n' not in key and len(key)<4096
# The random password is discarded; only key authentication is enabled.
password_hash=subprocess.check_output(['openssl','passwd','-6','-stdin'],
    input=(secrets.token_urlsafe(48)+'\n').encode()).decode().strip()
put('etc/passwd','root:x:0:0:root:/root:/bin/sh\nsshd:x:74:74:sshd:/var/empty:/bin/false\ntabor:x:1000:1000:Tabor:/home/tabor:/bin/sh\n')
put('etc/group','root:x:0:\nsshd:x:74:\ntabor:x:1000:\n')
put('etc/shadow','root:*:20000:0:99999:7:::\nsshd:*:20000:0:99999:7:::\ntabor:'+password_hash+':20000:0:99999:7:::\n',0o600)
put('etc/nsswitch.conf','passwd: files\ngroup: files\nshadow: files\nhosts: files dns\n')
put('etc/hosts','127.0.0.1 localhost\n')
put('home/tabor/.ssh/authorized_keys',key+'\n',0o600,1000,1000)
put('etc/ssh/sshd_config','''Port 22
AddressFamily inet
ListenAddress 0.0.0.0
HostKey /etc/ssh/ssh_host_ed25519_key
PidFile /run/sshd.pid
PermitRootLogin no
AllowUsers tabor
AuthenticationMethods publickey
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitEmptyPasswords no
UsePAM no
UseDNS no
AuthorizedKeysFile .ssh/authorized_keys
Subsystem sftp /usr/lib/openssh/sftp-server
''',0o600)
put('etc/start-ssh','''#!/bin/sh
set -eu
umask 077
mkdir -p /run /var/empty /var/log /dev/pts
grep -q ' /dev/pts ' /proc/mounts || mount -t devpts devpts /dev/pts
if [ ! -f /etc/ssh/ssh_host_ed25519_key ]; then
 echo 'Generating unique SSH host key for this live boot'
 /usr/bin/ssh-keygen -q -t ed25519 -N '' -f /etc/ssh/ssh_host_ed25519_key
fi
/usr/sbin/sshd -t -f /etc/ssh/sshd_config
/usr/sbin/sshd -E /tmp/sshd.log -f /etc/ssh/sshd_config
echo 'SSHD_READY: tabor public-key login; inspect ip addr for the LAN address'
''',0o755)
put('etc/start-network','''#!/bin/sh
set -eu
echo tabor-live > /proc/sys/kernel/hostname
for directory in /sys/class/net/*; do
 interface=${directory##*/}
 [ "$interface" = lo ] && continue
 echo "Trying wired DHCP on $interface"
 if udhcpc -q -n -t 5 -T 3 -i "$interface" -x hostname:tabor-live; then
  /etc/start-ssh
  ip addr show dev "$interface"
  echo NETWORK_SSH_READY > /dev/console
  exit 0
 fi
done
echo 'No DHCP lease; local rescue shell remains available'
exit 1
''',0o755)
put('etc/tabor-rescue.txt','''Experimental A1222 Linux hardware-validation image; E/Xorg not installed yet.
Wired DHCP/SSH starts in the background; inspect /tmp/network-boot.log.
Manual retry: ip link; udhcpc -i INTERFACE; /etc/start-ssh
SSH: tabor, key-only, unique host keys each live boot, no root/password login.
Console remains a root rescue shell. SSH is ordinary uid1000; no sudo in this slice.
SPE/glibc: spe-abi-check --cli (returns status; record every failure).
Fractal: fractal-test > /tmp/fractal.log (explicit SPE/no-libc demo, not GL).
QEMU still fails fenv rounding; no full ABI or physical GPU acceptance claimed.
No internal-disk installation. Keep firmware changes temporary; do not saveenv.
''')
for name,source in [('libxcrypt/COPYING.LIB',a.crypt_results/'source/COPYING.LIB'),
                    ('libxcrypt/LICENSING',a.crypt_results/'source/LICENSING')]:
    put('usr/share/licenses/'+name,source.read_bytes())
busybox=json.loads((a.project/'profiles/toolchain-bootstrap.json').read_text())
put('usr/share/licenses/busybox/LICENSE',(a.base_results/('busybox-'+busybox['busybox']['version'])/'LICENSE').read_bytes())
locks=json.loads((a.project/'profiles/debian-trixie.lock.json').read_text())
glibc=next(f for f in locks['components']['glibc']['files'] if '.orig.' in f['filename'])
archive=a.debian_cache/glibc['filename'];assert sha(archive)==glibc['sha256']
with tarfile.open(archive) as t:
    member=next(m for m in t if m.name.endswith('/COPYING.LIB'))
    put('usr/share/licenses/glibc/COPYING.LIB',t.extractfile(member).read())
archive=a.toolchain_cache/busybox['gcc']['filename']
assert hashlib.sha512(archive.read_bytes()).hexdigest()==busybox['gcc']['sha512']
with tarfile.open(archive) as t:
    found=0
    for member in t:
        if member.name.endswith(('/COPYING.RUNTIME','/COPYING3')) and member.name.count('/')==1:
            put('usr/share/licenses/gcc-runtime/'+Path(member.name).name,t.extractfile(member).read())
            found+=1
            if found==2:break
    assert found==2
directories=[{'path':x,'mode':0o755} for x in ['dev/pts','run','var/empty','var/log']]
directories += [{'path':'home/tabor','mode':0o700,'uid':1000,'gid':1000},
                {'path':'home/tabor/.ssh','mode':0o700,'uid':1000,'gid':1000}]
files=[]
for name in sorted(metadata):files.append({**metadata[name],'sha256':sha(root/name)})
manifest={'files':files,'directories':directories,'source_receipts_sha256':sources,
          'authorized_key_sha256':sha(a.authorized_key),'host_keys_in_image':False}
(a.output/'payload-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(a.output/'receipt.json').write_text(json.dumps({'status':'key-only-live-payload-assembled',
    'manifest_sha256':sha(a.output/'payload-manifest.json'),'physical_boot':False,
    'host_keys_in_image':False,'source_receipts_sha256':sources},indent=2)+'\n')
print('Key-only live payload assembled; no host/private client keys included.')
