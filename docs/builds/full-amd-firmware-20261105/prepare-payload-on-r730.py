import pathlib,hashlib,json,subprocess,tarfile,shutil
b=pathlib.Path('/srv/data1/tabor-build/linux-live-001');w=b/'work/full-amd-firmware-20261105-001';w.mkdir()
deb=b/'firmware-intake/firmware-amd-graphics_20250410-2_all.deb'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(deb)=='22fa89a699044d92e54c9a3b6d737da4f474245fa2001d3cbc039b74d56ac933'
subprocess.run(['dpkg-deb','-x',str(deb),str(w/'package')],check=True)
fw=w/'package/usr/lib/firmware';stage=w/'stage';(stage/'lib').mkdir(parents=True)
shutil.copytree(fw,stage/'lib/firmware',symlinks=True)
doc=w/'package/usr/share/doc/firmware-amd-graphics'
if doc.exists():shutil.copytree(doc,stage/'usr/share/doc/firmware-amd-graphics',symlinks=True)
module=b/'work/tabor-modular-20261105-003/output/drivers/gpu/drm/amd/amdgpu/amdgpu.ko'
requested=subprocess.check_output(['modinfo','-F','firmware',str(module)],text=True).splitlines()
polaris=sorted(set(n for n in requested if 'polaris10' in n or 'polaris11' in n))
missing=[n for n in polaris if not (fw/n).is_file()];assert not missing,missing
# Materialized-file manifest checks actual symlink targets as well as content.
entries=[]
for f in sorted((stage/'lib/firmware').rglob('*')):
 if f.is_symlink():assert f.resolve().is_relative_to((stage/'lib/firmware').resolve()),str(f)
 if f.is_file():entries.append({'path':f.relative_to(stage).as_posix(),'sha256':sha(f),'size':f.stat().st_size,'link':str(f.readlink()) if f.is_symlink() else None})
manifest={'package':'firmware-amd-graphics','version':'20250410-2','deb_sha256':sha(deb),'firmware_files':entries,'module_polaris_requests':polaris,'polaris_missing':missing,'all_module_firmware_names':requested}
(w/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(w/'all-sha256.txt').write_text(''.join(e['sha256']+'  /'+e['path']+'\n' for e in entries))
(w/'polaris-sha256.txt').write_text(''.join(sha(fw/n)+'  /lib/firmware/'+n+'\n' for n in polaris))
with tarfile.open(w/'firmware-payload.tar','w') as t:
 for f in sorted(stage.iterdir()):t.add(f,arcname=f.name)
r={'status':'prepared','firmware_file_count':len(entries),'payload_sha256':sha(w/'firmware-payload.tar'),'payload_bytes':(w/'firmware-payload.tar').stat().st_size,'polaris_module_requests':len(polaris),'polaris_missing':missing}
(w/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
