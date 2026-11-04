#!/usr/bin/env python3
"""Bounded native offline apt cache regression, run as root on the R730."""
import argparse,json,subprocess,hashlib
from apt_archive_cache import prepare, retain
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--native-root',type=Path,required=True)
p.add_argument('--cache',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();out=a.output;out.mkdir(exist_ok=False)
root=a.native_root;base=a.cache
w=prepare(base,out.name,root/'var/cache/apt/archives',1000,1000)
a=next(w.glob('libbrotli1_*_amd64.deb'))
name,version=subprocess.check_output(['dpkg-deb','-f',str(a),'Package','Version'],text=True).splitlines();name=name.split(': ',1)[-1];version=version.split(': ',1)[-1]
cmd=['systemd-nspawn','--quiet','--private-network','--read-only','-D',str(root),'--bind='+str(w)+':/var/cache/apt/archives','apt-get','-o','Debug::NoLocking=true','-o','Dir::Log=/tmp','-o','Dir::State::extended_states=/tmp/extended_states','--download-only','--reinstall','-y','install',name+'='+version]
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(out/'offline-apt.log').write_text(r.stdout)
receipt={'network':'nspawn private-network; no host interfaces','command':cmd,'exit':r.returncode,'archives_seeded':len(list(w.glob('*.deb'))),'package':name,'version':version,'archive_sha256':hashlib.sha256(a.read_bytes()).hexdigest(),'apt_output':r.stdout,'retention':retain(base,w)}
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));assert r.returncode==0 and 'Need to get 0 B/' in r.stdout
