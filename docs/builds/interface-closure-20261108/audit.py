"""R730: inventory every candidate boundary in the pinned AMD source tree.
Counts are review candidates, never a correctness or execution-coverage claim.
"""
from pathlib import Path
import re,json,hashlib,os,resource
os.sched_setaffinity(0,{min(os.sched_getaffinity(0))});resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
S=Path('/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-004/source')
A=S/'drivers/gpu/drm/amd';W=Path('/srv/data1/tabor-build/source-review/interface-closure-20261108');W.mkdir(exist_ok=True)
patterns={
 'register_access':r'\b(?:RREG\w*|WREG\w*|readl|writel|readq|writeq|ioread\w*|iowrite\w*)\s*\(',
 'ring_publication':r'\bamdgpu_ring_(?:write\w*|commit|set_wptr)\s*\(',
 'indirect_buffer_store':r'\b(?:ib\s*(?:->|\.)\s*ptr|buffer)\s*\[[^;\n]*\]\s*=',
 'endian_policy':r'__BIG_ENDIAN|__LITTLE_ENDIAN|\b(?:cpu_to_(?:le|be)\d+|(?:le|be)\d+_to_cpu\w*)\s*\(|SWAP_ENABLE|SWAP_CNTL|ENDIAN_SWAP',
 'dma_and_mapping':r'\b(?:dma_\w+|memcpy_toio|memcpy_fromio|memset_io|memcpy|memset|ioremap\w*|memremap\w*)\s*\(',
 'ordering':r'\b(?:mb|rmb|wmb|dma_rmb|dma_wmb|mmiowb|READ_ONCE|WRITE_ONCE|amdgpu_device_flush_hdp|amdgpu_device_invalidate_hdp)\s*\(',
}
rx={k:re.compile(v)for k,v in patterns.items()};inventory=[];counts={k:0 for k in patterns};hashes={}
for p in sorted(A.rglob('*')):
 if p.suffix not in ('.c','.h'):continue
 t=p.read_text(errors='replace');hits=[]
 for n,line in enumerate(t.splitlines(),1):
  classes=[k for k,r in rx.items()if r.search(line)]
  if classes:
   for k in classes:counts[k]+=1
   hits.append(dict(line=n,classes=classes,text=line.strip()))
 if hits:
  name=str(p.relative_to(S));hashes[name]=hashlib.sha256(p.read_bytes()).hexdigest();inventory.append(dict(file=name,hits=hits))
(W/'source-candidates.json').write_text(json.dumps(inventory,indent=2)+'\n')
# Explicit owning contracts for the selected Polaris boot/render path.
rows=[
 ('MMIO registers','amdgpu/amdgpu_device.c','amdgpu_device_rreg','Linux readl/writel numeric accessor','compiled PPC accessor reviewed; actual MMIO remains hardware gate'),
 ('indexed SMC registers','pm/powerplay/smumgr/smu7_smumgr.c','smu7_send_msg_to_smc','native numeric register values','response and trace replay pass; timing open'),
 ('ATOM clock payload','amdgpu/atom.h','amdgpu_atom_set_clock_word','LE24+8 wire word','shared helpers tested'),
 ('raw PowerPlay clocks','pm/powerplay/hwmgr/smu7_hwmgr.c','smu7_get_pp_table_entry_callback_func_v1','LE raw clocks -> native once','0024 connected regression passes; hardware open'),
 ('SMU transfer objects','pm/powerplay/smumgr/polaris10_smumgr.c','polaris10_populate_single_graphic_level','native -> packed SMU BE fields','individual levels tested; full table snapshot open'),
 ('SMU SRAM upload','pm/powerplay/smumgr/smu7_smumgr.c','smu7_copy_bytes_to_smc','bytes packed MSB-first into numeric register','tail and connected transfer tests pass'),
 ('GFX/compute primary rings','amdgpu/amdgpu_ring.c','amdgpu_ring_uses_sw_le','software LE policy; hardware ring swap disabled on target','scratch tests pass; full workload open'),
 ('GFX indirect fetch','amdgpu/gfx_v8_0.c','gfx_v8_0_ring_emit_ib_gfx','BE packet fetch mode2 separate from primary ring','source identified; actual fetch not qualified'),
 ('compute indirect fetch','amdgpu/gfx_v8_0.c','gfx_v8_0_ring_emit_ib_compute','BE packet fetch mode2 separate from primary ring','source identified; shader storage and fetch open'),
 ('SDMA ring and IB','amdgpu/sdma_v3_0.c','sdma_v3_0_gfx_resume','distinct RB_SWAP and IB_SWAP settings','source identified; ring scratch passed, IB hardware open'),
 ('UVD decoder ring and IB','amdgpu/uvd_v6_0.c','uvd_v6_0_start','native words plus LMI hardware swap0xa','decoder ring test passed; IB workload open'),
 ('UVD encoder ring','amdgpu/uvd_v6_0.c','uvd_v6_0_enc_ring_emit_ib','software LE primary ring; indirect pointer does not prove payload conversion','encoder ring test passed; IB contract review required'),
 ('UVD encoder native IB producer','amdgpu/uvd_v6_0.c','uvd_v6_0_enc_get_create_msg','native buffer stores; must pair with actual encoder fetch contract','OPEN: no blanket conversion until shared LMI/fetch behavior resolved'),
 ('VCE ring and IB','amdgpu/vce_v3_0.c','vce_v3_0','LMI swap configuration and job payload contract','OPEN: not covered by UVD encoder ring result'),
 ('fence writeback','amdgpu/amdgpu_fence.c','amdgpu_fence_read','LE memory -> native; CPU writer LE','new actual read/write regression passes; GPU writeback open'),
 ('CPU page-table writer','amdgpu/amdgpu_gmc.c','amdgpu_gmc_set_pte_pde','native64 -> Linux writeq LE MMIO','new actual function regression passes with modeled writeq; DMA translation open'),
 ('Polaris interrupt vectors','amdgpu/tonga_ih.c','tonga_ih_decode_iv','LE dwords -> native fields','new actual decoder regression passes; IRQ delivery open'),
 ('interrupt doorbell shadow','amdgpu/tonga_ih.c','tonga_ih_set_rptr','native shadow store has upstream BE TODO','OPEN: determine shadow consumer and required format before change'),
 ('DMA addressing','amdgpu/gmc_v8_0.c','dma_set_mask_and_coherent','40bit device DMA mask; Linux mapping and SWIOTLB','OPEN: verify P1022 windows/cache policy with real device addresses'),
 ('publication/cache ordering','amdgpu/amdgpu_ib.c','amdgpu_device_flush_hdp','HDP flush before emission; invalidate before fence; ring commit publishes','OPEN: offline byte equality does not test physical ordering'),
 ('firmware containers and microcode','amdgpu/amdgpu_ucode.c','amdgpu_ucode','LE metadata; raw microcode byte transfer','OPEN: complete firmware-family copy/size/offset walk'),
 ('display scanout pixels','amdgpu/dce_v10_0.c','GRPH_ENDIAN_SWAP','pixel-format-specific hardware swap; separate from packets','OPEN: actual fbcon/KMS scanout and modeset'),
]
ledger=[]
for name,file,key,contract,status in rows:
 p=A/file;t=p.read_text();i=t.find(key)
 if i<0:raise RuntimeError((file,key))
 ledger.append(dict(channel=name,file=str(p.relative_to(S)),line=t[:i].count('\n')+1,anchor=key,contract=contract,status=status))
(W/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
r=dict(status='REVIEW_REQUIRED',hardware_accessed=False,deployment_allowed=False,source_root=str(S),candidate_files=len(inventory),candidate_counts=counts,ledger_contracts=len(ledger),file_sha256=hashes,warning='Static pattern candidates include other ASICs and dead branches; counts are neither coverage nor defect counts.')
(W/'audit-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='file_sha256'},indent=2))
