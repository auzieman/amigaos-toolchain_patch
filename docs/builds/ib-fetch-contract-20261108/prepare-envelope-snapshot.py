from pathlib import Path
import hashlib,json,difflib
s=Path('tabor-spe-toolchain/work/ib-flow-009-review');w=Path('tabor-spe-toolchain/docs/builds/ib-fetch-contract-20261108');g=(s/'gfx_v8_0.c').read_text();n=g
# Capture only CPU mapped memory, once, after existing timeout. No new GPU commands/register reads.
a=n.index('static int gfx_v8_0_ring_test_ib(');b=n.index('static void gfx_v8_0_free_microcode(',a);f=n[a:b]
f=f.replace('\tunsigned int index;','\tunsigned int index, diag_i;\n\tu64 submit_start;')
f=f.replace('\tr = amdgpu_ib_schedule(ring, 1, &ib, NULL, &f);','\tsubmit_start = ring->wptr;\n\tr = amdgpu_ib_schedule(ring, 1, &ib, NULL, &f);')
needle='\t\tr = -ETIMEDOUT;\n\t\tgoto err2;'
assert f.count(needle)==1
new='''\t\t/* Snapshot the published envelope, not just its IB payload. All
		 * reads below are CPU mappings already owned by this submission.
		 * No MMIO, new work, reset, fence processing or recovery.
		 */
		dev_err(adev->dev,
			"IB_ENVELOPE start=%llu end=%llu mask=%08x ring_lo=%08x ring_hi=%08x le=%u\\n",
			(unsigned long long)submit_start,
			(unsigned long long)ring->wptr, ring->buf_mask,
			lower_32_bits(ring->gpu_addr), upper_32_bits(ring->gpu_addr),
			ib.is_le);
		dev_err(adev->dev,
			"IB_WRITEBACK rptr_bytes=%4ph wptr_bytes=%4ph cond_bytes=%4ph cond_lo=%08x cond_hi=%08x\\n",
			ring->rptr_cpu_addr, ring->wptr_cpu_addr,
			ring->cond_exe_cpu_addr,
			lower_32_bits(ring->cond_exe_gpu_addr),
			upper_32_bits(ring->cond_exe_gpu_addr));
		for (diag_i = 0; diag_i < 128 && diag_i < ring->wptr - submit_start;
		     diag_i++) {
			u32 word = READ_ONCE(ring->ring[(submit_start + diag_i) & ring->buf_mask]);

			dev_err(adev->dev, "IB_RING word=%u bytes=%4ph\\n", diag_i, &word);
		}
		for (diag_i = 0; diag_i < ib.length_dw && diag_i < 16; diag_i++) {
			u32 word = READ_ONCE(ib.ptr[diag_i]);

			dev_err(adev->dev, "IB_PAYLOAD word=%u bytes=%4ph\\n", diag_i, &word);
		}
'''+needle
f=f.replace(needle,new);n=n[:a]+f+n[b:]
patch=''.join(difflib.unified_diff(g.splitlines(True),n.splitlines(True),fromfile='a/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c',tofile='b/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c'))
(w/'0030-gfx8-cpu-envelope-snapshot.patch').write_text(patch)
(w/'source-audit-009.json').write_text(json.dumps({'baseline_release':'6.12.113-tabor-e2e-009','source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in s.glob('*.c')},'physical_result':'IB swap-policy change did not resolve timeout; readable console and responsiveness user confirmed','diagnostic_patch':'CPU mapped ring envelope and IB bytes only; not installed','hardware_accessed_by_audit':False},indent=2)+'\n')
print('Created source-pinned CPU-only diagnostic patch; not deployed')
