from pathlib import Path
import runpy,subprocess,time,re,json
b=runpy.run_path('tabor-spe-toolchain/work/modular-usb-update-20261105-001/board_access.py')['base'];d=Path('tabor-spe-toolchain/docs/builds/gpu-memory-contract-20261109')
def ssh(c,**kw):return subprocess.run(['ssh',*b,'root@192.168.1.249',c],**kw)
for name in ['gfx-write','read-vram']:
 src='/srv/data1/tabor-build/linux-live-001/work/gfx-write-20261109-003/'+name
 a=subprocess.Popen(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','cat '+src],stdout=subprocess.PIPE)
 r=ssh('cat > /run/'+name+'; chmod 755 /run/'+name+'; /sbin/busybox-modules sha256sum /run/'+name,stdin=a.stdout,capture_output=True,text=True);a.stdout.close();assert a.wait()==0;r.check_returncode();h=subprocess.check_output(['python3','lab/consolidation-20261002/r730-prep-20261031/remote.py','sha256sum '+src],text=True).split()[0];assert h==r.stdout.split()[0]
loader='/opt/tabor-radeonsi-20261109/lib/ld.so.1 --library-path /opt/tabor-radeonsi-20261109/lib:/opt/tabor-radeonsi-20261109/usr/lib '
trace='/sys/kernel/tracing/instances/tabor-vm012';names='amdgpu_vm_flush amdgpu_vm_set_ptes amdgpu_vm_copy_ptes amdgpu_cs_ioctl'
log=(d/'held-test.txt').open('w');proc=None
try:
 ssh('set -e; echo 0 > '+trace+'/tracing_on; echo > '+trace+'/trace; for n in '+names+'; do echo 1 > '+trace+'/events/amdgpu/$n/enable; done; echo 1 > '+trace+'/tracing_on',check=True)
 proc=subprocess.Popen(['ssh',*b,'root@192.168.1.249','/run/busybox-render-tools timeout 35 '+loader+'/run/gfx-write uswc hold'],stdout=log,stderr=subprocess.STDOUT)
 for i in range(12):
  time.sleep(1)
  if 'HOLDING_ALLOCATION' in (d/'held-test.txt').read_text():break
 else:raise RuntimeError('allocation hold not reached')
 r=ssh('cat '+trace+'/trace',capture_output=True,text=True,check=True);(d/'held-vm-trace.txt').write_text(r.stdout)
 leaf=re.findall(r'amdgpu_vm_set_ptes: pe=([0-9a-f]+), addr=([0-9a-f]+), incr=4096, flags=77, count=1',r.stdout);assert len(leaf)==1,leaf
 root=re.findall(r'amdgpu_vm_flush: ring=gfx, id=(\d+), hub=0, pd_addr=([0-9a-f]+)',r.stdout);assert len(root)==1,root
 pe,addr=map(lambda x:int(x,16),leaf[0]);pd=int(root[0][1],16);base=0xf400000000
 assert base<=pe<base+0x100000000 and base<=pd<base+0x100000000
 result={'vmid':int(root[0][0]),'pte_gpu_address':hex(pe),'expected_pte':hex(addr|0x77),'pde_gpu_address':hex(pd),'reads':{}}
 for label,gpu in [('pte',pe),('pde',pd)]:
  r=ssh('/run/busybox-render-tools timeout 5 '+loader+'/run/read-vram '+format(gpu-base,'x'),capture_output=True,text=True,timeout=10,check=True)
  result['reads'][label]=r.stdout.strip();print(label,r.stdout.strip(),flush=True)
 (d/'held-pte-result.json').write_text(json.dumps(result,indent=2)+'\n')
finally:
 ssh('echo 0 > '+trace+'/tracing_on; for n in '+names+'; do echo 0 > '+trace+'/events/amdgpu/$n/enable; done')
 if proc:
  try:proc.wait(timeout=35)
  except subprocess.TimeoutExpired:proc.terminate()
 log.close()
print((d/'held-test.txt').read_text())
