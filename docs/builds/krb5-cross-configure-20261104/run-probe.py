from pathlib import Path
import subprocess,json,hashlib,os
b=Path('/srv/data1/tabor-build/linux-live-001');o=b/'work/constructor-destructor-proof-002';o.mkdir();root=o/'sysroot';root.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
for folder,name in [('debian-glibc-402','libc6'),('debian-glibc-402','libc6-dev')]:
 parent=b/'work'/folder;r=json.loads((parent/'receipt.json').read_text());f=next(parent.glob(name+'_*_powerpcspe.deb'));assert sha(f)==r['packages'][f.name]['sha256'];subprocess.run(['dpkg-deb','-x',str(f),str(root)],check=True);records.append({'file':f.name,'sha256':sha(f)})
(root/'lib').symlink_to('usr/lib') # Standard merged-/usr layout for this extracted probe sysroot.
sdk=b/'work/sdk-fixed-headers-001/root/usr/lib/tabor-spe-toolchain';gcc=sdk/'bin/powerpc-linux-gnuspe-gcc';src=Path('/tmp/constructor-destructor-check.c');binary=o/'check'
cmd=[str(gcc),'--sysroot='+str(root),str(src),'-o',str(binary)]
r=subprocess.run(cmd,capture_output=True,text=True);(o/'build.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
for name in ['constructor.pending','destructor.pending']:(o/name).touch()
r=subprocess.run(['qemu-ppc','-cpu','e500v2','-L',str(root),str(binary)],cwd=o,capture_output=True,text=True,timeout=30);assert r.returncode==0,(r.returncode,r.stderr);assert not (o/'constructor.pending').exists() and not (o/'destructor.pending').exists()
proof={'status':'measured-in-SPE-QEMU','target_architecture':'powerpcspe','cpu':'e500v2','compiler':str(gcc),'compiler_sha256':sha(gcc),'source_sha256':sha(src),'binary_sha256':sha(binary),'inputs':records,'sysroot_layout':'lib -> usr/lib; isolated extracted probe root only','compile_command':cmd,'run_command':['qemu-ppc','-cpu','e500v2','-L',str(root),str(binary)],'exit':r.returncode,'krb5_cv_attr_constructor_destructor':'yes,yes','scope':'dynamic executable constructor/destructor semantics with accepted glibc; not full Kerberos, shared-library unload, or physical hardware validation'}
(o/'receipt.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
