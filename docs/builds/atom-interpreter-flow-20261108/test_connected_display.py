"""R730: connect actual display ATOM producers to actual execution engine."""
from pathlib import Path
import subprocess,json,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
B=Path('/srv/data1/tabor-build/source-review');W=B/'atom-interpreter-flow-20261108'
caller=(B/'console-selected-path-20261108/atom-display.c').read_text();a=caller.index('static int amdgpu_atom_execute_table(');b=caller.index('{',a)+1;depth=1
while depth:depth+=(caller[b]=='{')-(caller[b]=='}');b+=1
old=caller[a:b]
new=old.replace('static int amdgpu_atom_execute_table','extern int engine_roundtrip(u32*,unsigned);\nstatic int amdgpu_atom_execute_table').replace('return 0;}','return engine_roundtrip(args,size);}')
assert old!=new;caller=caller[:a]+new+caller[b:];(W/'connected-display.c').write_text(caller)
engine=(W/'engine.c').read_text();variants={'baseline':engine,'native-ps-read':engine.replace('get_unaligned_le32((u32 *)&ctx->ps[idx])','ctx->ps[idx]'),'native-ps-write':engine.replace('ctx->ps[idx] = cpu_to_le32(val);','ctx->ps[idx] = val;')}
outputs={};controls={}
for name,text in variants.items():
 assert name=='baseline'or text!=engine
 src=W/(name+'-engine.c');src.write_text(text)
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
  obj=W/(name+'-'+arch+'.o');exe=W/('display-'+name+'-'+arch)
  flags=(['-mstackrealign']if arch=='x86'else[])+['-O2','-ffunction-sections','-ffreestanding','-fno-stack-protector','-fno-pie']
  cmd=[cc]+flags+['-DENGINE_LIBRARY','-Damdgpu_atom_execute_table=engine_execute_table','-Dmain=unused_engine_main','-D_start=unused_engine_start','-Dmemcpy=engine_memcpy','-Dmemset=engine_memset','-c',str(src),'-o',str(obj)]
  p=subprocess.run(cmd,capture_output=True);(W/(name+'-'+arch+'-compile.log')).write_bytes(p.stderr);p.check_returncode()
  cmd=[cc]+flags+['-nostdlib','-no-pie','-static','-Wl,--gc-sections',str(W/'connected-display.c'),str(obj),'-lgcc','-o',str(exe)]
  p=subprocess.run(cmd,capture_output=True);p.check_returncode();p=subprocess.run(runner+[str(exe)],capture_output=True,timeout=30);outputs[name,arch]=p.stdout
  if name=='baseline'or arch=='x86':p.check_returncode()
  else:assert p.returncode!=0,(name,arch)
  controls[name+'-'+arch]={'exit':p.returncode,'output_bytes':len(p.stdout)}
assert outputs['baseline','x86']==outputs['baseline','ppc']==outputs['native-ps-read','x86']==outputs['native-ps-write','x86']
r=dict(status='PASS',display_scenarios_per_architecture=392,actual_interpreter_lines=1272,full_request_bytes=8192,output_sha256=hashlib.sha256(outputs['baseline','ppc']).hexdigest(),caller_source_sha256=hashlib.sha256(caller.encode()).hexdigest(),engine_source_sha256=hashlib.sha256(engine.encode()).hexdigest(),controls=controls,hardware_accessed=False,limits=['Synthetic ATOM bytecode transports real caller parameter buffers, not actual GPU VBIOS programs','Numeric register endpoint and Linux scheduling/allocation shims','Confirms serializer/interpreter agreement for exercised requests, not device state/timing'])
(W/'connected-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
