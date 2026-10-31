#!/usr/bin/env python3
"""Re-extract a locked Debian source package and reapply local patches every run."""
import argparse, hashlib, json, os, re, subprocess, sys, shutil, signal
from pathlib import Path

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--project',type=Path,default=Path('/project'))
 p.add_argument('--cache',type=Path,default=Path('/cache'))
 p.add_argument('--work',type=Path,required=True)
 p.add_argument('--component',choices=['linux','glibc'],required=True)
 p.add_argument('--mode',choices=['prepare','configure','build'],default='prepare')
 p.add_argument('--image-id',required=True)
 p.add_argument('--jobs',type=int,default=2)
 p.add_argument('--kernel-profile',choices=['tabor','qemu-smoke','qemu-live','tabor-live'],default='tabor')
 a=p.parse_args();project=a.project.resolve();cache=a.cache.resolve();work=a.work.resolve()
 if not re.search(r'(?:^|@)sha256:[0-9a-f]{64}$',a.image_id):p.error('image digest required')
 if not 1<=a.jobs<=32:p.error('invalid job count')
 if any(work.is_relative_to(x) or x.is_relative_to(work) for x in [cache,project]):p.error('independent work directory required')
 lock=json.loads((project/'profiles/debian-trixie.lock.json').read_text());component=lock['components'][a.component]
 series=project/'patches'/a.component/'series'
 patches=[]
 for line in series.read_text().splitlines():
  name=line.split('#',1)[0].strip()
  if name:
   patch=(series.parent/name).resolve()
   if not patch.is_relative_to(series.parent.resolve()):p.error('patch outside series')
   patches.append(patch)
 # Refuse reuse; never reset a reference source or silently resume an iteration.
 work.mkdir(parents=True,exist_ok=False)
 receipt={'component':a.component,'version':component['version'],'image_id':a.image_id,'status':'started','mode':a.mode,'lock_sha256':sha(project/'profiles/debian-trixie.lock.json'),'series_sha256':sha(series),'patches':{x.name:sha(x) for x in patches},'commands':[],'kernel_profile':a.kernel_profile,'boot_tested':False,'spe_userspace_validated':False}
 def interrupted(signum,frame):raise RuntimeError('Iteration interrupted by signal '+str(signum))
 signal.signal(signal.SIGTERM,interrupted)
 with (work/'build.log').open('w') as log:
  def run(cmd,cwd=None,allow_failure=False):
   receipt['commands'].append(cmd);log.write('$ '+repr(cmd)+'\n');log.flush()
   env={**os.environ,'KBUILD_BUILD_USER':'tabor','KBUILD_BUILD_HOST':'lab','KBUILD_BUILD_TIMESTAMP':'1970-01-01 00:00:00 UTC','KBUILD_BUILD_VERSION':'1'}
   proc=subprocess.Popen(cmd,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)
   while True:
    try:rc=proc.wait(timeout=5);break
    except subprocess.TimeoutExpired:
     if shutil.disk_usage(work).free < 1024**3:
      os.killpg(proc.pid,signal.SIGTERM)
      try:proc.wait(timeout=10)
      except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
      raise RuntimeError('Local workspace free-space guard stopped this command below 1 GiB')
   if rc and not allow_failure:raise RuntimeError('Command failed ('+str(rc)+'): '+repr(cmd))
   return rc
  try:
   for f in component['files']:
    path=cache/f['filename']
    if path.stat().st_size!=f['size'] or sha(path)!=f['sha256']:raise ValueError('Cached source mismatch: '+f['filename'])
   if a.component=='linux' and a.mode!='prepare' and shutil.disk_usage(work).free < 4*1024**3:
    raise RuntimeError('Kernel build needs at least 4 GiB free local workspace before extraction')
   source=work/'source'
   # HTTPS DSC + payload hashes are pinned; independent archive signature verification remains explicit in lock.
   run(['dpkg-source','--no-check','-x',str(cache/component['dsc']),str(source)])
   for patch in patches:
    run(['git','apply','--check',str(patch)],source)
    run(['git','apply',str(patch)],source)
   receipt['status']='prepared'
   if a.mode!='prepare':
    output=work/'output';output.mkdir()
    run(['dpkg-query','-W']);run(['powerpc-linux-gnu-gcc','--version']);run(['powerpc-linux-gnu-ld','--version'])
    if a.component=='linux':
     make=['make','-C',str(source),'O='+str(output),'ARCH=powerpc','CROSS_COMPILE=powerpc-linux-gnu-']
     if a.kernel_profile in ['qemu-smoke','qemu-live']:
      seed=project/'profiles/qemu'/('e500v2-live.config' if a.kernel_profile=='qemu-live' else 'e500v2-smoke.config')
      receipt['config_seed_sha256']=sha(seed)
      run(make+['KCONFIG_ALLCONFIG='+str(seed),'allnoconfig'])
     else:run(make+['mpc85xx_smp_defconfig'])
     run([str(source/'scripts/config'),'--file',str(output/'.config'),'--enable','TABOR','--enable','SPE','--enable','DEVTMPFS','--enable','DEVTMPFS_MOUNT','--enable','DEBUG_INFO_NONE','--disable','DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT','--disable','DEBUG_INFO','--disable','DEBUG_INFO_BTF'])
     if a.kernel_profile=='tabor-live':
      fragment=project/'profiles/images/tabor-live-kernel.config'
      receipt['live_fragment_sha256']=sha(fragment)
      for line in fragment.read_text().splitlines():
       if not line or line.startswith('#'):continue
       match=re.fullmatch(r'CONFIG_([A-Z0-9_]+)=([yn])',line)
       if not match:raise ValueError('Unsupported live fragment setting: '+line)
       run([str(source/'scripts/config'),'--file',str(output/'.config'),
            '--enable' if match.group(2)=='y' else '--disable',match.group(1)])
     run(make+['olddefconfig'])
     config=(output/'.config').read_text().splitlines()
     for key in ['CONFIG_PPC=y','CONFIG_BOOKE=y','CONFIG_SPE=y','CONFIG_TABOR=y','CONFIG_DEBUG_INFO_NONE=y']:
      if key not in config:raise ValueError('Required configuration missing: '+key)
     if a.kernel_profile in ['qemu-smoke','qemu-live']:
      for key in ['CONFIG_PPC_QEMU_E500=y','CONFIG_SMP=y','CONFIG_BLK_DEV_INITRD=y','CONFIG_BINFMT_ELF=y','CONFIG_SERIAL_8250_CONSOLE=y']:
       if key not in config:raise ValueError('Required QEMU configuration missing: '+key)
     if a.kernel_profile in ['tabor-live','qemu-live']:
      required=['CONFIG_FUTEX=y','CONFIG_COMPAT_32BIT_TIME=y','CONFIG_MULTIUSER=y','CONFIG_UNIX98_PTYS=y','CONFIG_SECCOMP=y','CONFIG_SECCOMP_FILTER=y','CONFIG_BINFMT_SCRIPT=y','CONFIG_INET=y','CONFIG_TMPFS=y','CONFIG_EXT4_FS=y']
      if a.kernel_profile=='qemu-live':
       required+=['CONFIG_HIGHMEM=y','CONFIG_SYSVIPC=y','CONFIG_INOTIFY_USER=y','CONFIG_NET_CORE=y','CONFIG_VIRTIO_NET=y','CONFIG_VIRTIO_PCI_LEGACY=y','CONFIG_HW_RANDOM_VIRTIO=y']
      if a.kernel_profile=='tabor-live':
       required+=['CONFIG_SMP=y','CONFIG_MMU=y','CONFIG_HIGHMEM=y','CONFIG_PHYS_64BIT=y','CONFIG_PTE_64BIT=y','CONFIG_SYSVIPC=y','CONFIG_INOTIFY_USER=y','CONFIG_DRM=y','CONFIG_DRM_AMDGPU=y','CONFIG_USB_HID=y','CONFIG_USB_STORAGE=y','CONFIG_VT_CONSOLE=y','CONFIG_FRAMEBUFFER_CONSOLE=y']
      for key in required:
       if key not in config:raise ValueError('Required live configuration missing: '+key)
     if a.kernel_profile in ['tabor-live','qemu-live']:
      nr=next((int(x.split('=')[1]) for x in config if x.startswith('CONFIG_NR_CPUS=')),0)
      if nr<2:raise ValueError('Live image must support at least two CPU cores')
     receipt['config_sha256']=sha(output/'.config');receipt['status']='configured'
     if a.mode=='build':
      # Catch board/DTS defects before spending time on the whole kernel.
      run(make+['-j'+str(a.jobs),'arch/powerpc/platforms/85xx/tabor.o','fsl/tabor-a1222.dtb'])
      targets=['vmlinux'] if a.kernel_profile in ['qemu-smoke','qemu-live'] else ['vmlinux','modules','dtbs']
      run(make+['-j'+str(a.jobs)]+targets)
      receipt['status']='compiled'
    else:
     # Do not build a generic PowerPC libc and mislabel it as SPE.
     probe=work/'spe-probe.c';probe.write_text('double add(double a,double b){return a+b;}\n')
     run(['powerpc-linux-gnu-gcc','-mcpu=8548','-mabi=spe','-mspe','-mfloat-gprs=double','-c',str(probe),'-o',str(work/'spe-probe.o')])
     run([str(source/'configure'),'--build=x86_64-linux-gnu','--host=powerpc-linux-gnuspe','--prefix=/usr','--disable-werror','CC=powerpc-linux-gnu-gcc -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double'],output)
     receipt['status']='configured'
     if a.mode=='build':run(['make','-j'+str(a.jobs)],output);receipt['status']='compiled'
    names=['vmlinux','System.map','.config','arch/powerpc/boot/dts/fsl/tabor-a1222.dtb']
    receipt['artifacts']={n:sha(output/n) for n in names if (output/n).is_file()}
   receipt['cache_reverified']=all(sha(cache/f['filename'])==f['sha256'] for f in component['files'])
  except Exception as exc:
   receipt['status']='failed';receipt['error']=str(exc);raise
  finally:(work/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(receipt['status'],work/'receipt.json')

if __name__=='__main__':
 try:main()
 except Exception as exc:print(str(exc),file=sys.stderr);sys.exit(1)
