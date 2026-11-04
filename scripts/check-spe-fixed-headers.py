#!/usr/bin/env python3
"""Reproduce fixed-header failures and compile corrected header combinations.

Read-only native Debian template, extracted real target headers, no target
execution or modified installation database. Heavy work stays on R730.
"""
import argparse, hashlib, importlib.util, json, shutil, subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
for key in ['root','sdk','packages','output']:
    p.add_argument('--'+key,type=Path,required=True)
a=p.parse_args();a.output.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'status':'running','target_execution':False,'items':[],'inputs':{}}
try:
    for pattern in ['libc6-dev_*.deb','linux-libc-dev_*.deb']:
        packages=list(a.packages.glob(pattern));assert len(packages)==1,packages
        package=packages[0];r['inputs'][package.name]=sha(package)
        subprocess.run(['dpkg-deb','-x',str(package),str(a.output/'sysroot')],check=True)
    shutil.copytree(a.sdk,a.output/'sdk',symlinks=True)
    fixed=a.output/'sdk/lib/gcc/powerpc-linux-gnuspe/8.5.0/include-fixed'
    fixtures={'mount':'#include <sys/mount.h>\n#include <linux/mount.h>\n',
              'rseq':'#include <sys/rseq.h>\n#include <linux/rseq.h>\n',
              'sched':'#include <sched.h>\n#include <linux/sched/types.h>\n',
              'statx':'#include <sys/stat.h>\n#include <linux/stat.h>\n',
              'close-range':'#include <unistd.h>\n#include <linux/close_range.h>\n'}
    for label,body in fixtures.items():(a.output/(label+'.c')).write_text('#define _GNU_SOURCE\n'+body+'int probe(void){return 0;}\n')
    for phase in ['original','corrected']:
        if phase=='corrected':
            spec=importlib.util.spec_from_file_location('repair',Path(__file__).with_name('repair-spe-fixed-headers.py'))
            mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
            r['repairs']=mod.repair(fixed)
        for label in fixtures:
            command=['systemd-nspawn','--quiet','--register=no','--timezone=off','--read-only',
                     '--directory='+str(a.root),'--bind='+str(a.output)+':/mnt',
                     '/mnt/sdk/bin/powerpc-linux-gnuspe-gcc','--sysroot=/mnt/sysroot',
                     '-H','-fsyntax-only','/mnt/'+label+'.c','-o','/mnt/'+phase+'-'+label+'.o']
            result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            log=a.output/(phase+'-'+label+'.log');log.write_text(result.stdout)
            r['items'].append({'phase':phase,'test':label,'exit':result.returncode,'log_sha256':sha(log)})
            if phase=='original' and label=='mount':assert result.returncode!=0 and 'redeclaration' in result.stdout,result.stdout
            if phase=='corrected':assert result.returncode==0,result.stdout
    r['status']='fixed-header-regression-passed-not-target-executed'
except Exception as error:
    r.update(status='failed',error=str(error));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
