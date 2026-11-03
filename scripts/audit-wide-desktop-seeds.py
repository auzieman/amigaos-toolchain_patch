#!/usr/bin/env python3
"""Probe broad desktop source Build-Depends using the frozen Debian universe.

Metadata only: no application source unpack, compilation or target execution.
These coverage probes do not become image package selections automatically.
"""
import argparse,hashlib,json,lzma,subprocess
from pathlib import Path
from debian.deb822 import Release,Sources
from debian.debian_support import Version
import yaml
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--dependency-audit',type=Path,required=True)
p.add_argument('--signed-index-cache',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--sources',nargs='+',default=['gnome-control-center','firefox-esr'])
a=p.parse_args();a.output.mkdir(exist_ok=False)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
parent=json.loads((a.dependency_audit/'receipt.json').read_text());assert parent['status']=='debian-dependency-audit-completed'
r={'status':'preparing','target_execution':False,'application_build_started':False,'image_selection_changed':False,'base_lock_sha256':parent['base_lock_sha256'],'dependency_audit_sha256':sha(a.dependency_audit/'receipt.json'),'source_indexes':[]}
try:
 selected={}
 for i,index in enumerate(parent['indexes']):
  release=a.signed_index_cache/(str(i)+'-InRelease');assert sha(release)==index['inrelease_sha256']
  with (a.output/(str(i)+'-signature.log')).open('w') as log:
   subprocess.run(['gpgv','--keyring','/usr/share/keyrings/debian-archive-keyring.gpg',release],stdout=log,stderr=subprocess.STDOUT,check=True)
  record=Release(release.open());entry=next(x for x in record['SHA256'] if x['name']=='main/source/Sources.xz')
  archive=a.output/(str(i)+'-Sources.xz')
  subprocess.run(['curl','--fail','--location','--retry','2','--max-time','120','--silent','--show-error',index['url']+entry['name'],'-o',archive],check=True)
  assert sha(archive)==entry['sha256'] and archive.stat().st_size==int(entry['size'])
  r['source_indexes'].append({'url':index['url']+entry['name'],'sha256':sha(archive)})
  with lzma.open(archive,'rt') as stream:
   for source in Sources.iter_paragraphs(stream,use_apt_pkg=False):
    name=source['Package']
    if name in a.sources and (name not in selected or Version(source['Version'])>Version(selected[name]['Version'])):selected[name]=source
 assert set(selected)==set(a.sources),'Missing requested source metadata'
 sources=a.output/'Sources'
 with sources.open('w') as out:
  for name,source in selected.items():
   (a.output/(name+'-source.txt')).write_text(str(source)+'\n');out.write(str(source)+'\n')
 r['sources']={n:{'version':s['Version'],'architecture':s['Architecture'],'build_depends':s.get('Build-Depends'),'build_depends_arch':s.get('Build-Depends-Arch'),'build_depends_indep':s.get('Build-Depends-Indep')} for n,s in selected.items()}
 native=a.dependency_audit/'NativePackages';spe=a.dependency_audit/'SpePackages'
 assert sha(native)==parent['native_packages_sha256']
 r['binary_inputs']={'native_sha256':sha(native),'spe_sha256':sha(spe)}
 cmd=['dose-builddebcheck','--deb-native-arch=amd64','--deb-host-arch=powerpcspe','--deb-profiles=cross,nocheck','--deb-drop-b-d-indep','--deb-emulate-sbuild','--failures','--successes','--explain',str(native),str(spe),str(sources)]
 with (a.output/'dependency-report.yaml').open('w') as out,(a.output/'dose.log').open('w') as err:
  result=subprocess.run(cmd,stdout=out,stderr=err)
 assert result.returncode in [0,1]
 report=yaml.load((a.output/'dependency-report.yaml').read_text(),Loader=yaml.BaseLoader)
 (a.output/'dependency-report.json').write_text(json.dumps(report,indent=2)+'\n')
 r.update(status='wide-desktop-dependency-probes-completed',dose_exit=result.returncode,report_sha256=sha(a.output/'dependency-report.yaml'),command=cmd)
except BaseException as error:r.update(status='failed',error=str(error));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
