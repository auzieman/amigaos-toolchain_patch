from pathlib import Path
import difflib,json,hashlib
b=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-008/source')
w=Path('/home/owner/ib-fetch-contract-20261108');w.mkdir(exist_ok=True)
files={};out={}
for n in ['amdgpu_ring.h','amdgpu_ib.c','gfx_v8_0.c']:
 rel='drivers/gpu/drm/amd/amdgpu/'+n;s=(b/rel).read_text();files[n]=s
 if n=='amdgpu_ring.h':
  old='\tuint32_t\t\t\tflags;\n};';assert s.count(old)==1
  s=s.replace(old,'\tuint32_t\t\t\tflags;\n\t/* Explicit CPU encoding of kernel-owned IB words; legacy is native. */\n\tbool\t\t\t\tis_le;\n};')
  s=s.replace('return ib->ptr[idx];','return ib->is_le ? le32_to_cpu(ib->ptr[idx]) : ib->ptr[idx];')
  s=s.replace('ib->ptr[idx] = value;','ib->ptr[idx] = ib->is_le ? cpu_to_le32(value) : value;')
 elif n=='amdgpu_ib.c':
  start=s.index('int amdgpu_ib_get(');i=s.index('\n\tif (size)',start)
  s=s[:i]+'\n\tib->is_le = false;\n'+s[i:]
 else:
  old='''\tib.ptr[0] = PACKET3(PACKET3_WRITE_DATA, 3);
\tib.ptr[1] = WRITE_DATA_DST_SEL(5) | WR_CONFIRM;
\tib.ptr[2] = lower_32_bits(gpu_addr);
\tib.ptr[3] = upper_32_bits(gpu_addr);
\tib.ptr[4] = 0xDEADBEEF;
\tib.length_dw = 5;'''
  assert s.count(old)==1
  new='''\t/* Test explicit LE fetch without relying on the legacy IB swap bits.
\t * AVFS and userspace submissions retain their existing native contract.
\t */
\tib.is_le = amdgpu_ring_uses_sw_le(ring);
\tib.length_dw = 5;
\tamdgpu_ib_set_value(&ib, 0, PACKET3(PACKET3_WRITE_DATA, 3));
\tamdgpu_ib_set_value(&ib, 1, WRITE_DATA_DST_SEL(5) | WR_CONFIRM);
\tamdgpu_ib_set_value(&ib, 2, lower_32_bits(gpu_addr));
\tamdgpu_ib_set_value(&ib, 3, upper_32_bits(gpu_addr));
\tamdgpu_ib_set_value(&ib, 4, 0xDEADBEEF);'''
  s=s.replace(old,new)
  assert s.count('(2 << 0) |')==2
  s=s.replace('(2 << 0) |','(ib->is_le ? 0 : (2 << 0)) |')
 out[n]=s;(w/n).write_text(s)
patch=''.join(''.join(difflib.unified_diff(files[n].splitlines(True),out[n].splitlines(True),fromfile='a/drivers/gpu/drm/amd/amdgpu/'+n,tofile='b/drivers/gpu/drm/amd/amdgpu/'+n)) for n in files)
(w/'0029-gfx8-test-explicit-little-endian-ib-fetch.patch').write_text(patch)
(w/'prepare.json').write_text(json.dumps({'status':'experimental-encoding-pair-not-hardware-validated','parent':'e2e-usb-20261108-008','inputs':{n:hashlib.sha256(s.encode()).hexdigest() for n,s in files.items()},'outputs':{n:hashlib.sha256(s.encode()).hexdigest() for n,s in out.items()},'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'scope':'Only gfx8 selected-ring selftest marks an IB as LE; get defaults native, preserving AVFS and job/user streams'},indent=2)+'\n')
