import json,pathlib,subprocess,yaml
from debian.deb822 import Sources
b=pathlib.Path('/srv/data1/tabor-build/linux-live-001')
a=b/'work/port-pipeline-20261104-013-binary-rebuilds-audit'
out=b/'work/source-subset-qualification-001'
out.mkdir(exist_ok=False)
receipt=json.loads((a/'receipt.json').read_text())
full=json.loads((a/'dependency-report.json').read_text())['report']
wanted={'json-c','cyrus-sasl2','openldap','libxt','libdrm'}
expected={x['package']:x for x in full if x['package'] in wanted}
results=[]
for i,command in enumerate(receipt['commands']):
 path=pathlib.Path(command[-1])
 with path.open() as stream:
  selected=[s for s in Sources.iter_paragraphs(stream,use_apt_pkg=False) if s['Package'] in wanted]
 if not selected:continue
 subset=out/('Sources-'+str(i));subset.write_text(''.join(str(s)+'\n' for s in selected))
 cmd=[*command[:-1],str(subset)]
 with (out/(str(i)+'.yaml')).open('w') as output:
  result=subprocess.run(cmd,stdout=output,stderr=subprocess.PIPE,text=True)
 assert result.returncode in [0,1],result.stderr
 report=yaml.load((out/(str(i)+'.yaml')).read_text(),Loader=yaml.BaseLoader)['report']
 for item in report:
  e=expected[item['package']]
  assert item['status']==e['status'],(item,e)
  def packages(row):
   return sorted(json.dumps(x,sort_keys=True) for x in row.get('installationset',[]))
  assert packages(item)==packages(e),(item['package'],'changed installation set')
  results.append({'source':item['package'],'status':item['status'],'installation_set_unchanged':True})
assert {x['source'] for x in results}==wanted
(out/'receipt.json').write_text(json.dumps({'status':'scoped-dose-equivalence-passed','binary_pool':'Unchanged retained full-audit NativePackages and SpePackages','results':results},indent=2)+'\n')
print(json.dumps(results))
