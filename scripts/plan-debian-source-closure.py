#!/usr/bin/env python3
"""Map actual unmet target library dependencies to authenticated apt source metadata.

Run in a native metadata container with Debian binary/source indexes. This
produces an intake plan, not proof of target build readiness or a build order.
Native tools are listed separately; only library/development candidates are
mapped to target sources. Every later build still uses dpkg-checkbuilddeps.
"""
import argparse,hashlib,json,re,subprocess
from pathlib import Path
from debian.deb822 import Deb822
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--queue-receipt',type=Path,required=True)
p.add_argument('--profile',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.output.mkdir(exist_ok=False)
r=json.loads(a.queue_receipt.read_text());profile=json.loads(a.profile.read_text())
latest=r.get('latest_items') or list({x['package']:x for x in r['items']}.values())
requirements={};native=[];unmapped=[];sources={}
for item in latest:
 for line in item.get('preflight',{}).get('unmet_dependencies',[]):
  expression=line.partition('unmet build dependencies:')[2].strip()
  # dpkg-checkbuilddeps diagnostics separate relations with spaces rather
  # than control-file commas. Consume version parentheses as one token.
  pattern=r'([a-z0-9][a-z0-9+.-]*)(?::([a-z0-9-]+))?(?:\s*\([^)]*\))?'
  for match in re.finditer(pattern,expression):
    name,role=match[1],match[2]
    if role=='native' or not (name.startswith('lib') or name.endswith('-dev')):
     native.append({'package':name,'role':role,'consumer':item['package']});continue
    requirements.setdefault(name,[]).append(item['package'])
def fields(name):
 data=subprocess.run(['apt-cache','show',name],capture_output=True,text=True)
 records=list(Deb822.iter_paragraphs(data.stdout.splitlines(keepends=True)))
 return records
for name,consumers in sorted(requirements.items()):
 records=fields(name)
 provider=name
 if not records:
  raw=subprocess.check_output(['apt-cache','showpkg',name],text=True)
  providers=list(dict.fromkeys(x.split()[0] for x in raw.partition('Reverse Provides:')[2].splitlines() if x.strip()))
  if len(providers)==1:provider=providers[0];records=fields(provider)
 if not records:
  unmapped.append({'package':name,'consumers':consumers});continue
 binary=records[0];source=binary.get('Source',provider)
 match=re.fullmatch(r'([^ ]+)(?: \(([^)]+)\))?',source);assert match,source
 source=match[1];version=match[2] or binary['Version']
 raw=subprocess.check_output(['apt-cache','showsrc','--only-source',source],text=True)
 entries=[x for x in Deb822.iter_paragraphs(raw.splitlines(keepends=True)) if x['Package']==source and x['Version']==version]
 if not entries:
  unmapped.append({'package':name,'source':source,'version':version,'consumers':consumers});continue
 if source not in sources:sources[source]={'version':version,'reason':'Actual unmet target development/library dependency','binary_requirements':{},'already_in_recipe_scope':source in profile['packages']}
 assert sources[source]['version']==version,(source,version)
 sources[source]['binary_requirements'][name]={'provider':provider,'consumers':sorted(set(consumers))}
plan={'scope':'Candidate source closure derived from actual Debian preflight; source license/hash intake required before build','components':{name:{'version':x['version'],'reason':x['reason']+': '+', '.join(x['binary_requirements'])} for name,x in sources.items() if not x['already_in_recipe_scope']}}
(a.output/'source-intake-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
(a.output/'receipt.json').write_text(json.dumps({'status':'source-closure-intake-planned-not-built','input_sha256':hashlib.sha256(a.queue_receipt.read_bytes()).hexdigest(),'sources':sources,'native_or_role_review':native,'unmapped':unmapped,'target_execution':False},indent=2)+'\n')
print(json.dumps({'new_source_candidates':len(plan['components']),'known_sources':len(sources)-len(plan['components']),'unmapped':len(unmapped)}))
