#!/usr/bin/env python3
"""Retain replayable iteration evidence, then discard only its generated trees."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,tarfile
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--results',type=Path,required=True);a=p.parse_args()
run=a.run.resolve();results=a.results.resolve()
if not re.fullmatch(r'(linux|glibc)-[0-9]{3}',run.name) or run.parent.name!='work':raise SystemExit('Expected component workspace under work/')
if results.is_relative_to(run) or run.is_relative_to(results):raise SystemExit('Separate retention directory required')
for name in ['source','output']:
 if (run/name).is_symlink():raise SystemExit('Refusing symlink cleanup')
receipt=json.loads((run/'receipt.json').read_text());component=receipt['component']
if not run.name.startswith(component+'-') or receipt['status'] not in ['failed','compiled','prepared','configured']:raise SystemExit('Unexpected iteration receipt')
results.mkdir(parents=True,exist_ok=True);retained={}
def keep(src,name):
 target=results/name;shutil.copy2(src,target)
 h=hashlib.sha256(src.read_bytes()).hexdigest()
 if hashlib.sha256(target.read_bytes()).hexdigest()!=h:raise SystemExit('Retained copy mismatch')
 retained[name]=h
for name in ['build.log','receipt.json']:
 if (run/name).is_file():keep(run/name,component+'-'+name)
output=run/'output'
for path,name in [('vmlinux','vmlinux'),('System.map','System.map'),('.config','kernel.config'),('arch/powerpc/platforms/85xx/tabor.o','tabor.o'),('arch/powerpc/boot/dts/fsl/tabor-a1222.dtb','tabor-a1222.dtb'),('config.log','glibc-config.log')]:
 if (output/path).is_file():keep(output/path,name)
modules=list(output.rglob('*.ko')) if output.exists() else []
if modules:
 archive=results/'kernel-modules.tgz'
 with tarfile.open(archive,'w:gz',compresslevel=1) as t:
  for f in modules:t.add(f,arcname=str(f.relative_to(output)))
 retained[archive.name]=hashlib.sha256(archive.read_bytes()).hexdigest()
# Only deterministic source/output directories created within this fresh run.
for name in ['source','output']:
 target=run/name
 if target.is_symlink():raise SystemExit('Refusing symlink cleanup')
 if target.exists():shutil.rmtree(target)
(results/(component+'-retention.json')).write_text(json.dumps({'component':component,'status':receipt['status'],'retained_sha256':retained,'module_count':len(modules),'generated_source_and_output_discarded':True},indent=2)+'\n')
print('Retained evidence and discarded generated trees:',run)
