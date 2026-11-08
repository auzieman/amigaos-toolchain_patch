"""Build and package one complete 6.12 kernel/modules set on the bounded R730."""
from pathlib import Path
import difflib,gzip,hashlib,json,os,shutil,struct,subprocess,zlib
parent=Path('/base/work/e2e-usb-20261108-006')
w=Path('/candidate');src=w/'source';out=w/'output';bundle=w/'bundle'
release='6.12.113-tabor-e2e-007'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r={'status':'started','kernel_release':release,'parent_candidate':'e2e-usb-20261108-006','parent_module_sha256':'39cb3f14c248af27a10ac04d970308c669f18b710deb7633c4380cab130a7a90','tools_image':'sha256:2781e11839beffa351f8c411d71b7e2bd1ae0336d24c60b407778c3350dd9da0','commands':[],'usb_written':False,'hardware_booted':False}
try:
 assert src.is_dir() and out.is_dir() and not (w/'receipt.json').exists(),'fresh prepared build required'
 assert sha(parent/'output/drivers/gpu/drm/amd/amdgpu/amdgpu.ko')==r['parent_module_sha256']
 parent_receipt=json.loads((parent/'receipt.json').read_text())
 stage=parent_receipt['source_patch_chain']
 stage['source_files_sha256'].update(parent_receipt['boundary_patch']['outputs'])
 for rel,digest in stage['source_files_sha256'].items():assert sha(parent/'source'/rel)==digest,rel
 original=(out/'.config').read_text()
 assert sha(parent/'output/.config')=='af8ff9c065e883f3f54b23a4838e09f81f723db245d18b3968e934fa1602a5a4'
 desired=original.replace('CONFIG_LOCALVERSION="-tabor-e2e-006"','CONFIG_LOCALVERSION="-tabor-e2e-007"');assert desired!=original
 (out/'.config').write_text(desired)
 # Copied Kbuild contains the accepted historical absolute path. Bind aliases
 # are established by the launcher, pointing exclusively to this private copy.
 make=['make','-C','/base/work/tabor-smu-diagnostics-20261105-003/source','O=/base/work/tabor-smu-diagnostics-20261105-003/output','ARCH=powerpc','CROSS_COMPILE=powerpc-linux-gnu-']
 with (w/'build.log').open('w') as log:
  def run(cmd):
   r['commands'].append(cmd);log.write('$ '+repr(cmd)+'\n');log.flush()
   subprocess.run(cmd,check=True,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'KBUILD_BUILD_USER':'tabor','KBUILD_BUILD_HOST':'lab','KBUILD_BUILD_TIMESTAMP':'1970-01-01 00:00:00 UTC','KBUILD_BUILD_VERSION':'1','SOURCE_DATE_EPOCH':'0'})
  run(make+['olddefconfig'])
  cfg=(out/'.config').read_text();assert cfg==desired,'unexpected config migration'
  for key in ['CONFIG_SMP=y','CONFIG_VT=y','CONFIG_VT_CONSOLE=y','CONFIG_FRAMEBUFFER_CONSOLE=y','CONFIG_DRM_FBDEV_EMULATION=y','CONFIG_DRM_AMDGPU=m','CONFIG_EXT4_FS=y','CONFIG_USB_STORAGE=y']:
   assert key in cfg.splitlines(),key
  run(make+['-j4','vmlinux','modules','dtbs'])
  assert (out/'include/config/kernel.release').read_text().strip()==release
  root=bundle/'root';fat=bundle/'fat/boot/e2e';fat.mkdir(parents=True)
  run(make+['INSTALL_MOD_PATH='+str(root),'modules_install'])
  run(['depmod','-b',str(root),'-F',str(out/'System.map'),release])
  run(['powerpc-linux-gnu-objcopy','-O','binary',str(out/'vmlinux'),str(w/'kernel.bin')])
  elf=(out/'vmlinux').read_bytes();assert elf[:6]==b'\x7fELF\x01\x02'
  phoff=struct.unpack_from('>I',elf,28)[0];phsize,phnum=struct.unpack_from('>HH',elf,42)
  loads=[struct.unpack_from('>8I',elf,phoff+i*phsize) for i in range(phnum)];loads=[x for x in loads if x[0]==1]
  assert min(x[3] for x in loads)==0
  memory_end=max(x[3]+x[5] for x in loads);assert memory_end<0x04000000
  raw=(w/'kernel.bin').read_bytes();(w/'kernel.gz').write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
  run(['mkimage','-A','ppc','-O','linux','-T','kernel','-C','gzip','-a','0','-e','0','-n','A1222 6.12 coherent test','-d',str(w/'kernel.gz'),str(fat/'uImage')])
  blob=(fat/'uImage').read_bytes();magic,hcrc,stamp,size,load,entry,dcrc=struct.unpack_from('>7I',blob);header=bytearray(blob[:64]);header[4:8]=b'\0'*4
  assert magic==0x27051956 and len(blob)==size+64 and zlib.crc32(header)==hcrc and zlib.crc32(blob[64:])==dcrc
  assert gzip.decompress(blob[64:])==raw
  shutil.copyfile(out/'arch/powerpc/boot/dts/fsl/tabor-a1222.dtb',fat/'tabor.dtb')
  for n in ['build','source']:
   p=root/'lib/modules'/release/n
   if p.is_symlink():p.unlink()
  # Firmware must match the retained known payload; never fetch a moving pack.
  fwroot=Path('/base/work/layered-rescue-20261105-001/root/lib/firmware')
  names=sorted(set(subprocess.check_output(['modinfo','-F','firmware',str(out/'drivers/gpu/drm/amd/amdgpu/amdgpu.ko')],text=True).splitlines()))
  names=[n for n in names if 'polaris11' in n]
  assert names
  for n in names:
   p=root/'lib/firmware'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(fwroot/n,p)
  # Use a new release directory so normal modprobe cannot select an old module.
  module=root/'lib/modules'/release/'kernel/drivers/gpu/drm/amd/amdgpu/amdgpu.ko'
  assert sha(module)==sha(out/'drivers/gpu/drm/amd/amdgpu/amdgpu.ko')
  import runpy
  inspect=runpy.run_path('/qualification/verify-ppc32-module.py')['inspect']
  r['module_verification']=inspect(module,release,out/'Module.symvers')
  r['kernel_physical_memory_end']=hex(memory_end)
  r['source_patch_chain']=stage
  r['boundary_patch']=json.loads((w/'boundary-stage.json').read_text())
  r['tools']={n:subprocess.check_output([n,'--version'],text=True).splitlines()[0] for n in ['powerpc-linux-gnu-gcc','powerpc-linux-gnu-ld']}
  r['config_sha256']=sha(out/'.config');r['vmlinux_sha256']=sha(out/'vmlinux');r['system_map_sha256']=sha(out/'System.map')
  r['firmware_sha256']={n:sha(root/'lib/firmware'/n) for n in names}
  r['bundle_files_sha256']={str(p.relative_to(bundle)):sha(p) for p in bundle.rglob('*') if p.is_file() and not p.is_symlink()}
  r['module_count']=len(list(root.rglob('*.ko')))
  r['expected_usb_serial']='03001919041721081205';r['expected_root_partuuid']='a1221105-02'
  r['status']='complete-kernel-modules-firmware-bundle-not-installed'
  (bundle/'manifest.json').write_text(json.dumps(r,indent=2)+'\n')
  run(['tar','cf',str(w/'update.tar'),'-C',str(bundle),'manifest.json','fat','root'])
  r['tar_sha256']=sha(w/'update.tar');r['tar_bytes']=(w/'update.tar').stat().st_size
except BaseException as e:
 r['status']='failed';r['error']=str(e);raise
finally:
 (w/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
