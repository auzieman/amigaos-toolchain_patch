from pathlib import Path
import hashlib,json,os,resource,subprocess
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
w=Path('/home/owner/ib-fetch-contract-20261108');previous=Path('/home/owner/gfx-ib-flow-20261108')
s=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-008/source');d=s/'drivers/gpu/drm/amd/amdgpu'
def function(t,sig):
 a=t.index(sig);i=t.index('{',a)+1;n=1
 while n:n+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
ring=(d/'amdgpu_ring.h').read_text();fence=(d/'amdgpu_fence.c').read_text();results=[]
for policy in ['old','new']:
 gfx=(d/'gfx_v8_0.c').read_text() if policy=='old' else (w/'gfx_v8_0.c').read_text()
 header=ring if policy=='old' else (w/'amdgpu_ring.h').read_text()
 pre=(previous/'fixture-prefix.c').read_text().replace('@VID@',str(d/'vid.h')).replace('@GFXENUM@',str(s/'drivers/gpu/drm/amd/include/asic_reg/gca/gfx_8_0_enum.h'))
 pre=pre.replace('u64 gpu_addr;};','u64 gpu_addr;bool is_le;};').replace('ib->ptr=ib_memory;','ib->is_le=false;ib->ptr=ib_memory;')
 code=gfx[:gfx.index('#include')]+pre
 for sig in ['static inline u32 amdgpu_ring_encode_dw(','static inline void amdgpu_ring_write(','static inline u32 amdgpu_ib_get_value(','static inline void amdgpu_ib_set_value(']:code+=function(header,sig)
 for n in ['gfx_v8_0_ring_emit_ib_gfx','gfx_v8_0_ring_emit_ib_compute','gfx_v8_0_ring_emit_fence_gfx','gfx_v8_0_ring_emit_fence_compute']:code+=function(gfx,'static void '+n+'(')
 code+=function(fence,'static u32 amdgpu_fence_read(')+(previous/'fixture-model.c').read_text()
 test=function(gfx,'static int gfx_v8_0_ring_test_ib(')
 code+=test.replace('gfx_v8_0_ring_test_ib(','test_original(')+test.replace('gfx_v8_0_ring_test_ib(','test_candidate(')
 main=(previous/'fixture-main.c').read_text().replace('if(model==1||model==3)expect=-ETIMEDOUT;', 'if(model==3'+('' if policy=='new' else '||model==1')+')expect=-ETIMEDOUT;').replace('if(version==0 && model==0)expect=-EINVAL;','')
 code+=main
 source=w/(policy+'.c');source.write_text(code);outputs={}
 for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc','-cpu','e500v2'])]:
  exe=w/(policy+'-'+arch);cmd=[cc]+(['-mstackrealign'] if arch=='x86' else [])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-builtin','-fno-pie','-no-pie','-static',str(source),'-o',str(exe)]
  p=subprocess.run(cmd,capture_output=True);(w/(policy+'-'+arch+'-compile.log')).write_bytes(p.stderr);p.check_returncode()
  p=subprocess.run(runner+[str(exe)],capture_output=True,timeout=30);assert p.returncode==0,(policy,arch,p.returncode,p.stderr.decode())
  outputs[arch]=p.stdout
 assert outputs['ppc']==outputs['x86']
 results.append({'policy':policy,'cases_per_arch':512,'normalized_result_bytes':len(outputs['ppc']),'fixture_sha256':hashlib.sha256(code.encode()).hexdigest()})
r={'status':'PASS','results':results,'hardware_accessed':False,'negative_controls':['old BE requires modeled hardware fetch swap','new explicit LE succeeds with swap honored or absent','double conversion still fails BE','completed memory without wakeup still times out'],'scope':'Actual GFX/compute emitters, typed IB setters and test callers; scheduler/GPU endpoints remain modeled','remaining':'Hardware fetch, preamble completion, coherency, GPU address translation and IRQ behavior unproven'}
(w/'check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
