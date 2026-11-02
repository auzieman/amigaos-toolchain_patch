#!/usr/bin/env python3
"""Build only the Debian powerpcspe UAPI header package, using Debian's libc-dev rules."""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','cache','output']:p.add_argument('--'+n,type=Path,required=True)
p.add_argument('--image-id',required=True)
p.add_argument('--debian-all-uapi',action='store_true',help='Preserve the normal Debian universal data package and add the SPE include tuple; no target code compilation')
a=p.parse_args();a.output.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((a.project/'profiles/debian-trixie.lock.json').read_text())['components']['linux']
r={'status':'started','architecture':'all' if a.debian_all_uapi else 'powerpcspe','kernel_architectures':['powerpc'],'data_export_only':True,'image_id':a.image_id,'recipe_sha256':sha(Path(__file__)),'source_lock_sha256':sha(a.project/'profiles/debian-trixie.lock.json'),'commands':[],'packages':{},'target_installation':False}
env={**os.environ,'DEB_HOST_ARCH':'powerpcspe','DEB_HOST_GNU_TYPE':'powerpc-linux-gnuspe','DEB_BUILD_OPTIONS':'nocheck parallel=4','LC_ALL':'C.UTF-8'}
log=(a.output/'build.log').open('w')
def run(cmd,cwd):
 cmd=list(map(str,cmd));r['commands'].append(cmd);log.write(repr(cmd)+'\n');log.flush();subprocess.run(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
try:
 for f in c['files']:
  q=a.cache/f['filename'];assert sha(q)==f['sha256']
 src=a.output/'source';run(['dpkg-source','--no-check','-x',a.cache/c['dsc'],src],a.output)
 patch=a.project/('patches/linux/headers/0002-register-spe-uapi-tuple.patch' if a.debian_all_uapi else 'patches/linux/headers/0001-package-spe-only-uapi-headers.patch');r['patch_sha256']=sha(patch)
 run(['git','apply','--check',patch],src);run(['git','apply',patch],src)
 ch=src/'debian/changelog';version=c['version'] if a.debian_all_uapi else c['version']+'+tabor1'
 if not a.debian_all_uapi:
  ch.write_text(f'linux ({version}) tabor-trixie; urgency=medium\n\n  * Package powerpcspe-only UAPI headers with the gnuspe include tuple.\n\n -- Tabor lab <root@localhost>  Sun, 01 Nov 2026 16:00:00 +0000\n\n'+ch.read_text())
 arches='powerpc';tuples='powerpc-linux-gnuspe:powerpc'
 if a.debian_all_uapi:
  generated=(src/'debian/rules.gen').read_text()
  arches=re.search(r"ALL_LIBCDEV_KERNELARCHES='([^']+)'",generated)[1]
  tuples=re.search(r"ALL_LIBCDEV_MULTIARCHES='([^']+)'",generated)[1]
  r['kernel_architectures']=arches.split()
 # This Debian target needs only header-export/build/packaging tools, not the
 # unrelated full kernel/perf/tools Build-Depends of the entire Linux source.
 run(['env','-u','DEB_HOST_ARCH','-u','DEB_HOST_GNU_TYPE','dpkg-checkbuilddeps','-d','debhelper-compat (= 13), rsync, make, gcc, libc6-dev, bison, flex'],src)
 run(['make','-f','debian/rules.real','binary_libc-dev','ALL_LIBCDEV_KERNELARCHES='+arches,'ALL_LIBCDEV_MULTIARCHES='+tuples,'PACKAGE_NAME=linux-libc-dev','DESTDIR='+str(src/'debian/linux-libc-dev'),'DH_OPTIONS=-plinux-libc-dev','SOURCEVERSION='+version,'SOURCE_BASENAME=linux','UPSTREAMVERSION=6.12','VERSION=6.12','BUILDDEB_ARGS=-Zgzip'],src)
 for deb in a.output.glob('*.deb'):
  assert subprocess.check_output(['dpkg-deb','-f',str(deb),'Architecture'],text=True).strip()==r['architecture']
  r['packages'][deb.name]={'sha256':sha(deb),'bytes':deb.stat().st_size,'architecture':r['architecture']}
 assert r['packages'];r['status']='debian-packages-built-not-target-installed'
except Exception as e:r.update(status='failed',error=str(e));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print(r['status'])
