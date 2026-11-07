from pathlib import Path
import subprocess,hashlib,json,shutil,os,datetime
os.sched_setaffinity(0, sorted(os.sched_getaffinity(0))[:4])
b=Path('/srv/data1/tabor-build/linux-live-001');w=b/'work/amdgpu-upstream-clean-20261107-003';w.mkdir(exist_ok=False)
repo=b/'upstream-amdgpu-20261107/amd-development';commit='5349075eac146ae0511d8929fc24451e4d9a4b7e'
src=w/'source';out=w/'output';out.mkdir()
r={'source_url':'https://gitlab.freedesktop.org/drm/amdgpu/kernel.git','source_commit':commit,'branch_at_intake':'drm-amdgpu-next','status':'preparing','experimental_gpu_patches':[],'board_patches':[],'hardware_tested':False}
def save(): (w/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
def run(cmd):
 with (w/'prepare.log').open('a') as log: subprocess.run(list(map(str,cmd)),check=True,stdout=log,stderr=subprocess.STDOUT,timeout=600)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
save()
try:
 run(['git','-C',repo,'worktree','add','--no-checkout','--detach',src,commit])
 run(['git','-C',src,'sparse-checkout','disable'])
 run(['git','-C',src,'checkout','--detach',commit])
 for name in ['0001-powerpc-tabor-initial-machine-dts.patch','0002-powerpc-tabor-match-vendor-compatible.patch']:
  p=Path('/home/owner/upstream-'+name)
  run(['git','-C',src,'apply','--check',p]);run(['git','-C',src,'apply',p]);r['board_patches'].append({'file':name,'sha256':sha(p)});save()
 config=b/'work/gfx-map-stage-20261107-001/output/.config';shutil.copy2(config,out/'.config');r['input_config_sha256']=sha(config)
 # No GPU files may differ from the pinned development source.
 changed=subprocess.check_output(['git','-C',str(src),'diff','--name-only'],text=True).splitlines()
 assert not any(p.startswith('drivers/gpu/') for p in changed)
 image='sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
 cmd=['docker','run','-d','--name','tabor-amdgpu-upstream-clean-003','--cpus=4','--memory=6g','--network=none','--entrypoint','/bin/sh','-v',str(w)+':/work',image,'-c', 'set -eu; cd /work/source; scripts/config --file /work/output/.config --set-str LOCALVERSION -tabor-upstream-001; make O=/work/output ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu- olddefconfig > /work/configure.log 2>&1; sha256sum /work/output/.config > /work/config.sha256; powerpc-linux-gnu-gcc --version > /work/compiler.txt; make O=/work/output ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu- -j4 vmlinux modules dtbs > /work/build.log 2>&1']
 cid=subprocess.check_output(cmd,text=True).strip();r.update(status='building',container=cid,image=image,changed_tracked_paths=changed);save();print(json.dumps(r),flush=True)
except Exception as e:
 r.update(status='preparation-failed',error=str(e));save();raise
