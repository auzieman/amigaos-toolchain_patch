/* Minimal e500v2 arithmetic test, Linux PPC32 syscalls, no libc dependency.
 * SPDX-License-Identifier: MIT
 * This checks selected instructions only, not the complete SPE ABI or fenv.
 */
.section .text
.globl _start
_start:
    /* Single precision: 1.5 + 2.25 = 3.75. */
    lis 4,0x3fc0
    lis 5,0x4010
    efsadd 3,4,5
    lis 6,0x4070
    cmpw 3,6
    bne failed
    /* Double precision operands occupy the full 64-bit SPE registers. */
    lis 6,operands@ha
    addi 6,6,operands@l
    evldd 4,0(6)
    evldd 5,8(6)
    efdadd 3,4,5
    lis 6,result@ha
    addi 6,6,result@l
    evstdd 3,0(6)
    lwz 3,0(6)
    lis 4,0x400e
    cmpw 3,4
    bne failed
    lwz 3,4(6)
    cmpwi 3,0
    bne failed
    lis 4,passed@ha
    addi 4,4,passed@l
    li 5,passed_end-passed
    b write_result
failed:
    lis 4,failure@ha
    addi 4,4,failure@l
    li 5,failure_end-failure
write_result:
    li 0,4
    li 3,1
    sc
1:  li 0,29
    sc
    b 1b
.section .rodata
.balign 8
operands:
    .long 0x3ff80000,0x00000000
    .long 0x40020000,0x00000000
passed:
    .ascii "SPE_SMOKE_PASS: efsadd + efdadd + evldd/evstdd known results verified.\nTABOR_QEMU_INIT_OK: selected SPE arithmetic passed; full ABI/glibc/GL not tested.\n"
passed_end:
failure:
    .ascii "SPE_SMOKE_FAIL: arithmetic result mismatch.\n"
failure_end:
.section .bss
.balign 8
result:
    .skip 8
.section .note.GNU-stack,"",@progbits
