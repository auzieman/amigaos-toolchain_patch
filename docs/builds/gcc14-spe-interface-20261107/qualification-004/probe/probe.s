	.file	"gcc14-spe-freestanding.c"
	.section	".text"
	.align 2
	.type	clobber_callers, @function
clobber_callers:
	lis 10,.LANCHOR0@ha
	lwz 9,.LANCHOR0@l(10)
	addi 9,9,1
	stw 9,.LANCHOR0@l(10)
	blr
	.size	clobber_callers, .-clobber_callers
	.align 2
	.type	probe_preserved, @function
probe_preserved:
	stwu 1,-32(1)
	mflr 0
	stw 3,16(1)
	stw 4,20(1)
	evstdd 31,24(1)
	stw 0,36(1)
	evldd 9,16(1)
	efdadd 31,9,9
	bl clobber_callers
	lis 9,.LC0@ha
	lwz 0,36(1)
	la 9,.LC0@l(9)
	lwz 10,8(1)
	evldd 9,0(9)
	lwz 11,12(1)
	mtlr 0
	efdadd 9,31,9
	evldd 31,24(1)
	evmergehi 10,9,9
	mr 11,9
	stw 10,8(1)
	mr 3,10
	stw 11,12(1)
	mr 4,11
	addi 1,1,32
	blr
	.size	probe_preserved, .-probe_preserved
	.align 2
	.type	finish, @function
finish:
	stwu 1,-16(1)
	cmpwi 7,3,0
	lis 4,.LANCHOR1@ha
	stw 31,12(1)
	mr 31,3
	beq- 7,.L8
	la 4,.LANCHOR1@l(4)
	li 5,28
.L6:
	li 0,4
	li 3,1
#APP
 # 53 "/recipe/bench/gcc14-spe-freestanding.c" 1
	sc
 # 0 "" 2
#NO_APP
	li 0,1
	mr 3,31
#APP
 # 65 "/recipe/bench/gcc14-spe-freestanding.c" 1
	sc
 # 0 "" 2
#NO_APP
.L7:
	b .L7
.L8:
	la 4,.LANCHOR1@l(4)
	li 5,75
	addi 4,4,32
	b .L6
	.size	finish, .-finish
	.align 2
	.type	probe_varargs.constprop.0, @function
probe_varargs.constprop.0:
	stwu 1,-64(1)
	li 11,1
	stw 5,32(1)
	lis 5,.LC2@ha
	stw 6,36(1)
	la 5,.LC2@l(5)
	stw 7,40(1)
	addi 6,1,72
	stw 8,44(1)
	addi 7,1,24
	evldd 3,0(5)
	evldd 8,32(1)
	evldd 5,40(1)
	stw 9,48(1)
	efdadd 8,8,3
	lwz 9,56(1)
	efdadd 8,8,5
	stw 10,52(1)
	lwz 10,60(1)
	evmergehi 9,8,8
	mr 10,8
	stw 4,28(1)
	mr 3,9
	stw 9,56(1)
	mr 4,10
	stw 10,60(1)
	stw 7,16(1)
	stb 11,8(1)
	stw 6,12(1)
	addi 1,1,64
	blr
	.size	probe_varargs.constprop.0, .-probe_varargs.constprop.0
	.align 2
	.globl probe_single
	.type	probe_single, @function
probe_single:
	efsadd 3,3,4
	blr
	.size	probe_single, .-probe_single
	.align 2
	.globl probe_double
	.type	probe_double, @function
probe_double:
	stwu 1,-32(1)
	stw 3,16(1)
	stw 4,20(1)
	stw 5,24(1)
	stw 6,28(1)
	evldd 9,16(1)
	lwz 11,12(1)
	evldd 10,24(1)
	efdadd 9,9,10
	lwz 10,8(1)
	evmergehi 10,9,9
	mr 11,9
	stw 10,8(1)
	mr 3,10
	stw 11,12(1)
	mr 4,11
	addi 1,1,32
	blr
	.size	probe_double, .-probe_double
	.align 2
	.globl _start
	.type	_start, @function
_start:
	stwu 1,-160(1)
	mflr 0
	lis 9,.LANCHOR2@ha
	lwz 3,.LANCHOR2@l(9)
	stw 0,164(1)
	evstdd 31,152(1)
	la 31,.LANCHOR2@l(9)
	evstdd 30,144(1)
	lwz 4,4(31)
	bl probe_single
	lis 9,0x4070
	cmpw 7,9,3
	bne- 7,.L35
	evldd 10,8(31)
	lis 30,0x400e
	evldd 9,16(31)
	lwz 7,112(1)
	lwz 8,116(1)
	evmergehi 7,10,10
	mr 8,10
	lwz 11,108(1)
	mr 3,7
	lwz 10,104(1)
	evmergehi 10,9,9
	mr 11,9
	mr 4,8
	stw 7,112(1)
	mr 5,10
	stw 8,116(1)
	mr 6,11
	stw 10,104(1)
	stw 11,108(1)
	bl probe_double
	cmpw 7,3,30
	bne- 7,.L21
	cmpwi 7,4,0
	beq- 7,.L22
.L21:
	li 3,2
	bl finish
.L35:
	li 3,1
	bl finish
.L22:
	evldd 10,8(31)
	li 3,2
	evldd 9,16(31)
	lwz 7,128(1)
	lwz 8,132(1)
	evmergehi 7,10,10
	mr 8,10
	lwz 11,124(1)
	mr 5,7
	lwz 10,120(1)
	evmergehi 10,9,9
	mr 11,9
	stw 7,128(1)
	mr 6,8
	stw 8,132(1)
	mr 7,10
	mr 8,11
	stw 10,120(1)
	stw 11,124(1)
	crxor 6,6,6
	bl probe_varargs.constprop.0
	cmpw 7,3,30
	bne- 7,.L23
	cmpwi 7,4,0
	bne+ 7,.L23
	evldd 9,8(31)
	lwz 10,136(1)
	lwz 11,140(1)
	evmergehi 10,9,9
	mr 11,9
	mr 3,10
	stw 10,136(1)
	mr 4,11
	stw 11,140(1)
	bl probe_preserved
	lis 9,0x400a
	cmpw 7,3,9
	bne- 7,.L25
	cmpwi 7,4,0
	mr 30,4
	bne- 7,.L25
	lis 9,.LANCHOR0@ha
	lwz 9,.LANCHOR0@l(9)
	cmplwi 7,9,1
	beq- 7,.L29
.L25:
	li 3,4
	bl finish
.L23:
	li 3,3
	bl finish
.L29:
	li 10,8
	li 9,0
	addi 4,1,72
	addi 5,1,40
	mtctr 10
.L26:
	lwz 8,0(31)
	lwz 10,4(31)
	stwx 8,4,9
	stwx 10,5,9
	addi 9,9,4
	bdnz .L26
	addi 31,1,8
	li 6,8
	mr 3,31
	bl probe_array
	subfic 9,30,8
	lis 10,0x4070
	mtctr 9
.L28:
	slwi 9,30,2
	lwzx 9,31,9
	cmpw 7,9,10
	bne- 7,.L36
	addi 30,30,1
	bdnz .L28
	li 3,0
	bl finish
.L36:
	li 3,5
	bl finish
	.size	_start, .-_start
	.section	.rodata.cst8,"aM",@progbits,8
	.align 3
.LC0:
	.long	1070596096
	.long	0
	.align 3
.LC2:
	.long	0
	.long	0
	.section	.rodata
	.align 2
	.set	.LANCHOR1,. + 0
	.type	fail.1, @object
	.size	fail.1, 29
fail.1:
	.string	"GCC14_SPE_FREESTANDING_FAIL\n"
	.zero	3
	.type	pass.0, @object
	.size	pass.0, 76
pass.0:
	.string	"GCC14_SPE_FREESTANDING_PASS single double varargs preserved optimized-loop\n"
	.section	".data"
	.align 3
	.set	.LANCHOR2,. + 0
	.type	single_a, @object
	.size	single_a, 4
single_a:
	.long	1069547520
	.type	single_b, @object
	.size	single_b, 4
single_b:
	.long	1074790400
	.type	double_a, @object
	.size	double_a, 8
double_a:
	.long	1073217536
	.long	0
	.type	double_b, @object
	.size	double_b, 8
double_b:
	.long	1073872896
	.long	0
	.section	".bss"
	.align 2
	.set	.LANCHOR0,. + 0
	.type	touched, @object
	.size	touched, 4
touched:
	.zero	4
	.ident	"GCC: (GNU) 14.2.0"
	.gnu_attribute 4, 1
	.section	.note.GNU-stack,"",@progbits
