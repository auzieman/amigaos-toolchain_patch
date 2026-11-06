import pathlib,subprocess,shutil,json
b=pathlib.Path('/srv/data1/tabor-build/linux-live-001');name='smu-diag-le-20261105-001';project=b/(name+'-project');work=b/'work'/name
image='sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
shutil.copytree(b/'smu-diagnostics-project-20261105-003',project,symlinks=True)
shutil.copy2('/home/owner/smu7-endian-candidate.patch',project/'patches/linux/0004-smu7-endian-experiment.patch')
with (project/'patches/linux/series').open('a') as f:f.write('0004-smu7-endian-experiment.patch\n')
# Qualify a fresh source/config with exact ordered patches first.
subprocess.run(['docker','run','--rm','--cpus=4','--memory=6g','--network=none','--entrypoint','/usr/bin/python3','-v',str(b)+':/base',image,str(project).replace(str(b),'/base')+'/scripts/debian-iterate.py','--project',str(project).replace(str(b),'/base'),'--cache','/base/tabor-source-cache','--work',str(work).replace(str(b),'/base'),'--component','linux','--mode','configure','--kernel-profile','tabor-modular','--kernel-config','/base/work/tabor-modular-20261105-003/output/.config','--jobs','4','--image-id',image],check=True)
reference=b/'work/tabor-smu-diagnostics-20261105-003/output'
shutil.copytree(reference,work/'output',symlinks=True,dirs_exist_ok=True,ignore=lambda d,n:{'source'} if pathlib.Path(d)==reference else set())
# Stable in-container Kbuild paths reuse accepted objects without altering references.
canonical='/base/work/tabor-smu-diagnostics-20261105-003'
link=work/'output/source'
if link.is_symlink():link.unlink()
link.symlink_to(canonical+'/source')
command=['docker','run','-d','--name','tabor-smu-diag-le-build-001','--cpus=4','--memory=6g','--network=none','--entrypoint','/bin/sh','-v',str(b)+':/base','-v',str(work/'source')+':'+canonical+'/source','-v',str(work/'output')+':'+canonical+'/output',image,'-c','make -C '+canonical+'/source O='+canonical+'/output ARCH=powerpc CROSS_COMPILE=powerpc-linux-gnu- -j4 modules > /base/work/'+name+'/modules.log 2>&1']
cid=subprocess.check_output(command,text=True).strip()
(work/'launch.json').write_text(json.dumps({'container':cid,'command':command,'reference_outputs_preserved':True,'status':'launched'},indent=2)+'\n');print(cid)
