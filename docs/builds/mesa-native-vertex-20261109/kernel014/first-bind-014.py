#!/usr/bin/env python3
"""Capture fresh-boot Polaris testing off-board; remount root read-only before bind."""
import argparse, json, os, re, shlex, signal, subprocess, time
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--key',required=True);p.add_argument('--known-hosts',required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--host',default='192.168.1.249');p.add_argument('--jump',default='root@192.168.1.15')
p.add_argument('--candidate',default='/root/polaris-next/amdgpu-candidate.ko')
p.add_argument('--sha256',default='099a4e2477910f7c3b870946ae167f90bc9b5b3fbcc4923ad654dad20ad0a6bd')
p.add_argument('--installed-release', default='6.12.113-tabor-e2e-014', help='Test a complete installed kernel/module set with normal modprobe; no RAM module override')
p.add_argument('--num-kcq',type=int,choices=range(0,9),help='optional upstream kernel compute queue count; requires a compatible candidate')
a=p.parse_args()
if a.installed_release != "6.12.113-tabor-e2e-014":p.error("This scoped diagnostic requires the complete 014 kernel/module set")
release=a.installed_release or '6.12.113-tabor-modular'
if not re.fullmatch(r'[A-Za-z0-9._+-]+',release):p.error('invalid kernel release')
if a.installed_release:
 if a.num_kcq is not None:p.error('installed-set mode preserves installed module options')
 a.candidate='/lib/modules/'+release+'/kernel/drivers/gpu/drm/amd/amdgpu/amdgpu.ko'
a.output.mkdir(parents=True,exist_ok=False)
opts=['-F','/dev/null','-J',a.jump,'-i',a.key,'-o','IdentitiesOnly=yes','-o','BatchMode=yes','-o','ConnectTimeout=6','-o','ServerAliveInterval=2','-o','ServerAliveCountMax=2','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+a.known_hosts]
base=['ssh',*opts,'root@'+a.host];pci='/sys/bus/pci/devices/0001:01:00.0'
receipt={'candidate':a.candidate,'sha256':a.sha256,'stages':[],'status':'started','boot_defaults_changed':False,'num_kcq':a.num_kcq,'installed_release':a.installed_release,'module_loading':'normal-modprobe' if a.installed_release else 'RAM-candidate'}
receipt['test_module_options'] = {'polaris11_le_user_ib': True}
logger=None;held=False;candidate_loaded=False

def stop(proc):
 if proc.poll() is None:
  try:os.killpg(proc.pid,signal.SIGTERM)
  except ProcessLookupError:pass
  try:proc.wait(timeout=2)
  except subprocess.TimeoutExpired:
   try:os.killpg(proc.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   proc.wait()

def run(stage,command,timeout=15):
 print(stage,flush=True)
 item={'stage':stage};receipt['stages'].append(item)
 with (a.output/(stage+'.txt')).open('wb') as out:
  proc=subprocess.Popen([*base,command],stdin=subprocess.DEVNULL,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
  try:item['returncode']=proc.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   item['status']='timeout';stop(proc);raise RuntimeError(stage+' timed out')
 if item['returncode']:raise RuntimeError(stage+' failed; see captured output')
 return (a.output/(stage+'.txt')).read_text(errors='replace')
try:
 cmd='test "$(uname -r)" = '+shlex.quote(release)+' && ! grep -q "^amdgpu " /proc/modules && test "$(cat '+pci+'/vendor)" = 0x1002 && test "$(cat '+pci+'/device)" = 0x67ff && uname -r && cat /proc/uptime && /sbin/busybox-modules sha256sum '+shlex.quote(a.candidate)
 out=run('01-preflight',cmd);assert out.split()[-2]==a.sha256,'candidate hash mismatch'
 dry=run('01b-loader-options-preflight','modprobe -D amdgpu polaris11_le_user_ib=1')
 assert 'polaris11_le_user_ib=1' in dry, 'module loader drops command-line options; refusing first bind'
 with (a.output/'kmsg.txt').open('wb') as log,(a.output/'kmsg.stderr').open('wb') as err:
  logger=subprocess.Popen([*base,'cat /dev/kmsg'],stdin=subprocess.DEVNULL,stdout=log,stderr=err,start_new_session=True)
  run('02-capture-marker',"printf '<6>TABOR_CAPTURE_READY\\n' > /dev/kmsg")
  for i in range(50):
   if b'TABOR_CAPTURE_READY' in (a.output/'kmsg.txt').read_bytes():break
   if logger.poll() is not None:raise RuntimeError('capture exited before test')
   time.sleep(.1)
  else:raise RuntimeError('off-board capture marker not received')
  run('03-root-readonly','sync && mount -o remount,ro / && cat /proc/mounts')
  mounts=(a.output/'03-root-readonly.txt').read_text().splitlines()
  assert any(len(x.split())>3 and x.split()[1]=='/' and 'ro' in x.split()[3].split(',') for x in mounts),'root not verified read-only'
  if a.installed_release:
   receipt['installed_driver_load_started']=True
   run('04-load-installed-driver','modprobe amdgpu polaris11_le_user_ib=1',40);candidate_loaded=True
   assert run('05-verify-fetch-contract','cat /sys/module/amdgpu/parameters/polaris11_le_user_ib').strip() == 'Y', 'diagnostic option not enabled; stop before submitting explicit-LE commands'
  else:
   run('04-hold-pci',"printf '%s\\n' tabor-held > "+pci+'/driver_override');held=True
   run('05-load-dependencies','modprobe amdgpu',30)
   run('06-remove-unbound-original','test ! -e '+pci+'/driver && rmmod amdgpu')
   run('07-insert-held-candidate','insmod '+shlex.quote(a.candidate)+(' num_kcq='+str(a.num_kcq) if a.num_kcq is not None else ''),30);candidate_loaded=True
   run('08-release-override',"printf '\\n' > "+pci+'/driver_override');held=False
   run('09-bind',"printf '%s\\n' 0001:01:00.0 > /sys/bus/pci/drivers/amdgpu/bind",40)
  run('10-device-state','cat /proc/fb; ls -l '+pci+'/driver; cat /proc/uptime; cat /proc/modules')
  receipt['status']='test-returned-review-hardware-state'
except Exception as e:
 receipt['status']='incomplete';receipt['error']=str(e);print(str(e),flush=True)
finally:
 if logger:stop(logger)
 if held:
  try:run('cleanup-override',"printf '\\n' > "+pci+'/driver_override',8)
  except Exception:receipt['override_cleanup']='unconfirmed'
 receipt['candidate_insert_completed']=candidate_loaded
 (a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
