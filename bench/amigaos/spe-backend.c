/* SPDX-License-Identifier: MIT */
#include "arithmetic.h"
#define OP(name, instruction) \
 __attribute__((noinline)) u32 name(u32 a, u32 b) { \
  u32 result; __asm__(instruction " %0,%1,%2":"=r"(result):"r"(a),"r"(b)); \
  return result; }
OP(spe_add, "efsadd")
OP(spe_sub, "efssub")
OP(spe_mul, "efsmul")
