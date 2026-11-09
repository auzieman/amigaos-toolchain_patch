from pathlib import Path
import hashlib,json,subprocess
base=Path('/srv/data1/tabor-build/linux-live-001')
old=base/'work/gcc14-spe-port-20261107-001'
w=base/'work/gcc14-sdk-20261108-001'
assert (old/'glibc-gcc14-002/result.exit').read_text().strip()=='0'
q=json.loads((old/'qualification-005/result.json').read_text())
assert 'PASS' in str(q) or 'pass' in str(q), q
w.mkdir(exist_ok=False)
subprocess.run(['cp','-a','--reflink=auto',str(old/'glibc-gcc14-002'),str(w/'glibc-build')],check=True)
image='sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
recipe=Path('/home/owner/gcc14-sdk-20261108/build.sh')
cmd=['docker','run','-d','--name','tabor-gcc14-sdk-20261108-001','--cpus=4','--memory=6g','--pids-limit=512','--network=none','--entrypoint','/bin/sh']
for host,guest,mode in [(w,'/fresh','rw'),(w/'glibc-build','/work/glibc-gcc14-002','rw'),(old/'build-stage1','/work/build-stage1','ro'),(old/'modern','/work/modern','ro'),(base/'work/debian-glibc-402/source','/source','ro'),(base/'sysroot','/sysroot','ro'),(recipe,'/recipe.sh','ro')]:
 cmd+=['-v',f'{host}:{guest}:{mode}']
cmd += [image,'/recipe.sh']
record={'command':cmd,'recipe_sha256':hashlib.sha256(recipe.read_bytes()).hexdigest(),'compiler_sha256':hashlib.sha256((old/'build-stage1/gcc/cc1').read_bytes()).hexdigest(),'status':'launching','purpose':'GCC14 full C/C++ threaded shared runtime SDK qualification; not yet Debian consumer builds','accepted_sdk_replaced':False}
(w/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
p=subprocess.run(cmd,capture_output=True,text=True);record.update(container_id=p.stdout.strip(),returncode=p.returncode,stderr=p.stderr,status='launched' if p.returncode==0 else 'launch-failed')
(w/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2));p.check_returncode()
