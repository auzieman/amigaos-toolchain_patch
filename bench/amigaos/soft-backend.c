/* SPDX-License-Identifier: MIT
 * Integer-only boundary to separately compiled GNU soft-fp helpers.
 * Compile this file and helpers with the same -msoft-float ABI.
 */
#include "arithmetic.h"
extern float tabor_softfp_add(float, float);
extern float tabor_softfp_sub(float, float);
extern float tabor_softfp_mul(float, float);
typedef union { float f; u32 u; } bits;
#define OP(name, helper) \
 __attribute__((noinline)) u32 name(u32 a, u32 b) { \
  bits x = {.u=a}, y = {.u=b}, z; z.f=helper(x.f,y.f); return z.u; }
OP(soft_add, tabor_softfp_add)
OP(soft_sub, tabor_softfp_sub)
OP(soft_mul, tabor_softfp_mul)
