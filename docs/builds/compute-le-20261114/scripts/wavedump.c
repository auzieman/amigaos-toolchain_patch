/* Dump every live shader wave on an amdgpu GFX8 device via debugfs.
 * Usage: wavedump [dri-index]   (prints one line per wave with STATUS.VALID set,
 * then the first 32 SGPRs of the first live wave). Polaris11: 2 SE, 1 SH. */
#define _FILE_OFFSET_BITS 64
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

static const char *names[] = { "type", "STATUS", "PC_LO", "PC_HI", "EXEC_LO", "EXEC_HI", "HW_ID",
   "INST0", "INST1", "GPR_ALLOC", "LDS_ALLOC", "TRAPSTS", "IB_STS", "TBA_LO", "TBA_HI",
   "TMA_LO", "TMA_HI", "IB_DBG0", "M0", "MODE" };
#define NF 20

int main(int argc, char **argv)
{
   const char *dri = argc > 1 ? argv[1] : "0";
   char path[128];
   snprintf(path, sizeof path, "/sys/kernel/debug/dri/%s/amdgpu_wave", dri);
   int fw = open(path, O_RDONLY);
   snprintf(path, sizeof path, "/sys/kernel/debug/dri/%s/amdgpu_gpr", dri);
   int fg = open(path, O_RDONLY);
   if (fw < 0) { perror("amdgpu_wave"); return 2; }
   int live = 0, first = 1;
   for (uint64_t se = 0; se < 2; se++)
      for (uint64_t cu = 0; cu < 16; cu++)
         for (uint64_t simd = 0; simd < 4; simd++)
            for (uint64_t wave = 0; wave < 10; wave++) {
               uint32_t d[NF] = {0};
               off_t pos = (off_t)((se << 7) | (cu << 23) | (wave << 31) | (simd << 37));
               ssize_t n = pread(fw, d, sizeof d, pos);
               if (n < 8) continue;
               if (!(d[1] & (1u << 16))) continue;   /* SQ_WAVE_STATUS.VALID */
               live++;
               printf("se%llu cu%llu simd%llu wave%llu:", (unsigned long long)se,
                      (unsigned long long)cu, (unsigned long long)simd, (unsigned long long)wave);
               for (int i = 1; i < n / 4 && i < NF; i++) printf(" %s=%08x", names[i], d[i]);
               printf("\n");
               if (first && fg >= 0) {
                  first = 0;
                  uint32_t s[64] = {0};
                  off_t gp = (off_t)((se << 12) | (cu << 28) | (wave << 36) | (simd << 44) | (1ULL << 60));
                  ssize_t m = pread(fg, s, sizeof s, gp);
                  printf("  sgprs(%zd bytes):", m);
                  for (int i = 0; i < m / 4; i++) printf("%s%08x", i % 8 ? " " : "\n   ", s[i]);
                  printf("\n");
               }
            }
   printf("live_waves=%d\n", live);
   return 0;
}
