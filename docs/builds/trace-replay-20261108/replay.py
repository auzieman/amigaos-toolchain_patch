"""R730-only fail-closed trace corpus extraction and actual SMU sender replay."""
from pathlib import Path
import re,json,hashlib,subprocess
W=Path('/srv/data1/tabor-build/source-review/trace-replay-20261108');W.mkdir(exist_ok=True)
trace=Path('/srv/data1/tabor-build/linux-live-001/hardware-evidence/x86-smu-20261106/first-bind-registers.trace')
rx=re.compile(r'([0-9.]+): amdgpu_device_([wr])reg: (0x[0-9a-f]+), (0x[0-9a-f]+), (0x[0-9a-f]+)')
transactions=[];pending=None;argument=None;events=0
for line in trace.open():
 m=rx.search(line)
 if not m:continue
 events+=1;t,op,device,reg,value=m.groups();reg=int(reg,16);value=int(value,16)
 if op=='w' and reg==0xa4:argument=value
 if op=='w' and reg==0x94:
  pending={'time':float(t),'message':value,'argument':argument,'response':None};transactions.append(pending);argument=None
 if op=='r' and reg==0x95 and value and pending and pending['response'] is None:pending['response']=value
assert transactions,'No captured transactions'
missing=[i for i,t in enumerate(transactions) if t['response'] is None]
if missing:raise RuntimeError('Missing captured responses: '+str(missing))
(W/'transactions.json').write_text(json.dumps(transactions,indent=2)+'\n')
# Actual production sender functions already extracted in whole-flow transport fixture.
base=Path('/srv/data1/tabor-build/source-review/smu-flow-review-20261108/transport.c').read_text()
base=base[:base.index('int main(void) {')]
cases='struct transaction {u32 message,arg,response,has_arg;};\nstatic const struct transaction cases[]={\n'+''.join('{%d,%d,%d,%d},\n'%(t['message'],t['argument'] or 0,t['response'],t['argument'] is not None) for t in transactions)+'};\n'
main=r'''
int main(void) {
 struct amdgpu_device dev={0};struct pp_hwmgr h={CHIP_POLARIS11,0,&dev};
 for(unsigned i=0;i<sizeof(cases)/sizeof(cases[0]);i++) {
  const struct transaction*t=&cases[i];arg=0xdeadbeef;message=0;injected=t->response;
  int result=t->has_arg?smu7_send_msg_to_smc_with_parameter(&h,t->message,t->arg):smu7_send_msg_to_smc(&h,t->message);
  int expected=t->response==1?0:t->response==0xfe?-EOPNOTSUPP:t->response==0xffff?-ENXIO:-EIO;
  if(result!=expected||message!=t->message||arg!=(t->has_arg?t->arg:0xdeadbeef))return 1;
  hex(i);hex(message);hex(t->has_arg);hex(arg);hex(response);hex(result);emit("\n",1);
 }
 return 0;
}
'''
code=base+cases+main;(W/'trace-replay.c').write_text(code)
for arch,cc,runner in [('x86','gcc',[]),('ppc','powerpc-linux-gnu-gcc',['qemu-ppc'])]:
 exe=W/('replay-'+arch)
 cmd=[cc]+(['-mstackrealign'] if arch=='x86' else [])+['-O2','-ffreestanding','-nostdlib','-fno-stack-protector','-fno-pie','-no-pie','-static',str(W/'trace-replay.c'),'-o',str(exe)]
 c=subprocess.run(cmd,capture_output=True);(W/(arch+'-compile.log')).write_bytes(c.stderr);c.check_returncode()
 c=subprocess.run(runner+[str(exe)],capture_output=True);(W/(arch+'.log')).write_bytes(c.stdout);c.check_returncode()
assert (W/'x86.log').read_bytes()==(W/'ppc.log').read_bytes()
with trace.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
summary={'trace_sha256':digest,'register_events':events,'captured_transactions':len(transactions),'missing_responses':len(missing),'captured_sclk_masks':[t for t in transactions if t['message']==0x145],'sender_replay':'PASS','replay_x86_equals_ppc':True,'replayed_captured_response_values_only':True,'complete_gpu_preflight':'INCOMPLETE','missing_coverage':['raw complete power/clock table snapshots','ATOM request and response buffers','encoder command memory and hardware swap effect','actual DMA/coherency/timing','trace buffer loss statistics'],'trace_scope':'Only six selected numeric register offsets; not a full PCIe/buffer trace. Poll counts/timing and raw bus transactions are not replayed.','hardware_accessed':False}
(W/'receipt.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
