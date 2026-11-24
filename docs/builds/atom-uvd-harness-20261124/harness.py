"""Pre-hardware x86-vs-PPC oracle for patches 0040 (ATOM fields) and 0041 (UVD message/encoder IB).

The real driver functions are extracted from the 021 tree (old) and the patched tree (new).
Each is compiled for x86-64 and big-endian ppc32 (run under qemu-ppc) against the real
atombios.h/pptable.h layouts. The inputs are byte-identical LE VBIOS tables, LE UVD
messages, and a stub VBIOS interpreter that reads and writes its parameter space as LE bytes
(the firmware view). Outputs are driver-side values plus the bytes the GPU/VBIOS would see.

Oracle per test: old-x86 == new-x86 (x86 behaviour unchanged), new-ppc == x86 (fixed), and
old-ppc != x86 (the test exercises the bug). No GPU is accessed.

usage: python3 harness.py OLD_SRC NEW_SRC WORKDIR
"""
import json, re, subprocess, sys
from pathlib import Path

OLD, NEW, W = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
W.mkdir(parents=True, exist_ok=True)
AMD = 'drivers/gpu/drm/amd'


def span(text, sig):
    """Whole definition starting at the line holding sig, through its matching brace."""
    i = text.find(sig)
    if i < 0:
        return None
    i = text.rfind('\n', 0, i) + 1
    j = text.index('{', i)
    depth = 0
    for k in range(j, len(text)):
        depth += {'{': 1, '}': -1}.get(text[k], 0)
        if depth == 0:
            end = k + 1
            if text[end:end + 1] == ';':
                end += 1
            return text[i:end]
    raise ValueError(sig)


BASE = r'''
/* Freestanding: there is no ppc32 libc on the build host. Minimal printf over raw write(2). */
#include <stddef.h>
#include <stdarg.h>
static long sys3(long nr, long a, long b, long c)
{
#if defined(__x86_64__)
	long r;
	asm volatile("syscall" : "=a"(r) : "a"(nr), "D"(a), "S"(b), "d"(c) : "rcx", "r11", "memory");
	return r;
#else
	register long r0 asm("r0") = nr, r3 asm("r3") = a, r4 asm("r4") = b, r5 asm("r5") = c;
	asm volatile("sc" : "+r"(r0), "+r"(r3), "+r"(r4), "+r"(r5) : : "cr0", "r6", "r7", "r8", "r9", "r10", "r11", "r12", "ctr", "memory");
	return r3;
#endif
}
#if defined(__x86_64__)
#define NR_WRITE 1
#define NR_EXIT 60
#else
#define NR_WRITE 4
#define NR_EXIT 1
#endif
void *memset(void *p, int c, size_t n) { volatile unsigned char *b = p; while (n--) *b++ = c; return p; }
void *memcpy(void *d, const void *s, size_t n) { volatile unsigned char *o = d; const unsigned char *i = s; while (n--) *o++ = *i++; return d; }
static int printf(const char *f, ...)
{
	char buf[1024]; unsigned n = 0; va_list ap; va_start(ap, f);
	for (; *f && n < sizeof(buf) - 24; f++) {
		if (*f != '%') { buf[n++] = *f; continue; }
		int zero = 0, width = 0, lng = 0;
		f++;
		if (*f == '0') zero = 1, f++;
		while (*f >= '0' && *f <= '9') width = width * 10 + *f++ - '0';
		if (*f == 'l') lng = 1, f++;
		if (*f == 's') { for (const char *s = va_arg(ap, const char *); *s; s++) buf[n++] = *s; continue; }
		unsigned long long v; int neg = 0, base = *f == 'x' ? 16 : 10;
		if (*f == 'd') { long long s = lng ? va_arg(ap, long) : va_arg(ap, int); if (s < 0) neg = 1, s = -s; v = s; }
		else v = lng ? va_arg(ap, unsigned long) : va_arg(ap, unsigned);
		char t[24]; int k = 0;
		do t[k++] = "0123456789abcdef"[v % base]; while (v /= base);
		if (neg) buf[n++] = '-';
		while (k < width) t[k++] = zero ? '0' : ' ';
		while (k) buf[n++] = t[--k];
	}
	va_end(ap);
	sys3(NR_WRITE, 1, (long)buf, n);
	return n;
}
int main(void);
void _start(void) { sys3(NR_EXIT, main(), 0, 0); for (;;); }
typedef unsigned char u8; typedef u8 uint8_t; typedef unsigned short u16; typedef u16 uint16_t;
typedef unsigned int u32; typedef u32 uint32_t; typedef unsigned long long u64; typedef u64 uint64_t;
typedef signed char int8_t; typedef short int16_t; typedef int int32_t; typedef long long int64_t;
typedef _Bool bool;
#define true 1
#define false 0
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define __BIG_ENDIAN 4321
#define le16_to_cpu(x) ((u16)__builtin_bswap16((u16)(x)))
#define le32_to_cpu(x) ((u32)__builtin_bswap32((u32)(x)))
#else
#define le16_to_cpu(x) ((u16)(x))
#define le32_to_cpu(x) ((u32)(x))
#endif
#define cpu_to_le16 le16_to_cpu
#define cpu_to_le32 le32_to_cpu
#define __force
#define __counted_by(x)
static inline u16 get_unaligned_le16(const void *p) { const u8 *b = p; return b[0] | b[1] << 8; }
#define EINVAL 22
#define ENOENT 2
#define ENOSPC 28
#define upper_32_bits(x) ((u32)((u64)(x) >> 32))
#define lower_32_bits(x) ((u32)(x))
#define ALIGN(x, a) (((x) + (a) - 1) & ~((a) - 1))
#define max(a, b) ((a) > (b) ? (a) : (b))
#define min(a, b) ((a) < (b) ? (a) : (b))
#define DRM_ERROR(...) printf("  [DRM_ERROR] " __VA_ARGS__)
#define dev_WARN_ONCE(d, c, ...) ((c) ? printf("  [WARN] " __VA_ARGS__), 1 : 0)
#define pr_debug(...) do {} while (0)
/* LE byte access: the firmware/GPU view, the same on every host */
static void put16(void *p, unsigned o, u16 v) { u8 *b = (u8 *)p + o; b[0] = v; b[1] = v >> 8; }
static void put32(void *p, unsigned o, u32 v) { put16(p, o, v); put16(p, o + 2, v >> 16); }
static u16 get16(const void *p, unsigned o) { const u8 *b = (const u8 *)p + o; return b[0] | b[1] << 8; }
static void dump(const char *tag, const void *p, unsigned n)
{ const u8 *b = p; printf("%s:", tag); for (unsigned i = 0; i < n; i++) printf("%s%02x", i % 4 ? "" : " ", b[i]); printf("\n"); }
'''

ATOM_SHIM = r'''
#include "atom-types.h"
#include "atombios.h"
struct amdgpu_device { struct { void *atom_context; } mode_info; };
struct vdep_entry { u32 clk; u16 v; };
struct vdep { unsigned count; struct vdep_entry entries[4]; };
struct pp_hwmgr { struct amdgpu_device *adev; struct { struct vdep *vddc_dependency_on_sclk; } dyn_state; };
#define PP_INIT_CALL(h, x) (x)
#define PP_ASSERT_WITH_CODE(c, m, code) do { if (!(c)) { code; } } while (0)
/* 64 KiB + slack: a byte-swapped u16 offset still lands inside, like a real VBIOS image */
static u8 blob_prof[65536 + 512], blob_gfx[65536 + 512];
static u8 seen[64];
static void *smu_atom_get_data_table(void *a, u32 ix, u16 *s, u8 *f, u8 *c)
{
	(void)a; (void)s; (void)f; (void)c;
	if (ix == GetIndexIntoMasterTable(DATA, ASIC_ProfilingInfo)) return blob_prof;
	if (ix == GetIndexIntoMasterTable(DATA, GFX_Info)) return blob_gfx;
	return NULL;
}
/* VBIOS stand-in: records the parameter bytes it was handed and answers in LE */
static int amdgpu_atom_execute_table(void *ctx, int idx, uint32_t *params, int size)
{
	(void)ctx;
	memcpy(seen, params, size < 64 ? size : 64);
	if (idx == GetIndexIntoMasterTable(COMMAND, SetVoltage))
		put16(params, offsetof(SET_VOLTAGE_PARAMETERS_V1_3, usVoltageLevel), 0x0123);
	if (idx == GetIndexIntoMasterTable(COMMAND, GetVoltageInfo)) {
		u16 id = get16(params, offsetof(GET_VOLTAGE_INFO_INPUT_PARAMETER_V1_2, usVoltageLevel));
		put16(params, offsetof(GET_EVV_VOLTAGE_INFO_OUTPUT_PARAMETER_V1_2, usVoltageLevel),
		      id == 0xff01 ? 1150 : 7);
	}
	return 0;
}
'''

ATOM_MAIN = r'''
int main(void)
{
	struct amdgpu_device adev = {0};
	struct vdep dep = { 1, { { 50000, 0xff01 } } };
	struct pp_hwmgr h = { &adev, { &dep } };
	typedef ATOM_ASIC_PROFILING_INFO_V2_1 P;
	unsigned base = sizeof(P), o;
	u16 vddc, vddci, v;

	/* ASIC_ProfilingInfo v2.1: 3 leakage bins, 2 VDDC and 2 VDDCI virtual ids */
	put16(blob_prof, offsetof(P, asHeader.usStructureSize), sizeof(P));
	blob_prof[offsetof(P, asHeader.ucTableFormatRevision)] = 2;
	blob_prof[offsetof(P, asHeader.ucTableContentRevision)] = 1;
	blob_prof[offsetof(P, ucLeakageBinNum)] = 3;
	blob_prof[offsetof(P, ucElbVDDC_Num)] = 2;
	blob_prof[offsetof(P, ucElbVDDCI_Num)] = 2;
	o = base;
	put16(blob_prof, offsetof(P, usLeakageBinArrayOffset), o);
	for (int j = 0; j < 3; j++) put16(blob_prof, o + 2 * j, 100 * (j + 1));
	o += 6; put16(blob_prof, offsetof(P, usElbVDDC_IdArrayOffset), o);
	put16(blob_prof, o, 0xff01); put16(blob_prof, o + 2, 0xff02);
	o += 4; put16(blob_prof, offsetof(P, usElbVDDC_LevelArrayOffset), o);
	for (int k = 0; k < 6; k++) put16(blob_prof, o + 2 * k, 900 + k * 10);
	o += 12; put16(blob_prof, offsetof(P, usElbVDDCI_IdArrayOffset), o);
	put16(blob_prof, o, 0xff01); put16(blob_prof, o + 2, 0xff02);
	o += 4; put16(blob_prof, offsetof(P, usElbVDDCI_LevelArrayOffset), o);
	for (int k = 0; k < 6; k++) put16(blob_prof, o + 2 * k, 800 + k * 10);
	for (unsigned id = 0xff01; id <= 0xff02; id++)
		for (unsigned e = 50; e <= 250; e += 100) {
			int r = atomctrl_get_leakage_vddc_base_on_leakage(&h, &vddc, &vddci, id, e);
			printf("leakage id=%04x efuse=%u: r=%d vddc=%u vddci=%u\n", id, e, r, vddc, vddci);
		}

	int r = atomctrl_get_leakage_id_from_efuse(&h, &v);
	printf("leakage_id_from_efuse: r=%d id=0x%04x\n", r, v);

	r = atomctrl_get_voltage_evv(&h, 0xff01, &v);
	printf("voltage_evv(0xff01): r=%d mv=%u\n", r, v);
	dump("  GetVoltageInfo params as seen by VBIOS", seen, sizeof(GET_VOLTAGE_INFO_INPUT_PARAMETER_V1_2));

	/* GFX_Info v2.3: EDC hi/lo leakage threshold and table offsets, pattern-filled tail */
	for (unsigned i = 0; i < 512; i++) blob_gfx[i] = i * 7 + 3;
	put16(blob_gfx, offsetof(ATOM_GFX_INFO_V2_3, usHiLoLeakageThreshold), 0x1234);
	put16(blob_gfx, offsetof(ATOM_GFX_INFO_V2_3, usEdcDidtLoDpm7TableOffset), 0x40);
	put16(blob_gfx, offsetof(ATOM_GFX_INFO_V2_3, usEdcDidtHiDpm7TableOffset), 0x80);
	AtomCtrl_HiLoLeakageOffsetTable hl;
	r = atomctrl_get_edc_hilo_leakage_offset_table(&h, &hl);
	printf("edc_hilo: r=%d threshold=0x%04x lo=0x%04x hi=0x%04x\n", r,
	       hl.usHiLoLeakageThreshold, hl.usEdcDidtLoDpm7TableOffset, hl.usEdcDidtHiDpm7TableOffset);
	AtomCtrl_EDCLeakgeTable et;
	r = atomctrl_get_edc_leakage_table(&h, &et, hl.usEdcDidtLoDpm7TableOffset);
	printf("edc_leakage: r=%d DIDT_REG (values written to DIDT registers):", r);
	for (int i = 0; i < 24; i++) printf(" %08x", et.DIDT_REG[i]);
	printf("\n");
	return 0;
}
'''

UVD_SHIM = r'''
typedef struct { int counter; } atomic_t;
static int atomic_read(atomic_t *a) { return a->counter; }
static int atomic_cmpxchg(atomic_t *a, int o, int n) { int r = a->counter; if (r == o) a->counter = n; return r; }
struct drm_file { int id; };
struct amdgpu_bo { void *ptr; };
static int amdgpu_bo_kmap(struct amdgpu_bo *b, void **p) { *p = b->ptr; return 0; }
static void amdgpu_bo_kunmap(struct amdgpu_bo *b) { (void)b; }
struct amdgpu_device { void *dev; struct { unsigned max_handles; atomic_t handles[16];
	struct drm_file *filp[16]; bool use_ctx_buf; unsigned decode_image_width; } uvd; };
struct amdgpu_cs_parser { struct amdgpu_device *adev; struct drm_file *filp; };
'''

UVD_MAIN = r'''
static u32 msgbuf[256] __attribute__((aligned(64)));
static void lemsg(unsigned type, unsigned handle)
{
	memset(msgbuf, 0, sizeof(msgbuf));
	put32(msgbuf, 0, 0xde4); put32(msgbuf, 4, type); put32(msgbuf, 8, handle);
	put32(msgbuf, 16, 0);		/* stream_type: H264 */
	put32(msgbuf, 24, 1920); put32(msgbuf, 28, 1088);
	put32(msgbuf, 36, 0x02000000);	/* dpb_size, above the 1080p minimum */
	put32(msgbuf, 112, 1920);	/* pitch */
	put32(msgbuf, 244, 4 << 16);	/* msg[61] */
}
int main(void)
{
	struct amdgpu_device adev = {0};
	struct drm_file f = {1};
	struct amdgpu_cs_parser p = { &adev, &f };
	struct amdgpu_bo bo = { msgbuf };
	struct amdgpu_uvd_cs_ctx ctx;
	adev.uvd.max_handles = 16;
	memset(&ctx, 0, sizeof(ctx));
	static unsigned sizes[16];
	ctx.parser = &p;
	ctx.buf_sizes = sizes;
	static const char *what[] = { "create", "decode", "destroy" };
	for (unsigned t = 0; t < 3; t++) {
		lemsg(t, 0x1234);
		memset(sizes, 0, sizeof(sizes));
		long r = amdgpu_uvd_cs_msg(&ctx, &bo, 0);
		printf("%s msg: r=%ld handles[0]=0x%08x buf_sizes:", what[t], r,
		       (u32)adev.uvd.handles[0].counter);
		for (unsigned i = 0; i < 16; i++)
			printf(" %u", sizes[i]);
		printf("\n");
	}
	return 0;
}
'''

ENC_SHIM = r'''
/* Polaris11 UVD_ENC ring policy (patch 0023): software LE on a big-endian host */
struct amdgpu_ring { void *adev; };
#ifdef __BIG_ENDIAN
static bool amdgpu_ring_uses_sw_le(struct amdgpu_ring *r) { (void)r; return true; }
#else
static bool amdgpu_ring_uses_sw_le(struct amdgpu_ring *r) { (void)r; return false; }
#endif
struct dma_fence { int x; };
struct amdgpu_bo { u64 gpu; };
struct amdgpu_ib { u32 *ptr; unsigned length_dw; };
struct amdgpu_job { struct amdgpu_ib ibs[1]; };
#define AMDGPU_IB_POOL_DIRECT 0
#define AMDGPU_KERNEL_JOB_ID_VCN_RING_TEST 0
static u32 ibmem[64]; static struct amdgpu_job thejob; static struct dma_fence fence;
static u8 submitted[256]; static unsigned submitted_len;
static int amdgpu_job_alloc_with_ib(void *a, void *b, void *c, unsigned size, int pool,
				    struct amdgpu_job **job, int id)
{ (void)a; (void)b; (void)c; (void)size; (void)pool; (void)id;
  memset(ibmem, 0xee, sizeof(ibmem)); thejob.ibs[0].ptr = ibmem; *job = &thejob; return 0; }
static u64 amdgpu_bo_gpu_offset(struct amdgpu_bo *bo) { return bo->gpu; }
static int amdgpu_job_submit_direct(struct amdgpu_job *job, struct amdgpu_ring *ring, struct dma_fence **f)
{ (void)ring; submitted_len = 16 * 4; memcpy(submitted, job->ibs[0].ptr, submitted_len); *f = &fence; return 0; }
static void amdgpu_job_free(struct amdgpu_job *job) { (void)job; }
static struct dma_fence *dma_fence_get(struct dma_fence *f) { return f; }
static void dma_fence_put(struct dma_fence *f) { (void)f; }
'''

ENC_MAIN = r'''
int main(void)
{
	struct amdgpu_ring ring = {0};
	struct amdgpu_bo bo = { 0x0000001234567000ull };
	struct dma_fence *f;
	int r = uvd_v6_0_enc_get_create_msg(&ring, 0xabcd, &bo, &f);
	printf("enc create r=%d\n", r);
	dump("  create IB bytes as fetched by the encoder", submitted, submitted_len);
	r = uvd_v6_0_enc_get_destroy_msg(&ring, 0xabcd, &bo, &f);
	printf("enc destroy r=%d\n", r);
	dump("  destroy IB bytes as fetched by the encoder", submitted, submitted_len);
	return 0;
}
'''


def atom_src(tree):
    c = (tree / AMD / 'pm/powerplay/hwmgr/ppatomctrl.c').read_text()
    h = (tree / AMD / 'pm/powerplay/hwmgr/ppatomctrl.h').read_text()
    types = ''.join(span(h, s) + '\n' for s in
                    ('struct _AtomCtrl_HiLoLeakageOffsetTable', 'struct _AtomCtrl_EDCLeakgeTable'))
    types += 'typedef struct _AtomCtrl_HiLoLeakageOffsetTable AtomCtrl_HiLoLeakageOffsetTable;\n'
    types += 'typedef struct _AtomCtrl_EDCLeakgeTable AtomCtrl_EDCLeakgeTable;\n'
    fns = [span(c, s) for s in (
        'int atomctrl_get_leakage_vddc_base_on_leakage(', 'int atomctrl_get_leakage_id_from_efuse(',
        'int atomctrl_get_voltage_evv(', 'int atomctrl_get_edc_hilo_leakage_offset_table(',
        'static AtomCtrl_EDCLeakgeTable *get_edc_leakage_table(', 'int atomctrl_get_edc_leakage_table(')]
    return BASE + ATOM_SHIM + types + '\n\n'.join(fns) + ATOM_MAIN


def uvd_src(tree):
    c = (tree / AMD / 'amdgpu/amdgpu_uvd.c').read_text()
    fns = [span(c, 'struct amdgpu_uvd_cs_ctx {'),
           span(c, 'static int amdgpu_uvd_cs_msg_decode('), span(c, 'static int amdgpu_uvd_cs_msg(')]
    return BASE + UVD_SHIM + '\n\n'.join(fns) + UVD_MAIN


def enc_src(tree):
    c = (tree / AMD / 'amdgpu/uvd_v6_0.c').read_text()
    fns = [span(c, s) for s in ('static void uvd_v6_0_enc_encode_ib(',
                                'static int uvd_v6_0_enc_get_create_msg(',
                                'static int uvd_v6_0_enc_get_destroy_msg(')]
    return BASE + ENC_SHIM + '\n\n'.join(f for f in fns if f) + ENC_MAIN


def run(name, gen):
    out = {}
    for ver, tree in (('old', OLD), ('new', NEW)):
        src = W / f'{name}-{ver}.c'
        src.write_text(gen(tree))
        for arch, cc, runner in (('x86', 'gcc', []), ('ppc', 'powerpc-linux-gnu-gcc', ['qemu-ppc'])):
            exe = W / f'{name}-{ver}-{arch}'
            c = subprocess.run([cc, '-O2', '-static', '-nostdlib', '-ffreestanding', '-fno-builtin',
                                '-fno-stack-protector', '-fno-pie', '-no-pie', '-Wall', '-Wno-unused-function',
                                '-Wno-builtin-declaration-mismatch'] + (['-mstackrealign'] if arch == 'x86' else []) + [
                                '-Wno-address-of-packed-member', '-Wno-unused-variable',
                                f'-I{tree / AMD / "include"}', str(src), '-o', str(exe), '-lgcc'],
                               capture_output=True, text=True)
            if c.returncode:
                raise SystemExit(f'{name}-{ver}-{arch} compile failed:\n{c.stderr}')
            if c.stderr.strip():
                (W / f'{name}-{ver}-{arch}-compile.log').write_text(c.stderr)
            p = subprocess.run(runner + [str(exe)], capture_output=True, text=True)
            o = p.stdout + (f'[exit {p.returncode}]\n' if p.returncode else '')
            (W / f'{name}-{ver}-{arch}.log').write_text(o)
            out[f'{ver}-{arch}'] = o
    x86 = out['old-x86']
    verdict = {
        'x86_unchanged': out['new-x86'] == x86,
        'new_ppc_matches_x86': out['new-ppc'] == x86,
        'old_ppc_differs': out['old-ppc'] != x86,
    }
    verdict['status'] = 'PASS' if all(verdict.values()) else 'FAIL'
    return verdict


results = {n: run(n, g) for n, g in (('atom', atom_src), ('uvd-msg', uvd_src), ('uvd-enc', enc_src))}
results['gpu_accessed'] = False
(W / 'receipt.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
sys.exit(0 if all(r['status'] == 'PASS' for k, r in results.items() if isinstance(r, dict)) else 1)
