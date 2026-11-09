from pathlib import Path
import subprocess,difflib,json,hashlib
b=Path('/srv/data1/tabor-build/linux-live-001');old=b/'work/radeonsi-systemic-20261109-001';w=b/'work/mesa-3d-contracts-20261109-001';assert not w.exists();subprocess.run(['cp','-a','--reflink=auto',str(old),str(w)],check=True)
root=w/'mesa-source';patch='';before={};after={}
p=root/'src/gallium/drivers/radeonsi/si_query.c';s=p.read_text();n=s;before[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
for a,z in [('results[(i * 4) + 1] = 0x80000000;', 'results[(i * 4) + 1] = util_cpu_to_le32(0x80000000);'),('results[(i * 4) + 3] = 0x80000000;', 'results[(i * 4) + 3] = util_cpu_to_le32(0x80000000);'),('(uint64_t)current_result[start_index] | (uint64_t)current_result[start_index + 1] << 32','(uint64_t)util_le32_to_cpu(current_result[start_index]) |\n           (uint64_t)util_le32_to_cpu(current_result[start_index + 1]) << 32'),('(uint64_t)current_result[end_index] | (uint64_t)current_result[end_index + 1] << 32','(uint64_t)util_le32_to_cpu(current_result[end_index]) |\n         (uint64_t)util_le32_to_cpu(current_result[end_index + 1]) << 32'),('result->u64 = *(uint64_t *)buffer;','result->u64 = util_le64_to_cpu(*(uint64_t *)buffer);')]:
 assert n.count(a)==1,a;n=n.replace(a,z)
p.write_text(n);after[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest();patch+=''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/'+str(p.relative_to(root)),tofile='b/'+str(p.relative_to(root))))
(w/'query-before.c').write_text(s);(w/'query-after.c').write_text(n)
p=root/'src/gallium/drivers/radeonsi/si_perfcounter.c';s=p.read_text();before[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest();a='uint32_t value = results[counter->base + j * counter->stride];';assert s.count(a)==1
n=s.replace(a,'uint32_t value = util_le64_to_cpu(results[counter->base + j * counter->stride]);');p.write_text(n);after[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest();patch+=''.join(difflib.unified_diff(s.splitlines(True),n.splitlines(True),fromfile='a/'+str(p.relative_to(root)),tofile='b/'+str(p.relative_to(root))))
(w/'perfcounter-before.c').write_text(s);(w/'perfcounter-after.c').write_text(n)
(w/'0007-radeonsi-query-memory-byte-contract.patch').write_text(patch)
(w/'query-contract-source.json').write_text(json.dumps({'parent':str(old),'before':before,'after':after,'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'scope':'GPU-visible status markers and CPU reads of GPU query/timestamp/perfcounter memory; native API results unchanged','hardware_tested':False},indent=2)+'\n');print(w)
