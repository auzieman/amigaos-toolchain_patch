/* Freestanding Linux PPC32 init: no libc, FPU or SPE ABI dependency.
 * SPDX-License-Identifier: MIT
 */
.section .text
.globl _start
_start:
    li 0,4
    li 3,1
    lis 4,message@ha
    addi 4,4,message@l
    li 5,message_end-message
    sc
1:  li 0,29
    sc
    b 1b
.section .rodata
message:
    .ascii "TABOR_QEMU_INIT_OK: PPC32 freestanding userspace reached; SPE/glibc not tested.\n"
message_end:
