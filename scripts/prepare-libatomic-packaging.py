#!/usr/bin/env python3
"""Create pinned Debian source packages around the recorded SPE libatomic build.

Explicit bootstrap assembly of already cross-compiled output, not a fresh GCC
source-package build. Canonical and build-root provider payloads stay separate.
"""
import argparse,hashlib,json,os,shutil,subprocess,tarfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for n in ['project','base','output','cache']:p.add_argument('--'+n,type=Path,required=True)
a=p.parse_args();a.output.mkdir(exist_ok=False);a.cache.mkdir(exist_ok=False)
def sha(path,algorithm='sha256'):
 h=hashlib.new(algorithm)
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
record_path=a.base/'work/libatomic-001/receipt.json';record=json.loads(record_path.read_text());assert record['status']=='built-not-executed'
spec=json.loads((a.project/'profiles/toolchain-bootstrap.json').read_text())['gcc'];archive=a.base/'cache'/spec['filename']
assert sha(archive,'sha512')==spec['sha512'] and sha(archive)==record['source_sha256']
stage=record_path.parent/'stage/usr/lib';assert sha(stage/'libatomic.so.1.2.0')==record['lib_sha256']
for name in ['libatomic.so.1.2.0','libatomic.a']:
 h=subprocess.check_output(['readelf','-h',stage/name],text=True)
 assert 'ELF32' in h and 'big endian' in h and all('PowerPC' in x for x in h.splitlines() if 'Machine:' in x)
dynamic=subprocess.check_output(['readelf','-d',stage/'libatomic.so.1.2.0'],text=True)
assert '[libatomic.so.1]' in dynamic and '(RPATH)' not in dynamic and '(RUNPATH)' not in dynamic
version='8.5.0+tabor1';components={}
with tarfile.open(archive) as upstream:
 licenses={n:upstream.extractfile('gcc-8.5.0/'+n).read() for n in ['COPYING3','COPYING3.LIB','COPYING.RUNTIME']}
for mode in ['canonical','provider']:
 source='tabor-spe-libatomic-'+mode;tree=a.output/source;debian=tree/'debian';debian.mkdir(parents=True);runtime=tree/'runtime';runtime.mkdir()
 library='libatomic1' if mode=='canonical' else 'tabor-spe-libatomic1'
 shutil.copyfile(stage/'libatomic.so.1.2.0',runtime/'libatomic.so.1.2.0')
 inputs=['libatomic.so.1.2.0']
 if mode=='canonical':
  shutil.copyfile(stage/'libatomic.a',runtime/'libatomic-static.input');inputs.append('libatomic-static.input')
 (tree/'runtime-files.sha256').write_text(''.join(sha(runtime/n)+'  runtime/'+n+'\n' for n in inputs))
 control=f'''Source: {source}
Section: libs
Priority: optional
Maintainer: Tabor SPE lab <root@localhost>
Build-Depends: debhelper-compat (= 13)
Standards-Version: 4.7.0
Rules-Requires-Root: no

Package: {library}
Architecture: powerpcspe
Multi-Arch: same
'''+('Provides: libatomic1 (= ${binary:Version})\n' if mode=='provider' else '')+'''Depends: ${shlibs:Depends}, ${misc:Depends}
Description: Recorded GCC8.5 SPE atomic runtime
 Real library from the pinned GCC8.5 cross compilation; bootstrap assembly.
'''
 if mode=='canonical':control+='''
Package: tabor-spe-libatomic-dev
Architecture: powerpcspe
Multi-Arch: same
Depends: libatomic1 (= ${binary:Version}), ${misc:Depends}
Description: Recorded SPE atomic development files
 Static library and linker symlink for the real GCC8.5 atomic runtime.
'''
 (debian/'control').write_text(control)
 rules=(a.project/'packaging/gcc-runtime/debian/rules').read_text().replace('dh_makeshlibs -V',"dh_makeshlibs -p"+library+" -V'libatomic1 (>= "+version+")'")
 if mode=='canonical':rules=rules.replace('sha256sum -c runtime-files.sha256\n','sha256sum -c runtime-files.sha256\n\tcp runtime/libatomic-static.input runtime/libatomic.a\n')
 (debian/'rules').write_text(rules);(debian/'rules').chmod(0o755)
 (debian/(library+'.install')).write_text('runtime/libatomic.so.1.2.0 usr/lib/powerpc-linux-gnuspe/\n')
 (debian/(library+'.links')).write_text('usr/lib/powerpc-linux-gnuspe/libatomic.so.1.2.0 usr/lib/powerpc-linux-gnuspe/libatomic.so.1\n')
 if mode=='canonical':
  (debian/'tabor-spe-libatomic-dev.install').write_text('runtime/libatomic.a usr/lib/powerpc-linux-gnuspe/\n')
  (debian/'tabor-spe-libatomic-dev.links').write_text('usr/lib/powerpc-linux-gnuspe/libatomic.so.1 usr/lib/powerpc-linux-gnuspe/libatomic.so\nusr/lib/powerpc-linux-gnuspe/libatomic.so.1 usr/lib/tabor-spe-toolchain/powerpc-linux-gnuspe/lib/libatomic.so\nusr/lib/powerpc-linux-gnuspe/libatomic.a usr/lib/tabor-spe-toolchain/powerpc-linux-gnuspe/lib/libatomic.a\n')
 (debian/'changelog').write_text(f'{source} ({version}) UNRELEASED; urgency=medium\n\n  * Assemble recorded, provenance-checked SPE atomic runtime.\n\n -- Tabor SPE lab <root@localhost>  Tue, 03 Nov 2026 00:20:00 +0000\n')
 (debian/'source').mkdir();(debian/'source/format').write_text('3.0 (native)\n')
 docs=tree/'licenses';docs.mkdir()
 for n,data in licenses.items():(docs/n).write_bytes(data)
 (docs/'provenance.json').write_text(json.dumps({'gcc':spec,'build_receipt_sha256':sha(record_path),'build':record,'phase':'Assembly of existing recorded cross compilation; no target execution'},indent=2)+'\n')
 (debian/'copyright').write_text('GCC libatomic: Free Software Foundation copyright holders.\nGPL-3.0-or-later with GCC Runtime Library Exception3.1; upstream license files included.\nSource: '+spec['url']+'\n')
 for name in [library]+(['tabor-spe-libatomic-dev'] if mode=='canonical' else []):(debian/(name+'.docs')).write_text('licenses/*\n')
 with (a.output/(mode+'-source.log')).open('w') as log:subprocess.run(['dpkg-source','-b',tree],cwd=a.cache,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'XZ_OPT':'-T1'},check=True)
 dsc=source+'_'+version+'.dsc';files=[a.cache/dsc,a.cache/(source+'_'+version+'.tar.xz')]
 components[source]={'version':version,'dsc':dsc,'files':[{'filename':f.name,'sha256':sha(f),'size':f.stat().st_size,'url':'private-recorded-bootstrap-source:'+f.name} for f in files]}
(a.output/'sources.lock.json').write_text(json.dumps({'scope':'Private bootstrap assembly of recorded GCC8.5 SPE libatomic; preserve original compiler/source provenance and licenses','components':components},indent=2)+'\n')
(a.output/'receipt.json').write_text(json.dumps({'status':'recorded-libatomic-source-packages-prepared','target_execution':False,'raw_receipt_sha256':sha(record_path),'raw_library_sha256':record['lib_sha256'],'source_sha512':spec['sha512'],'sources_lock_sha256':sha(a.output/'sources.lock.json')},indent=2)+'\n')
