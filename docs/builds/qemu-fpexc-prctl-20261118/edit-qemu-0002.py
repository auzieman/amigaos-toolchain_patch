#!/usr/bin/env python3
"""#39: qemu linux-user implements PR_GET_FPEXC/PR_SET_FPEXC for PowerPC SPE.

Usage: edit-qemu-0002.py <qemu source dir>   (edits in place; fails if an anchor is missing)

The kernel (arch/powerpc/kernel/process.c set_fpexc_mode/get_fpexc_mode) keeps a per-thread
thread.fpexc_mode: PR_FP_EXC_SW_ENABLE plus the enabled exceptions on an SPE CPU, or the
classic MSR[FE0,FE1] mode bits. It starts as MSR_FE0 | MSR_FE1 on 32-bit, is copied to new
threads, and is not reset by exec. qemu answered both prctls with EINVAL, so glibc's e500
fegetenv left its environment word unwritten and a later fesetenv loaded stack garbage into
SPEFSCR.
"""
import sys
from pathlib import Path

root = Path(sys.argv[1])


def edit(rel, old, new):
    p = root / rel
    s = p.read_text()
    if s.count(old) != 1:
        sys.exit(f"{rel}: anchor not found exactly once")
    p.write_text(s.replace(old, new))


edit("linux-user/qemu.h",
     """    abi_ulong child_tidptr;
#ifdef TARGET_M68K
""",
     """    abi_ulong child_tidptr;
#ifdef TARGET_PPC
    /* PR_SET_FPEXC mode, kept as the kernel keeps thread.fpexc_mode. */
    uint32_t ppc_fpexc_mode;
#endif
#ifdef TARGET_M68K
""")

edit("linux-user/main.c",
     """    ts->used = 1;
    ts->sigaltstack_used = (struct target_sigaltstack) {
""",
     """    ts->used = 1;
#if defined(TARGET_PPC) && !defined(TARGET_PPC64)
    /* The 32-bit kernel's INIT_THREAD: MSR_FE0 | MSR_FE1, PR_GET_FPEXC gives 3. */
    ts->ppc_fpexc_mode = (1u << MSR_FE0) | (1u << MSR_FE1);
#endif
    ts->sigaltstack_used = (struct target_sigaltstack) {
""")

edit("linux-user/syscall.c",
     """        ts = g_new0(TaskState, 1);
        init_task_state(ts);
""",
     """        ts = g_new0(TaskState, 1);
        init_task_state(ts);
#ifdef TARGET_PPC
        /* The kernel copies thread.fpexc_mode to the new thread. */
        ts->ppc_fpexc_mode = parent_ts->ppc_fpexc_mode;
#endif
""")

edit("linux-user/syscall.c",
     """#ifndef do_prctl_get_fp_mode
#define do_prctl_get_fp_mode do_prctl_inval0
#endif
""",
     """#ifndef do_prctl_get_fp_mode
#define do_prctl_get_fp_mode do_prctl_inval0
#endif
#ifndef do_prctl_get_fpexc
#define do_prctl_get_fpexc do_prctl_inval1
#endif
#ifndef do_prctl_set_fpexc
#define do_prctl_set_fpexc do_prctl_inval1
#endif
""")

edit("linux-user/syscall.c",
     """    case PR_GET_FPEXC:
    case PR_SET_FPEXC:
        /* Was used for SPE on PowerPC. */
        return -TARGET_EINVAL;
""",
     """    case PR_GET_FPEXC:
        return do_prctl_get_fpexc(env, arg2);
    case PR_SET_FPEXC:
        return do_prctl_set_fpexc(env, arg2);
""")

edit("linux-user/ppc/target_prctl.h",
     """/* No special prctl support required. */
""",
     """/*
 * PowerPC specific prctl functions for linux-user
 *
 * SPDX-License-Identifier: GPL-2.0-or-later
 */
#ifndef PPC_TARGET_PRCTL_H
#define PPC_TARGET_PRCTL_H

/*
 * PR_GET_FPEXC/PR_SET_FPEXC as arch/powerpc/kernel/process.c implements them on an SPE
 * CPU. glibc's e500 fenv code saves and restores the environment through them. Only the
 * mode is kept: qemu's SPE arithmetic gives IEEE results directly, so there are no kernel
 * fix-ups or SIGFPE deliveries for the mode to steer. Other CPUs keep the old EINVAL.
 */
#define PPC_PR_FP_ALL_EXCEPT (PR_FP_EXC_DIV | PR_FP_EXC_OVF | PR_FP_EXC_UND | \\
                              PR_FP_EXC_RES | PR_FP_EXC_INV)

static uint32_t ppc_pack_fe01(uint32_t mode)
{
    return ((mode << 10) & (1u << MSR_FE0)) | ((mode << 8) & (1u << MSR_FE1));
}

static uint32_t ppc_unpack_fe01(uint32_t bits)
{
    return ((bits & (1u << MSR_FE0)) >> 10) | ((bits & (1u << MSR_FE1)) >> 8);
}

static abi_long do_prctl_get_fpexc(CPUArchState *env, abi_long arg2)
{
    TaskState *ts = get_task_state(env_cpu(env));
    uint32_t val;

    if (!(env->insns_flags & PPC_SPE)) {
        return -TARGET_EINVAL;
    }
    if (ts->ppc_fpexc_mode & PR_FP_EXC_SW_ENABLE) {
        val = ts->ppc_fpexc_mode;
    } else {
        val = ppc_unpack_fe01(ts->ppc_fpexc_mode);
    }
    return put_user_u32(val, arg2);
}
#define do_prctl_get_fpexc do_prctl_get_fpexc

static abi_long do_prctl_set_fpexc(CPUArchState *env, abi_long arg2)
{
    TaskState *ts = get_task_state(env_cpu(env));
    uint32_t val = arg2;

    if (!(env->insns_flags & PPC_SPE)) {
        return -TARGET_EINVAL;
    }
    if (val & PR_FP_EXC_SW_ENABLE) {
        ts->ppc_fpexc_mode = val & (PR_FP_EXC_SW_ENABLE | PPC_PR_FP_ALL_EXCEPT);
        return 0;
    }
    if (val > PR_FP_EXC_PRECISE) {
        return -TARGET_EINVAL;
    }
    ts->ppc_fpexc_mode = ppc_pack_fe01(val);
    return 0;
}
#define do_prctl_set_fpexc do_prctl_set_fpexc

#endif /* PPC_TARGET_PRCTL_H */
""")
print("edited")
