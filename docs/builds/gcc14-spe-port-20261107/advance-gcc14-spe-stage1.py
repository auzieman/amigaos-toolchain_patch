from pathlib import Path
import re,difflib,json,subprocess,hashlib,shutil
w=Path('/srv/data1/tabor-build/linux-live-001/work/gcc14-spe-port-20261107-001');modern=w/'modern'
patch='';created=[]
def blocks(s):
 s='\n'.join(l for l in s.splitlines() if not l.startswith(';'))
 return [b.strip() for b in re.split(r'\n\s*\n',s) if b.strip()]
for opt in (modern/'gcc/config/powerpcspe').glob('*.opt'):
 names={b.splitlines()[0] for b in blocks(opt.read_text())}
 upstream=modern/'gcc/config/rs6000'/(opt.name.replace('powerpcspe','rs6000')+'.urls')
 records=[b for b in blocks(upstream.read_text()) if b.splitlines()[0] in names] if upstream.exists() else []
 text='; GCC14 option URL metadata: shared documented options only; no invented SPE documentation links.\n\n'+''.join(b+'\n\n' for b in records)
 dest=opt.with_name(opt.name+'.urls');assert not dest.exists();dest.write_text(text)
 rel=dest.relative_to(modern);created.append({'file':str(rel),'sha256':hashlib.sha256(text.encode()).hexdigest(),'shared_records':len(records)})
 patch+=''.join(difflib.unified_diff([],text.splitlines(True),fromfile='/dev/null',tofile='b/'+str(rel)))
(w/'0002-option-url-metadata.patch').write_text(patch);(w/'option-url-metadata.json').write_text(json.dumps(created,indent=2)+'\n')
# No executable source bytes change in this update; restore original reference modes.
for item in json.loads((w/'imports.json').read_text())['files']:
 shutil.copymode(w/'legacy'/item['source'],modern/item['destination'])
image='sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0'
# All previous target preparation remains in the disposable stage1 tree; keep going
# collects independent failures rather than stopping at the first diagnostic.
args=['docker','run','-d','--name','tabor-gcc14-spe-stage1-002','--cpus=4','--memory=6g','--network=none','--entrypoint','/bin/sh','-v',str(w)+':/work',image,'-c','cd /work/build-stage1 && make -k -j4 all-gcc > /work/build-stage1-002.log 2>&1']
cid=subprocess.check_output(args,text=True).strip();(w/'launch-002.json').write_text(json.dumps({'container':cid,'command':args,'update':'option metadata only; compiler target source semantics unchanged','qualification':'bootstrap diagnostics only'},indent=2)+'\n');print('Launched keep-going compiler diagnostic; URL companions:',len(created))
