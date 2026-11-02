#!/usr/bin/env python3
"""Install Debian native build prerequisites for the reviewed source scope.

This adds existing amd64/all Debian binary packages, never native source builds.
It is a host-tool superset: target dependencies still need genuine powerpcspe
packages and dpkg-checkbuilddeps in every cross build. Fail-forward per source.
"""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
from debian.deb822 import Deb822
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--project',type=Path,required=True)
p.add_argument('--queue',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.output.mkdir(exist_ok=False)
profile=json.loads((a.project/'profiles/images/debian-package-builder.json').read_text())
spec=json.loads(a.queue.read_text());records=[]
for path in Path('/etc/apt/sources.list.d').glob('*.sources'):records.extend(Deb822.iter_paragraphs(path.open()))
selected=[]
for x in records:
 if any(s in ['trixie','trixie-updates','trixie-security'] for s in x.get('Suites','').split()) and any(host in x.get('URIs','') for host in ['deb.debian.org/debian','security.debian.org/debian-security']):
  assert 'Signed-By' in x and Path(x['Signed-By']).is_file()
  y=Deb822(x);y['Types']='deb-src';y['Components']='main';selected.append(y)
assert selected
Path('/etc/apt/sources.list.d/tabor-native-build-sources.sources').write_text('\n'.join(str(x) for x in selected))
r={'status':'running','recipe_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
   'role':'native Debian binary build prerequisites, not target libraries','items':[]}
def save():(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
env={**os.environ,'DEBIAN_FRONTEND':'noninteractive','LC_ALL':'C.UTF-8'}
with (a.output/'apt-update.log').open('w') as log:subprocess.run(['apt-get','update'],stdout=log,stderr=subprocess.STDOUT,check=True,env=env)
for item in spec['attempts']:
 name=item['package'];settings={**profile,**profile.get('package_inputs',{}).get(name,{})}
 lock=json.loads((a.project/settings['source_lock']).read_text());version=lock['components'][name]['version']
 cmd=['apt-get','build-dep','--arch-only','--no-remove','--no-install-recommends','-y',
      '--build-profiles=cross,nocheck',name+'='+version]
 with (a.output/(name+'.log')).open('w') as log:
  result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
 r['items'].append({'source':name,'version':version,'exit':result.returncode});save()
audit=subprocess.check_output(['dpkg','--audit'],text=True);assert not audit,audit
(a.output/'installed.tsv').write_text(subprocess.check_output(['dpkg-query','-W','-f=${binary:Package}\t${Version}\t${Architecture}\t${db:Status-Status}\n'],text=True))
r['status']='native-prerequisites-installed-with-deferred-sources' if any(x['exit'] for x in r['items']) else 'native-prerequisites-installed'
save()
