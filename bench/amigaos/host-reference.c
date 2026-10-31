/* SPDX-License-Identifier: MIT
 * Host-only IEEE float reference, NOT the target's integer soft-fp backend.
 */
#include "arithmetic.h"
typedef union { float f; u32 u; } bits;
#define OP(name, operation) \
 __attribute__((noinline)) u32 name(u32 a, u32 b) { \
  bits x={.u=a},y={.u=b},z; z.f=x.f operation y.f; return z.u; }
OP(soft_add, +)
OP(soft_sub, -)
OP(soft_mul, *)
u32 spe_add(u32 a,u32 b){return soft_add(a,b);}
u32 spe_sub(u32 a,u32 b){return soft_sub(a,b);}
u32 spe_mul(u32 a,u32 b){return soft_mul(a,b);}
