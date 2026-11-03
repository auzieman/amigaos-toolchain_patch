#!/usr/bin/env python3
"""Check each broad source dependency relation with Debian's cross-build solver.

This complements the whole-source coinstallability check. Individual relation
probes reveal coverage gaps; they do not prove the combined build set is ready.
"""
import argparse,hashlib,json,subprocess
from pathlib import Path
from debian.deb822 import Sources,PkgRelation
import yaml
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--seed-audit',type=Path,required=True)
p.add_argument('--dependency-audit',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.output.mkdir(exist_ok=False)
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
parent=json.loads((a.seed_audit/'receipt.json').read_text());assert parent['status']=='wide-desktop-dependency-probes-completed'
r={'status':'preparing','scope':'Individual declared relation coverage; whole-source coinstallability remains a separate gate','target_execution':False,'application_build_started':False,'parent_receipt_sha256':sha(a.seed_audit/'receipt.json')}
try:
 mapping={};source_file=a.output/'RelationSources'
 with source_file.open('w') as out:
  for name,metadata in parent['sources'].items():
   source=Sources((a.seed_audit/(name+'-source.txt')).open());assert source['Version']==metadata['version']
   for field in ['Build-Depends','Build-Depends-Arch']:
    raw=source.get(field,'');assert raw==(metadata[field.lower().replace('-','_')] or '')
    for index,relation in enumerate(PkgRelation.parse_relations(raw)):
     probe='probe-'+name+'-'+field.lower()+'-'+str(index)
     expression=PkgRelation.str([relation]);record=Sources()
     record['Package']=probe;record['Version']='1';record['Architecture']=source['Architecture'];record[field]=expression
     for conflict in ['Build-Conflicts','Build-Conflicts-Arch']:
      if source.get(conflict):record[conflict]=source[conflict]
     out.write(str(record)+'\n')
     mapping[probe]={'source':name,'source_version':source['Version'],'field':field,'relation':expression}
 native=a.dependency_audit/'NativePackages';spe=a.dependency_audit/'SpePackages'
 assert sha(native)==parent['binary_inputs']['native_sha256'] and sha(spe)==parent['binary_inputs']['spe_sha256']
 cmd=['dose-builddebcheck','--deb-native-arch=amd64','--deb-host-arch=powerpcspe','--deb-profiles=cross,nocheck','--deb-drop-b-d-indep','--deb-emulate-sbuild','--failures','--explain',str(native),str(spe),str(source_file)]
 with (a.output/'dependency-report.yaml').open('w') as out,(a.output/'dose.log').open('w') as err:
  result=subprocess.run(cmd,stdout=out,stderr=err)
 assert result.returncode in [0,1]
 report=yaml.load((a.output/'dependency-report.yaml').read_text(),Loader=yaml.BaseLoader)
 failures=[]
 for item in report.get('report',[]):
  assert item['status']=='broken';failures.append({**mapping[item['package']],'solver_explanation':item.get('reasons',[])})
 (a.output/'relation-coverage.json').write_text(json.dumps({'checked_relations':len(mapping),'blocking_relations':failures,'scope':r['scope']},indent=2)+'\n')
 r.update(status='wide-dependency-relations-checked',checked_relations=len(mapping),blocking_relations=len(failures),dose_exit=result.returncode,report_sha256=sha(a.output/'dependency-report.yaml'),coverage_sha256=sha(a.output/'relation-coverage.json'))
except BaseException as error:r.update(status='failed',error=str(error));raise
finally:(a.output/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
