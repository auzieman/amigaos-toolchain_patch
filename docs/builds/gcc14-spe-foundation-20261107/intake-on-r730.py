from pathlib import Path
import subprocess,json,hashlib,tarfile
b=Path('/srv/data1/tabor-build/linux-live-001');w=b/'work/gcc14-spe-foundation-20261107-001';w.mkdir(exist_ok=False)
lock=json.loads(Path('/home/owner/gcc14-source-lock.json').read_text());cache=b/'port-dependency-source-cache-001'
for f in lock['files']:
 p=cache/f['filename']
 with p.open('rb') as stream:h=hashlib.file_digest(stream,'sha256').hexdigest()
 assert p.stat().st_size==f['size'] and h==f['sha256'],f['filename']
old=b/'cache/gcc-8.5.0.tar.xz'
with old.open('rb') as f: oldhash=hashlib.file_digest(f,'sha512').hexdigest()
assert oldhash=='92f599680e6b7fbce88bcdda810f468777d541e5fddfbb287f7977d51093de2a5178bd0e6a08dfe37090ea10a0508a43ccd00220041abbbec33f1179bfc174d8'
with tarfile.open(old) as t:
 oldpaths=[m.name for m in t if '/config/powerpcspe/' in m.name or '/config/rs6000/e500' in m.name]
(w/'legacy-backend-files.json').write_text(json.dumps(oldpaths,indent=2)+'\n')
(w/'probe.c').write_text('#ifndef __SPE__\n#error SPE ABI is not enabled\n#endif\ndouble add(double a, double b) { return a+b; }\n')
image='sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
cmd=['docker','run','--rm','--cpus=4','--memory=6g','--network=none','--entrypoint','/bin/sh','-v',str(w)+':/work','-v',str(cache)+':/cache:ro',image,'-c','set -eu; dpkg-source --no-check -x /cache/'+lock['dsc']+' /work/debian-source > /work/extract.log 2>&1; powerpc-linux-gnu-gcc --version > /work/compiler.txt; set +e; powerpc-linux-gnu-gcc -mcpu=8548 -mabi=spe -mspe -mfloat-gprs=double -mlong-double-128 -O2 -S /work/probe.c -o /work/probe.s > /work/probe.log 2>&1; code=$?; echo "$code" > /work/probe-exit.txt; exit 0']
subprocess.run(cmd,check=True)
r={'status':'sources-qualified-modern-SPE-not-restored','gcc_debian_version':lock['version'],'source_files':lock['files'],'legacy_gcc_sha512':oldhash,'legacy_backend_files':len(oldpaths),'probe_exitcode':int((w/'probe-exit.txt').read_text()),'compiler':(w/'compiler.txt').read_text().splitlines()[0],'gpu_or_kernel_changed':False,'workstation_rebuild_started':False,'inner_archives':[str(p.relative_to(w)) for p in (w/'debian-source').glob('*.tar.*')]}
(w/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));print((w/'probe.log').read_text()[:1400])
