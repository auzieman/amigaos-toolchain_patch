"""Pre-hardware x86-vs-PPC oracle for the VM page-table encode path (SDMA v3 updates).

The real amdgpu_vm_sdma_update, amdgpu_vm_sdma_copy_ptes, amdgpu_vm_sdma_set_ptes,
amdgpu_vm_map_gart and sdma_v3_0_vm_{copy_pte,write_pte,set_pte_pde} are extracted from an old
tree (vanilla v6.12.113) and a new tree (kernel 021). They build page-table updates into small
SDMA IBs. A model of the SDMA engine then executes each IB as the hardware sees it:
- command dwords are the CPU-native words, because SDMA v3 fetches IBs with its hardware
  32-bit swap on big-endian;
- COPY_LINEAR source data is read as raw bytes (swap field 0).
The page table is kept as LE GPU memory, and the entries are printed from it.

Cases:
- a 2 MiB GTT BO (512 scattered pages, copy path, split over many IBs; entry 16 is
  glamor's IB page at VA 0x210000);
- a contiguous VRAM range (GEN_PTEPDE);
- a 2-entry update (WRITE).

Oracle: old-x86 == new-x86, new-ppc == x86, and old-ppc != x86. No GPU is accessed.

usage: python3 harness.py OLD_SRC NEW_SRC WORKDIR
"""
import json, re, subprocess, sys
from pathlib import Path

OLD, NEW, W = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
W.mkdir(parents=True, exist_ok=True)
AMD = 'drivers/gpu/drm/amd/amdgpu'
HERE = Path(__file__).resolve().parent
# Freestanding printf/syscall base shared with the ATOM/UVD oracle.
BASE = re.search(r"BASE = r'''(.*?)'''",
                 (HERE.parent / 'atom-uvd-harness-20261124/harness.py').read_text(), re.S).group(1)


def span(text, sig):
    i = text.find(sig)
    if i < 0:
        raise SystemExit(f'missing: {sig}')
    i = text.rfind('\n', 0, i) + 1
    j = text.index('{', i)
    d = 0
    for k in range(j, len(text)):
        d += {'{': 1, '}': -1}.get(text[k], 0)
        if d == 0:
            return text[i:k + 1]


SHIM = r'''
#define cpu_to_le64_(x) (x)
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define cpu_to_le64(x) ((u64)__builtin_bswap64((u64)(x)))
#else
#define cpu_to_le64(x) ((u64)(x))
#endif
typedef u64 __le64;
typedef u64 dma_addr_t;
#define PAGE_SHIFT 12
#define PAGE_MASK (~((1ull << PAGE_SHIFT) - 1))
#include "tonga_sdma_pkt_open.h"
#define AMDGPU_KERNEL_JOB_ID_VM_UPDATE 0
#define trace_amdgpu_vm_copy_ptes(...) do {} while (0)
#define trace_amdgpu_vm_set_ptes(...) do {} while (0)
struct dma_fence { int x; };
struct dma_resv_iter { int x; };
#define dma_resv_iter_begin(c, r, u) do { (void)(c); } while (0)
#define dma_resv_for_each_fence_unlocked(c, f) for ((f) = NULL; (f); )
#define dma_resv_iter_end(c) do {} while (0)
static void dma_fence_get(struct dma_fence *f) { (void)f; }
static void dma_fence_put(struct dma_fence *f) { (void)f; }
struct drm_sched_job { int x; };
static int drm_sched_job_add_dependency(struct drm_sched_job *j, struct dma_fence *f) { (void)j; (void)f; return 0; }
struct amdgpu_ib { u64 gpu_addr; unsigned length_dw; u32 *ptr; };
struct amdgpu_job { struct drm_sched_job base; struct amdgpu_ib ibs[1]; };
struct amdgpu_vm_pte_funcs { unsigned copy_pte_num_dw; };
struct amdgpu_device { struct { const struct amdgpu_vm_pte_funcs *vm_pte_funcs; } vm_manager; };
struct amdgpu_bo { struct { struct { void *resv; } base; } tbo; u64 gpu; };
struct amdgpu_bo_vm { struct amdgpu_bo bo; };
struct amdgpu_vm_update_params {
	struct amdgpu_device *adev; struct amdgpu_job *job; unsigned num_dw_left;
	dma_addr_t *pages_addr; bool immediate;
};
static u64 amdgpu_bo_gpu_offset_no_check(struct amdgpu_bo *bo) { return bo->gpu; }
'''

MODEL = r'''
/* GPU memory: the page table (LE) at PT_GPU, the SDMA IBs at IB_GPU */
#define PT_GPU 0xF400000000ull
#define IB_GPU 0xFF00800000ull
#define IB_DW (16u * 1024u)	/* AMDGPU_VM_SDMA_MAX_NUM_DW */
static u8 pt[8 * 1024];

static u32 ibmem[IB_DW];
static unsigned njobs, ncopy, nwrite, ngen;
static void pt_put64(u64 gpu, u64 v)
{
	unsigned o = gpu - PT_GPU;
	for (int i = 0; i < 8; i++) pt[o + i] = v >> (8 * i);
}
/* Execute the IB as SDMA v3 sees it on this host */
static void sdma_execute(struct amdgpu_ib *ib)
{
	const u32 *c = ib->ptr;	/* command dwords: CPU-native values (HW swap on BE) */
	unsigned i = 0;
	while (i < ib->length_dw) {
		u32 op = c[i] & 0xff;
		if (op == SDMA_OP_COPY) {
			u32 bytes = c[i + 1];
			u64 src = c[i + 3] | (u64)c[i + 4] << 32, dst = c[i + 5] | (u64)c[i + 6] << 32;
			const u8 *s = (const u8 *)ibmem + (src - IB_GPU);	/* data: raw bytes */
			memcpy(pt + (dst - PT_GPU), s, bytes);
			ncopy++; i += 7;
		} else if (op == SDMA_OP_WRITE) {
			u64 dst = c[i + 1] | (u64)c[i + 2] << 32;
			u32 ndw = c[i + 3];
			for (u32 k = 0; k < ndw; k += 2)
				pt_put64(dst + 4 * k, c[i + 4 + k] | (u64)c[i + 5 + k] << 32);
			nwrite++; i += 4 + ndw;
		} else if (op == SDMA_OP_GEN_PTEPDE) {
			u64 pe = c[i + 1] | (u64)c[i + 2] << 32;
			u64 flags = c[i + 3] | (u64)c[i + 4] << 32, addr = c[i + 5] | (u64)c[i + 6] << 32;
			u32 incr = c[i + 7], count = c[i + 9];
			for (u32 k = 0; k < count; k++)
				pt_put64(pe + 8 * k, (addr + (u64)k * incr) | flags);
			ngen++; i += 10;
		} else {
			printf("  unknown SDMA op %u at dw %u\n", op, i);
			return;
		}
	}
}
static struct amdgpu_job job;
static int amdgpu_vm_sdma_commit(struct amdgpu_vm_update_params *p, struct dma_fence **f)
{
	(void)f;
	if (p->job->ibs->length_dw) { sdma_execute(p->job->ibs); njobs++; }
	return 0;
}
static int amdgpu_vm_sdma_alloc_job(struct amdgpu_vm_update_params *p, unsigned count, int id)
{
	/* the real allocator's sizing: 256 dw, plus 2 per PTE on the copy path, capped at 16K */
	unsigned ndw = 256u + (p->pages_addr ? count * 2 : 0);
	(void)id;
	if (ndw > IB_DW) ndw = IB_DW;
	memset(ibmem, 0xee, sizeof(ibmem));
	job.ibs[0].ptr = ibmem; job.ibs[0].gpu_addr = IB_GPU; job.ibs[0].length_dw = 0;
	p->job = &job; p->num_dw_left = ndw;
	return 0;
}
#define amdgpu_vm_copy_pte(adev, ib, pe, src, count) sdma_v3_0_vm_copy_pte((ib), (pe), (src), (count))
#define amdgpu_vm_write_pte(adev, ib, pe, value, count, incr) sdma_v3_0_vm_write_pte((ib), (pe), (value), (count), (incr))
#define amdgpu_vm_set_pte_pde(adev, ib, pe, addr, count, incr, flags) sdma_v3_0_vm_set_pte_pde((ib), (pe), (addr), (count), (incr), (flags))
'''

MAIN = r'''
static void ptdump(const char *tag, unsigned first, unsigned n)
{
	printf("%s:", tag);
	for (unsigned k = first; k < first + n; k++) {
		u64 v = 0;
		for (int i = 7; i >= 0; i--) v = v << 8 | pt[8 * k + i];
		printf(" [%u]=%08x%08x", k, (u32)(v >> 32), (u32)v);
	}
	printf("\n");
}
static dma_addr_t pages[512];
int main(void)
{
	static const struct amdgpu_vm_pte_funcs funcs = { 7 };
	struct amdgpu_device adev = { { &funcs } };
	struct amdgpu_bo_vm vmbo; memset(&vmbo, 0, sizeof vmbo); vmbo.bo.gpu = PT_GPU;
	struct amdgpu_vm_update_params p; memset(&p, 0, sizeof p); p.adev = &adev;
	/* GTT pages: scattered, some above 4 GiB to exercise the high dword */
	for (unsigned i = 0; i < 512; i++)
		pages[i] = 0x10000000ull + (u64)((i * 37) % 512) * 0x3000 + ((i % 64) == 7 ? 0x100000000ull : 0);
	const u64 gtt_flags = 0x0040000000000073ull;	/* low valid/system/snoop/rw bits + a high flag */

	/* 1. 2 MiB GTT mapping at VA 0x200000: PT entries 512..1023 of the 2 MiB-aligned PT */
	memset(pt, 0, sizeof pt);
	p.pages_addr = pages;
	amdgpu_vm_sdma_alloc_job(&p, 0, 0);	/* as amdgpu_vm_sdma_prepare */
	int r = amdgpu_vm_sdma_update(&p, &vmbo, 0, 0, 512, 4096, gtt_flags);
	amdgpu_vm_sdma_commit(&p, NULL);
	printf("gtt r=%d jobs=%u copies=%u\n", r, njobs, ncopy);
	ptdump("gtt entries 0-3", 0, 4);
	ptdump("gtt entry 16 (VA 0x210000)", 16, 1);
	ptdump("gtt entries 7,71 (pages above 4 GiB)", 7, 1);
	ptdump("gtt entry 71", 71, 1);
	ptdump("gtt entries 508-511", 508, 4);
	unsigned bad = 0;
	for (unsigned k = 0; k < 512; k++) {
		u64 v = 0, want = (pages[k] & 0xFFFFFFFFFFFFF000ull) | gtt_flags;
		for (int i = 7; i >= 0; i--) v = v << 8 | pt[8 * k + i];
		bad += v != want;
	}
	printf("gtt entries wrong vs expected: %u of 512\n", bad);

	/* 2. contiguous VRAM: GEN_PTEPDE */
	memset(pt, 0, sizeof pt); njobs = 0;
	p.pages_addr = NULL;
	amdgpu_vm_sdma_alloc_job(&p, 0, 0);
	r = amdgpu_vm_sdma_update(&p, &vmbo, 0, 0x0F4FF00000ull, 64, 4096, 0x0000000000000061ull);
	amdgpu_vm_sdma_commit(&p, NULL);
	printf("vram r=%d gen=%u\n", r, ngen);
	ptdump("vram entries 0,1,63", 0, 2);
	ptdump("vram entry 63", 63, 1);

	/* 3. two entries: WRITE */
	memset(pt, 0, sizeof pt); njobs = 0;
	amdgpu_vm_sdma_alloc_job(&p, 0, 0);
	r = amdgpu_vm_sdma_update(&p, &vmbo, 8 * 5, 0x0F4FFA0000ull, 2, 4096, 0x0000000000000001ull);
	amdgpu_vm_sdma_commit(&p, NULL);
	printf("pde r=%d writes=%u\n", r, nwrite);
	ptdump("pde entries 5,6", 5, 2);
	return 0;
}
'''


def src(sdma_tree, vm_sdma_file):
    s3 = (sdma_tree / AMD / 'sdma_v3_0.c').read_text()
    vm = (sdma_tree / AMD / 'amdgpu_vm.c').read_text()
    vs = Path(vm_sdma_file).read_text()
    fns = [span(s3, 'static void sdma_v3_0_vm_copy_pte('), span(s3, 'static void sdma_v3_0_vm_write_pte('),
           span(s3, 'static void sdma_v3_0_vm_set_pte_pde('), span(vm, 'uint64_t amdgpu_vm_map_gart('),
           span(vs, 'static void amdgpu_vm_sdma_copy_ptes('), span(vs, 'static void amdgpu_vm_sdma_set_ptes('),
           span(vs, 'static int amdgpu_vm_sdma_update(')]
    return BASE + SHIM + MODEL + '\n\n'.join(fns) + MAIN


def run():
    out = {}
    for ver, f in (('old', OLD / AMD / 'amdgpu_vm_sdma.c'), ('new', NEW / AMD / 'amdgpu_vm_sdma.c')):
        c = W / f'pte-{ver}.c'
        c.write_text(src(NEW, f))
        for arch, cc, runner in (('x86', 'gcc', []), ('ppc', 'powerpc-linux-gnu-gcc', ['qemu-ppc'])):
            exe = W / f'pte-{ver}-{arch}'
            p = subprocess.run([cc, '-O2', '-static', '-nostdlib', '-ffreestanding', '-fno-builtin',
                                '-fno-stack-protector', '-fno-pie', '-no-pie', '-Wall', '-Wno-unused-function',
                                '-Wno-builtin-declaration-mismatch'] + (['-mstackrealign'] if arch == 'x86' else []) +
                               [f'-I{NEW / AMD}', str(c), '-o', str(exe), '-lgcc'], capture_output=True, text=True)
            if p.returncode:
                raise SystemExit(f'pte-{ver}-{arch} compile failed:\n{p.stderr}')
            p = subprocess.run(runner + [str(exe)], capture_output=True, text=True)
            o = p.stdout + (f'[exit {p.returncode}]\n' if p.returncode else '')
            (W / f'pte-{ver}-{arch}.log').write_text(o)
            out[f'{ver}-{arch}'] = o
    x86 = out['old-x86']
    v = {'x86_unchanged': out['new-x86'] == x86, 'new_ppc_matches_x86': out['new-ppc'] == x86,
         'old_ppc_differs': out['old-ppc'] != x86}
    v['status'] = 'PASS' if all(v.values()) else 'FAIL'
    return v


res = {'vm-pte': run(), 'gpu_accessed': False}
(W / 'receipt.json').write_text(json.dumps(res, indent=2) + '\n')
print(json.dumps(res, indent=2))
sys.exit(0 if res['vm-pte']['status'] == 'PASS' else 1)
