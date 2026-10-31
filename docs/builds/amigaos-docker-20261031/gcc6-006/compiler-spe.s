	.file	"compiler-spe.c"
	.section	".text"
	.align 2
	.globl addf
	.type	addf, @function
addf:
	efsadd 3,3,4
	blr
	.size	addf, .-addf
	.align 2
	.globl addd
	.type	addd, @function
addd:
	stwu 1,-32(1)
	evmergelo 9,3,4
	evmergelo 10,5,6
	mr 11,4
	efdadd 9,9,10
	mr 10,3
	evmergehi 10,9,9
	mr 11,9
	stw 5,16(1)
	mr 3,10
	stw 6,20(1)
	mr 4,11
	stw 10,8(1)
	stw 11,12(1)
	addi 1,1,32
	blr
	.size	addd, .-addd
	.ident	"GCC: (adtools build 6.4.0) 6.4.0"
	.gnu_attribute 4, 2
