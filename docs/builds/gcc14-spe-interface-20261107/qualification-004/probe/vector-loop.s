	.file	"gcc14-spe-vector.c"
	.section	".text"
	.align 2
	.globl probe_array
	.type	probe_array, @function
probe_array:
	cmpwi 7,6,0
	beqlr- 7
	addi 9,6,-1
	cmplwi 7,9,4
	ble- 7,.L3
	or 9,3,5
	or 9,4,9
	andi. 9,9,0x7
	bne- 0,.L3
	rlwinm 10,6,2,0,28
	addi 10,10,-8
	li 9,0
	srwi 10,10,3
	addi 10,10,1
	mtctr 10
.L4:
	evlddx 10,4,9
	evlddx 8,5,9
	evfsadd 10,10,8
	evstddx 10,3,9
	addi 9,9,8
	bdnz .L4
	andi. 9,6,0x1
	beqlr- 0
	rlwinm 6,6,2,0,28
	lwzx 9,4,6
	lwzx 10,5,6
	efsadd 9,9,10
	stwx 9,3,6
	blr
.L3:
	slwi 9,6,2
	addi 4,4,-4
	addi 9,9,-4
	addi 5,5,-4
	srwi 9,9,2
	addi 3,3,-4
	addi 9,9,1
	mtctr 9
.L6:
	lwzu 9,4(4)
	lwzu 10,4(5)
	efsadd 9,9,10
	stwu 9,4(3)
	bdnz .L6
	blr
	.size	probe_array, .-probe_array
	.ident	"GCC: (GNU) 14.2.0"
	.section	.note.GNU-stack,"",@progbits
