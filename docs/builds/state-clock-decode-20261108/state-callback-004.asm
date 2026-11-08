
/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-004/output/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.o:     file format elf32-powerpc


Disassembly of section .text:

00009404 <smu7_get_pp_table_entry_callback_func_v1>:
    9404:	94 21 ff a0 	stwu    r1,-96(r1)
    9408:	7c 08 02 a6 	mflr    r0
    940c:	92 c1 00 38 	stw     r22,56(r1)
    9410:	93 21 00 44 	stw     r25,68(r1)
    9414:	93 41 00 48 	stw     r26,72(r1)
    9418:	93 61 00 4c 	stw     r27,76(r1)
    941c:	93 81 00 50 	stw     r28,80(r1)
    9420:	7c dc 33 78 	mr      r28,r6
    9424:	93 a1 00 54 	stw     r29,84(r1)
    9428:	7c 7d 1b 78 	mr      r29,r3
    942c:	93 c1 00 58 	stw     r30,88(r1)
    9430:	7c 9e 23 78 	mr      r30,r4
    9434:	93 e1 00 5c 	stw     r31,92(r1)
    9438:	7c bf 2b 78 	mr      r31,r5
    943c:	90 01 00 64 	stw     r0,100(r1)
    9440:	92 e1 00 3c 	stw     r23,60(r1)
    9444:	93 01 00 40 	stw     r24,64(r1)
    9448:	89 24 00 08 	lbz     r9,8(r4)
    944c:	89 1c 00 2e 	lbz     r8,46(r28)
    9450:	88 86 00 2d 	lbz     r4,45(r6)
    9454:	81 42 03 88 	lwz     r10,904(r2)
    9458:	91 41 00 2c 	stw     r10,44(r1)
    945c:	39 40 00 00 	li      r10,0
    9460:	88 bc 00 2b 	lbz     r5,43(r28)
    9464:	89 5c 00 2c 	lbz     r10,44(r28)
    9468:	38 c0 00 00 	li      r6,0
    946c:	83 03 01 74 	lwz     r24,372(r3)
    9470:	55 29 07 7e 	clrlwi  r9,r9,29
    9474:	90 ff 00 18 	stw     r7,24(r31)
    9478:	91 3f 00 14 	stw     r9,20(r31)
    947c:	50 88 40 2e 	rlwimi  r8,r4,8,0,23
    9480:	b0 df 00 20 	sth     r6,32(r31)
    9484:	50 aa 40 2e 	rlwimi  r10,r5,8,0,23
    9488:	55 07 44 2e 	rlwinm  r7,r8,8,16,23
    948c:	a2 ff 00 94 	lhz     r23,148(r31)
    9490:	55 19 c6 3e 	rlwinm  r25,r8,24,24,31
    9494:	55 5a c6 3e 	rlwinm  r26,r10,24,24,31
    9498:	55 48 44 2e 	rlwinm  r8,r10,8,16,23
    949c:	7f 39 3b 78 	or      r25,r25,r7
    94a0:	7f 5a 43 78 	or      r26,r26,r8
    94a4:	88 fe 00 0a 	lbz     r7,10(r30)
    94a8:	89 1e 00 0b 	lbz     r8,11(r30)
    94ac:	39 20 00 00 	li      r9,0
    94b0:	89 5e 00 0c 	lbz     r10,12(r30)
    94b4:	3b 77 00 01 	addi    r27,r23,1
    94b8:	54 e7 c0 0e 	slwi    r7,r7,24
    94bc:	55 08 80 1e 	slwi    r8,r8,16
    94c0:	7d 08 3b 78 	or      r8,r8,r7
    94c4:	55 4a 40 2e 	slwi    r10,r10,8
    94c8:	7d 4a 43 78 	or      r10,r10,r8
    94cc:	89 1e 00 0d 	lbz     r8,13(r30)
    94d0:	91 3f 00 28 	stw     r9,40(r31)
    94d4:	38 80 00 00 	li      r4,0
    94d8:	b1 3f 00 2c 	sth     r9,44(r31)
    94dc:	57 39 04 3e 	clrlwi  r25,r25,16
    94e0:	7d 08 53 78 	or      r8,r8,r10
    94e4:	55 0a c0 3e 	rotlwi  r10,r8,24
    94e8:	51 0a 42 1e 	rlwimi  r10,r8,8,8,15
    94ec:	57 5a 04 3e 	clrlwi  r26,r26,16
    94f0:	51 0a 46 3e 	rlwimi  r10,r8,8,24,31
    94f4:	7f 5a e2 14 	add     r26,r26,r28
    94f8:	55 4a 97 fe 	rlwinm  r10,r10,18,31,31
    94fc:	7e d9 e2 14 	add     r22,r25,r28
    9500:	99 5f 00 25 	stb     r10,37(r31)
    9504:	88 fe 00 0a 	lbz     r7,10(r30)
    9508:	89 1e 00 0b 	lbz     r8,11(r30)
    950c:	89 5e 00 0c 	lbz     r10,12(r30)
    9510:	54 e7 c0 0e 	slwi    r7,r7,24
    9514:	55 08 80 1e 	slwi    r8,r8,16
    9518:	7d 08 3b 78 	or      r8,r8,r7
    951c:	55 4a 40 2e 	slwi    r10,r10,8
    9520:	7d 4a 43 78 	or      r10,r10,r8
    9524:	89 1e 00 0d 	lbz     r8,13(r30)
    9528:	b3 7f 00 94 	sth     r27,148(r31)
    952c:	57 7b 04 3e 	clrlwi  r27,r27,16
    9530:	98 df 00 26 	stb     r6,38(r31)
    9534:	7d 08 53 78 	or      r8,r8,r10
    9538:	91 3f 00 74 	stw     r9,116(r31)
    953c:	55 0a c0 3e 	rotlwi  r10,r8,24
    9540:	91 3f 00 78 	stw     r9,120(r31)
    9544:	51 0a 42 1e 	rlwimi  r10,r8,8,8,15
    9548:	91 3f 00 48 	stw     r9,72(r31)
    954c:	51 0a 46 3e 	rlwimi  r10,r8,8,24,31
    9550:	91 3f 00 4c 	stw     r9,76(r31)
    9554:	55 4a 8f fe 	rlwinm  r10,r10,17,31,31
    9558:	99 5f 00 3c 	stb     r10,60(r31)
    955c:	48 00 00 01 	bl      955c <smu7_get_pp_table_entry_callback_func_v1+0x158>
    9560:	7c 1b 18 40 	cmplw   r27,r3
    9564:	40 80 07 08 	bge     9c6c <smu7_get_pp_table_entry_callback_func_v1+0x868>
    9568:	a0 ff 00 94 	lhz     r7,148(r31)
    956c:	81 3d 01 24 	lwz     r9,292(r29)
    9570:	54 e5 04 3e 	clrlwi  r5,r7,16
    9574:	7c 05 48 40 	cmplw   r5,r9
    9578:	40 80 06 c8 	bge     9c40 <smu7_get_pp_table_entry_callback_func_v1+0x83c>
    957c:	89 3e 00 03 	lbz     r9,3(r30)
    9580:	56 f7 04 3e 	clrlwi  r23,r23,16
    9584:	56 fb 08 3c 	slwi    r27,r23,1
    9588:	7f 7b ba 14 	add     r27,r27,r23
    958c:	1d 29 00 0d 	mulli   r9,r9,13
    9590:	57 66 10 3a 	slwi    r6,r27,2
    9594:	7c df 32 14 	add     r6,r31,r6
    9598:	7d 3a 4a 14 	add     r9,r26,r9
    959c:	88 69 00 09 	lbz     r3,9(r9)
    95a0:	89 09 00 0a 	lbz     r8,10(r9)
    95a4:	89 49 00 0b 	lbz     r10,11(r9)
    95a8:	88 89 00 0c 	lbz     r4,12(r9)
    95ac:	54 63 c0 0e 	slwi    r3,r3,24
    95b0:	55 08 80 1e 	slwi    r8,r8,16
    95b4:	55 49 40 2e 	slwi    r9,r10,8
    95b8:	7d 08 1b 78 	or      r8,r8,r3
    95bc:	39 46 00 9c 	addi    r10,r6,156
    95c0:	7d 29 43 78 	or      r9,r9,r8
    95c4:	7c 89 4b 78 	or      r9,r4,r9
    95c8:	7d 20 55 2c 	stwbrx  r9,0,r10
    95cc:	7d 3c c8 ae 	lbzx    r9,r28,r25
    95d0:	2c 09 00 00 	cmpwi   r9,0
    95d4:	41 82 00 ec 	beq     96c0 <smu7_get_pp_table_entry_callback_func_v1+0x2bc>
    95d8:	2c 09 00 01 	cmpwi   r9,1
    95dc:	41 82 03 bc 	beq     9998 <smu7_get_pp_table_entry_callback_func_v1+0x594>
    95e0:	81 18 08 28 	lwz     r8,2088(r24)
    95e4:	39 40 00 01 	li      r10,1
    95e8:	55 09 04 3e 	clrlwi  r9,r8,16
    95ec:	28 09 00 02 	cmplwi  r9,2
    95f0:	41 82 00 38 	beq     9628 <smu7_get_pp_table_entry_callback_func_v1+0x224>
    95f4:	28 09 00 04 	cmplwi  r9,4
    95f8:	39 40 00 02 	li      r10,2
    95fc:	41 82 00 2c 	beq     9628 <smu7_get_pp_table_entry_callback_func_v1+0x224>
    9600:	28 09 00 01 	cmplwi  r9,1
    9604:	39 40 00 00 	li      r10,0
    9608:	41 82 00 20 	beq     9628 <smu7_get_pp_table_entry_callback_func_v1+0x224>
    960c:	89 3e 00 04 	lbz     r9,4(r30)
    9610:	75 0a 00 04 	andis.  r10,r8,4
    9614:	7d 2a 4b 78 	mr      r10,r9
    9618:	40 82 03 18 	bne     9930 <smu7_get_pp_table_entry_callback_func_v1+0x52c>
    961c:	75 08 00 02 	andis.  r8,r8,2
    9620:	39 40 00 00 	li      r10,0
    9624:	40 82 03 18 	bne     993c <smu7_get_pp_table_entry_callback_func_v1+0x538>
    9628:	3f a0 00 00 	lis     r29,0
    962c:	3b bd 00 00 	addi    r29,r29,0
    9630:	57 69 10 3a 	slwi    r9,r27,2
    9634:	a1 1d 03 06 	lhz     r8,774(r29)
    9638:	7d 3f 4a 14 	add     r9,r31,r9
    963c:	b1 49 00 a4 	sth     r10,164(r9)
    9640:	3d 40 00 08 	lis     r10,8
    9644:	a0 9d 03 08 	lhz     r4,776(r29)
    9648:	a0 dd 03 0a 	lhz     r6,778(r29)
    964c:	b1 01 00 1c 	sth     r8,28(r1)
    9650:	a1 1d 03 0c 	lhz     r8,780(r29)
    9654:	81 38 08 2c 	lwz     r9,2092(r24)
    9658:	b0 81 00 1e 	sth     r4,30(r1)
    965c:	b0 c1 00 20 	sth     r6,32(r1)
    9660:	a0 9d 03 0e 	lhz     r4,782(r29)
    9664:	7c 09 50 00 	cmpw    r9,r10
    9668:	a0 dd 03 10 	lhz     r6,784(r29)
    966c:	b1 01 00 22 	sth     r8,34(r1)
    9670:	a1 1d 03 12 	lhz     r8,786(r29)
    9674:	8a fe 00 06 	lbz     r23,6(r30)
    9678:	b0 81 00 24 	sth     r4,36(r1)
    967c:	b0 c1 00 26 	sth     r6,38(r1)
    9680:	b1 01 00 28 	sth     r8,40(r1)
    9684:	41 82 03 b0 	beq     9a34 <smu7_get_pp_table_entry_callback_func_v1+0x630>
    9688:	7c 09 50 40 	cmplw   r9,r10
    968c:	41 81 00 74 	bgt     9700 <smu7_get_pp_table_entry_callback_func_v1+0x2fc>
    9690:	3d 40 00 02 	lis     r10,2
    9694:	7c 09 50 00 	cmpw    r9,r10
    9698:	41 82 03 94 	beq     9a2c <smu7_get_pp_table_entry_callback_func_v1+0x628>
    969c:	7c 09 50 40 	cmplw   r9,r10
    96a0:	41 81 02 74 	bgt     9914 <smu7_get_pp_table_entry_callback_func_v1+0x510>
    96a4:	2c 09 00 00 	cmpwi   r9,0
    96a8:	41 82 06 18 	beq     9cc0 <smu7_get_pp_table_entry_callback_func_v1+0x8bc>
    96ac:	3d 40 00 01 	lis     r10,1
    96b0:	7c 09 50 00 	cmpw    r9,r10
    96b4:	40 82 03 88 	bne     9a3c <smu7_get_pp_table_entry_callback_func_v1+0x638>
    96b8:	3a e0 00 01 	li      r23,1
    96bc:	48 00 00 6c 	b       9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    96c0:	89 3e 00 01 	lbz     r9,1(r30)
    96c4:	1d 29 00 0b 	mulli   r9,r9,11
    96c8:	7d 36 4a 14 	add     r9,r22,r9
    96cc:	88 69 00 05 	lbz     r3,5(r9)
    96d0:	89 09 00 06 	lbz     r8,6(r9)
    96d4:	89 49 00 07 	lbz     r10,7(r9)
    96d8:	88 89 00 08 	lbz     r4,8(r9)
    96dc:	54 63 c0 0e 	slwi    r3,r3,24
    96e0:	55 08 80 1e 	slwi    r8,r8,16
    96e4:	55 49 40 2e 	slwi    r9,r10,8
    96e8:	7d 08 1b 78 	or      r8,r8,r3
    96ec:	39 46 00 a0 	addi    r10,r6,160
    96f0:	7d 29 43 78 	or      r9,r9,r8
    96f4:	7c 89 4b 78 	or      r9,r4,r9
    96f8:	7d 20 55 2c 	stwbrx  r9,0,r10
    96fc:	4b ff fe e4 	b       95e0 <smu7_get_pp_table_entry_callback_func_v1+0x1dc>
    9700:	3d 40 00 20 	lis     r10,32
    9704:	7c 09 50 00 	cmpw    r9,r10
    9708:	41 82 03 84 	beq     9a8c <smu7_get_pp_table_entry_callback_func_v1+0x688>
    970c:	3d 40 00 40 	lis     r10,64
    9710:	7c 09 50 00 	cmpw    r9,r10
    9714:	41 82 02 14 	beq     9928 <smu7_get_pp_table_entry_callback_func_v1+0x524>
    9718:	3d 40 00 10 	lis     r10,16
    971c:	7c 09 50 00 	cmpw    r9,r10
    9720:	40 82 03 1c 	bne     9a3c <smu7_get_pp_table_entry_callback_func_v1+0x638>
    9724:	3a e0 00 0c 	li      r23,12
    9728:	57 7b 10 3a 	slwi    r27,r27,2
    972c:	38 e7 00 01 	addi    r7,r7,1
    9730:	7d 3f da 14 	add     r9,r31,r27
    9734:	54 bb 08 3c 	slwi    r27,r5,1
    9738:	b2 e9 00 a6 	sth     r23,166(r9)
    973c:	7f 7b 2a 14 	add     r27,r27,r5
    9740:	b0 ff 00 94 	sth     r7,148(r31)
    9744:	57 67 10 3a 	slwi    r7,r27,2
    9748:	7c ff 3a 14 	add     r7,r31,r7
    974c:	89 3e 00 02 	lbz     r9,2(r30)
    9750:	1d 29 00 0d 	mulli   r9,r9,13
    9754:	7d 3a 4a 14 	add     r9,r26,r9
    9758:	88 a9 00 09 	lbz     r5,9(r9)
    975c:	89 09 00 0a 	lbz     r8,10(r9)
    9760:	89 49 00 0b 	lbz     r10,11(r9)
    9764:	88 c9 00 0c 	lbz     r6,12(r9)
    9768:	54 a5 c0 0e 	slwi    r5,r5,24
    976c:	55 08 80 1e 	slwi    r8,r8,16
    9770:	55 49 40 2e 	slwi    r9,r10,8
    9774:	7d 08 2b 78 	or      r8,r8,r5
    9778:	39 47 00 9c 	addi    r10,r7,156
    977c:	7d 29 43 78 	or      r9,r9,r8
    9780:	7c c9 4b 78 	or      r9,r6,r9
    9784:	7d 20 55 2c 	stwbrx  r9,0,r10
    9788:	7d 3c c8 ae 	lbzx    r9,r28,r25
    978c:	2c 09 00 00 	cmpwi   r9,0
    9790:	40 82 01 c4 	bne     9954 <smu7_get_pp_table_entry_callback_func_v1+0x550>
    9794:	89 3e 00 00 	lbz     r9,0(r30)
    9798:	1d 29 00 0b 	mulli   r9,r9,11
    979c:	7d 36 4a 14 	add     r9,r22,r9
    97a0:	88 a9 00 05 	lbz     r5,5(r9)
    97a4:	89 09 00 06 	lbz     r8,6(r9)
    97a8:	89 49 00 07 	lbz     r10,7(r9)
    97ac:	88 c9 00 08 	lbz     r6,8(r9)
    97b0:	54 a5 c0 0e 	slwi    r5,r5,24
    97b4:	55 08 80 1e 	slwi    r8,r8,16
    97b8:	55 49 40 2e 	slwi    r9,r10,8
    97bc:	7d 08 2b 78 	or      r8,r8,r5
    97c0:	39 47 00 a0 	addi    r10,r7,160
    97c4:	7d 29 43 78 	or      r9,r9,r8
    97c8:	7c c9 4b 78 	or      r9,r6,r9
    97cc:	7d 20 55 2c 	stwbrx  r9,0,r10
    97d0:	81 18 08 28 	lwz     r8,2088(r24)
    97d4:	39 40 00 01 	li      r10,1
    97d8:	55 09 04 3e 	clrlwi  r9,r8,16
    97dc:	28 09 00 02 	cmplwi  r9,2
    97e0:	41 82 00 4c 	beq     982c <smu7_get_pp_table_entry_callback_func_v1+0x428>
    97e4:	28 09 00 04 	cmplwi  r9,4
    97e8:	39 40 00 02 	li      r10,2
    97ec:	41 82 00 40 	beq     982c <smu7_get_pp_table_entry_callback_func_v1+0x428>
    97f0:	28 09 00 01 	cmplwi  r9,1
    97f4:	39 40 00 00 	li      r10,0
    97f8:	41 82 00 34 	beq     982c <smu7_get_pp_table_entry_callback_func_v1+0x428>
    97fc:	89 3e 00 05 	lbz     r9,5(r30)
    9800:	75 0a 00 04 	andis.  r10,r8,4
    9804:	7d 2a 4b 78 	mr      r10,r9
    9808:	40 82 02 8c 	bne     9a94 <smu7_get_pp_table_entry_callback_func_v1+0x690>
    980c:	75 08 00 02 	andis.  r8,r8,2
    9810:	39 40 00 00 	li      r10,0
    9814:	41 a2 00 18 	beq     982c <smu7_get_pp_table_entry_callback_func_v1+0x428>
    9818:	39 29 ff ff 	addi    r9,r9,-1
    981c:	55 29 04 3e 	clrlwi  r9,r9,16
    9820:	39 40 00 01 	li      r10,1
    9824:	28 09 00 01 	cmplwi  r9,1
    9828:	7d 40 50 5e 	iselgt  r10,0,r10
    982c:	57 69 10 3a 	slwi    r9,r27,2
    9830:	a1 1d 03 06 	lhz     r8,774(r29)
    9834:	7d 3f 4a 14 	add     r9,r31,r9
    9838:	a0 7d 03 08 	lhz     r3,776(r29)
    983c:	b1 49 00 a4 	sth     r10,164(r9)
    9840:	3d 40 00 08 	lis     r10,8
    9844:	a0 9d 03 0a 	lhz     r4,778(r29)
    9848:	b1 01 00 1c 	sth     r8,28(r1)
    984c:	81 38 08 2c 	lwz     r9,2092(r24)
    9850:	a0 bd 03 0c 	lhz     r5,780(r29)
    9854:	a0 dd 03 0e 	lhz     r6,782(r29)
    9858:	a0 fd 03 10 	lhz     r7,784(r29)
    985c:	7c 09 50 00 	cmpw    r9,r10
    9860:	a1 1d 03 12 	lhz     r8,786(r29)
    9864:	8b de 00 07 	lbz     r30,7(r30)
    9868:	b0 61 00 1e 	sth     r3,30(r1)
    986c:	b0 81 00 20 	sth     r4,32(r1)
    9870:	b0 a1 00 22 	sth     r5,34(r1)
    9874:	b0 c1 00 24 	sth     r6,36(r1)
    9878:	b0 e1 00 26 	sth     r7,38(r1)
    987c:	b1 01 00 28 	sth     r8,40(r1)
    9880:	41 82 01 a4 	beq     9a24 <smu7_get_pp_table_entry_callback_func_v1+0x620>
    9884:	7c 09 50 40 	cmplw   r9,r10
    9888:	41 81 00 e4 	bgt     996c <smu7_get_pp_table_entry_callback_func_v1+0x568>
    988c:	3d 40 00 02 	lis     r10,2
    9890:	7c 09 50 00 	cmpw    r9,r10
    9894:	41 82 01 88 	beq     9a1c <smu7_get_pp_table_entry_callback_func_v1+0x618>
    9898:	7c 09 50 40 	cmplw   r9,r10
    989c:	41 81 01 0c 	bgt     99a8 <smu7_get_pp_table_entry_callback_func_v1+0x5a4>
    98a0:	2c 09 00 00 	cmpwi   r9,0
    98a4:	41 82 04 50 	beq     9cf4 <smu7_get_pp_table_entry_callback_func_v1+0x8f0>
    98a8:	3d 40 00 01 	lis     r10,1
    98ac:	7c 09 50 00 	cmpw    r9,r10
    98b0:	40 82 01 0c 	bne     99bc <smu7_get_pp_table_entry_callback_func_v1+0x5b8>
    98b4:	3b c0 00 01 	li      r30,1
    98b8:	57 7b 10 3a 	slwi    r27,r27,2
    98bc:	38 60 00 00 	li      r3,0
    98c0:	7f 7f da 14 	add     r27,r31,r27
    98c4:	b3 db 00 a6 	sth     r30,166(r27)
    98c8:	81 41 00 2c 	lwz     r10,44(r1)
    98cc:	81 22 03 88 	lwz     r9,904(r2)
    98d0:	7d 4a 4a 79 	xor.    r10,r10,r9
    98d4:	39 20 00 00 	li      r9,0
    98d8:	40 82 03 e4 	bne     9cbc <smu7_get_pp_table_entry_callback_func_v1+0x8b8>
    98dc:	80 01 00 64 	lwz     r0,100(r1)
    98e0:	82 c1 00 38 	lwz     r22,56(r1)
    98e4:	82 e1 00 3c 	lwz     r23,60(r1)
    98e8:	83 01 00 40 	lwz     r24,64(r1)
    98ec:	7c 08 03 a6 	mtlr    r0
    98f0:	83 21 00 44 	lwz     r25,68(r1)
    98f4:	83 41 00 48 	lwz     r26,72(r1)
    98f8:	83 61 00 4c 	lwz     r27,76(r1)
    98fc:	83 81 00 50 	lwz     r28,80(r1)
    9900:	83 a1 00 54 	lwz     r29,84(r1)
    9904:	83 c1 00 58 	lwz     r30,88(r1)
    9908:	83 e1 00 5c 	lwz     r31,92(r1)
    990c:	38 21 00 60 	addi    r1,r1,96
    9910:	4e 80 00 20 	blr
    9914:	3d 40 00 04 	lis     r10,4
    9918:	7c 09 50 00 	cmpw    r9,r10
    991c:	40 82 01 20 	bne     9a3c <smu7_get_pp_table_entry_callback_func_v1+0x638>
    9920:	3a e0 00 04 	li      r23,4
    9924:	4b ff fe 04 	b       9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9928:	3a e0 00 20 	li      r23,32
    992c:	4b ff fd fc 	b       9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9930:	2c 09 00 02 	cmpwi   r9,2
    9934:	40 82 fc e8 	bne     961c <smu7_get_pp_table_entry_callback_func_v1+0x218>
    9938:	4b ff fc f0 	b       9628 <smu7_get_pp_table_entry_callback_func_v1+0x224>
    993c:	39 29 ff ff 	addi    r9,r9,-1
    9940:	39 40 00 01 	li      r10,1
    9944:	55 29 04 3e 	clrlwi  r9,r9,16
    9948:	28 09 00 01 	cmplwi  r9,1
    994c:	7d 40 50 5e 	iselgt  r10,0,r10
    9950:	4b ff fc d8 	b       9628 <smu7_get_pp_table_entry_callback_func_v1+0x224>
    9954:	2c 09 00 01 	cmpwi   r9,1
    9958:	40 82 fe 78 	bne     97d0 <smu7_get_pp_table_entry_callback_func_v1+0x3cc>
    995c:	89 3e 00 00 	lbz     r9,0(r30)
    9960:	55 2a 20 36 	slwi    r10,r9,4
    9964:	7d 29 50 50 	subf    r9,r9,r10
    9968:	4b ff fe 34 	b       979c <smu7_get_pp_table_entry_callback_func_v1+0x398>
    996c:	3d 40 00 20 	lis     r10,32
    9970:	7c 09 50 00 	cmpw    r9,r10
    9974:	41 82 00 a0 	beq     9a14 <smu7_get_pp_table_entry_callback_func_v1+0x610>
    9978:	3d 40 00 40 	lis     r10,64
    997c:	7c 09 50 00 	cmpw    r9,r10
    9980:	41 82 00 8c 	beq     9a0c <smu7_get_pp_table_entry_callback_func_v1+0x608>
    9984:	3d 40 00 10 	lis     r10,16
    9988:	7c 09 50 00 	cmpw    r9,r10
    998c:	40 82 00 30 	bne     99bc <smu7_get_pp_table_entry_callback_func_v1+0x5b8>
    9990:	3b c0 00 0c 	li      r30,12
    9994:	4b ff ff 24 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9998:	89 3e 00 01 	lbz     r9,1(r30)
    999c:	55 2a 20 36 	slwi    r10,r9,4
    99a0:	7d 29 50 50 	subf    r9,r9,r10
    99a4:	4b ff fd 24 	b       96c8 <smu7_get_pp_table_entry_callback_func_v1+0x2c4>
    99a8:	3d 40 00 04 	lis     r10,4
    99ac:	7c 09 50 00 	cmpw    r9,r10
    99b0:	40 82 00 0c 	bne     99bc <smu7_get_pp_table_entry_callback_func_v1+0x5b8>
    99b4:	3b c0 00 04 	li      r30,4
    99b8:	4b ff ff 00 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    99bc:	39 41 00 30 	addi    r10,r1,48
    99c0:	57 c7 04 3e 	clrlwi  r7,r30,16
    99c4:	a4 ca ff ec 	lhzu    r6,-20(r10)
    99c8:	39 00 00 00 	li      r8,0
    99cc:	7c 07 30 00 	cmpw    r7,r6
    99d0:	41 82 00 d0 	beq     9aa0 <smu7_get_pp_table_entry_callback_func_v1+0x69c>
    99d4:	39 00 00 01 	li      r8,1
    99d8:	a0 ca 00 02 	lhz     r6,2(r10)
    99dc:	39 4a 00 02 	addi    r10,r10,2
    99e0:	7c 07 30 00 	cmpw    r7,r6
    99e4:	41 82 00 bc 	beq     9aa0 <smu7_get_pp_table_entry_callback_func_v1+0x69c>
    99e8:	a0 ca 00 02 	lhz     r6,2(r10)
    99ec:	39 08 00 01 	addi    r8,r8,1
    99f0:	39 4a 00 02 	addi    r10,r10,2
    99f4:	7c 07 30 00 	cmpw    r7,r6
    99f8:	41 82 00 a8 	beq     9aa0 <smu7_get_pp_table_entry_callback_func_v1+0x69c>
    99fc:	39 08 00 01 	addi    r8,r8,1
    9a00:	2c 08 00 07 	cmpwi   r8,7
    9a04:	40 82 ff d4 	bne     99d8 <smu7_get_pp_table_entry_callback_func_v1+0x5d4>
    9a08:	4b ff fe b0 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9a0c:	3b c0 00 20 	li      r30,32
    9a10:	4b ff fe a8 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9a14:	3b c0 00 10 	li      r30,16
    9a18:	4b ff fe a0 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9a1c:	3b c0 00 02 	li      r30,2
    9a20:	4b ff fe 98 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9a24:	3b c0 00 08 	li      r30,8
    9a28:	4b ff fe 90 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9a2c:	3a e0 00 02 	li      r23,2
    9a30:	4b ff fc f8 	b       9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9a34:	3a e0 00 08 	li      r23,8
    9a38:	4b ff fc f0 	b       9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9a3c:	39 41 00 30 	addi    r10,r1,48
    9a40:	56 e6 04 3e 	clrlwi  r6,r23,16
    9a44:	a4 8a ff ec 	lhzu    r4,-20(r10)
    9a48:	39 00 00 00 	li      r8,0
    9a4c:	7c 06 20 00 	cmpw    r6,r4
    9a50:	41 82 01 10 	beq     9b60 <smu7_get_pp_table_entry_callback_func_v1+0x75c>
    9a54:	39 00 00 01 	li      r8,1
    9a58:	a0 8a 00 02 	lhz     r4,2(r10)
    9a5c:	39 4a 00 02 	addi    r10,r10,2
    9a60:	7c 06 20 00 	cmpw    r6,r4
    9a64:	41 82 00 fc 	beq     9b60 <smu7_get_pp_table_entry_callback_func_v1+0x75c>
    9a68:	a0 8a 00 02 	lhz     r4,2(r10)
    9a6c:	39 08 00 01 	addi    r8,r8,1
    9a70:	39 4a 00 02 	addi    r10,r10,2
    9a74:	7c 06 20 00 	cmpw    r6,r4
    9a78:	41 82 00 e8 	beq     9b60 <smu7_get_pp_table_entry_callback_func_v1+0x75c>
    9a7c:	39 08 00 01 	addi    r8,r8,1
    9a80:	2c 08 00 07 	cmpwi   r8,7
    9a84:	40 82 ff d4 	bne     9a58 <smu7_get_pp_table_entry_callback_func_v1+0x654>
    9a88:	4b ff fc a0 	b       9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9a8c:	3a e0 00 10 	li      r23,16
    9a90:	4b ff fc 98 	b       9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9a94:	2c 09 00 02 	cmpwi   r9,2
    9a98:	40 82 fd 74 	bne     980c <smu7_get_pp_table_entry_callback_func_v1+0x408>
    9a9c:	4b ff fd 90 	b       982c <smu7_get_pp_table_entry_callback_func_v1+0x428>
    9aa0:	3d 40 00 01 	lis     r10,1
    9aa4:	7d 4a 40 30 	slw     r10,r10,r8
    9aa8:	7d 4a 48 39 	and.    r10,r10,r9
    9aac:	40 a2 fe 0c 	bne     98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9ab0:	2c 08 00 00 	cmpwi   r8,0
    9ab4:	39 48 ff ff 	addi    r10,r8,-1
    9ab8:	41 82 01 fc 	beq     9cb4 <smu7_get_pp_table_entry_callback_func_v1+0x8b0>
    9abc:	71 07 00 01 	andi.   r7,r8,1
    9ac0:	3c c0 00 01 	lis     r6,1
    9ac4:	41 82 00 14 	beq     9ad8 <smu7_get_pp_table_entry_callback_func_v1+0x6d4>
    9ac8:	7c c7 50 30 	slw     r7,r6,r10
    9acc:	7c e7 48 39 	and.    r7,r7,r9
    9ad0:	41 a2 00 24 	beq     9af4 <smu7_get_pp_table_entry_callback_func_v1+0x6f0>
    9ad4:	48 00 01 4c 	b       9c20 <smu7_get_pp_table_entry_callback_func_v1+0x81c>
    9ad8:	7c c7 50 30 	slw     r7,r6,r10
    9adc:	7c e7 48 39 	and.    r7,r7,r9
    9ae0:	40 82 01 40 	bne     9c20 <smu7_get_pp_table_entry_callback_func_v1+0x81c>
    9ae4:	39 4a ff ff 	addi    r10,r10,-1
    9ae8:	7c c7 50 30 	slw     r7,r6,r10
    9aec:	7c e7 48 39 	and.    r7,r7,r9
    9af0:	40 82 01 30 	bne     9c20 <smu7_get_pp_table_entry_callback_func_v1+0x81c>
    9af4:	39 4a ff ff 	addi    r10,r10,-1
    9af8:	2c 0a ff ff 	cmpwi   r10,-1
    9afc:	40 82 ff dc 	bne     9ad8 <smu7_get_pp_table_entry_callback_func_v1+0x6d4>
    9b00:	2c 08 00 06 	cmpwi   r8,6
    9b04:	39 08 00 01 	addi    r8,r8,1
    9b08:	41 a2 fd b0 	beq     98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9b0c:	71 0a 00 01 	andi.   r10,r8,1
    9b10:	3c e0 00 01 	lis     r7,1
    9b14:	40 82 00 30 	bne     9b44 <smu7_get_pp_table_entry_callback_func_v1+0x740>
    9b18:	7c ea 40 30 	slw     r10,r7,r8
    9b1c:	7d 4a 48 39 	and.    r10,r10,r9
    9b20:	41 a2 00 18 	beq     9b38 <smu7_get_pp_table_entry_callback_func_v1+0x734>
    9b24:	48 00 00 2c 	b       9b50 <smu7_get_pp_table_entry_callback_func_v1+0x74c>
    9b28:	39 08 00 01 	addi    r8,r8,1
    9b2c:	7c ea 40 30 	slw     r10,r7,r8
    9b30:	7d 4a 48 39 	and.    r10,r10,r9
    9b34:	40 82 00 1c 	bne     9b50 <smu7_get_pp_table_entry_callback_func_v1+0x74c>
    9b38:	39 08 00 01 	addi    r8,r8,1
    9b3c:	2c 08 00 07 	cmpwi   r8,7
    9b40:	41 a2 fd 78 	beq     98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9b44:	7c ea 40 30 	slw     r10,r7,r8
    9b48:	7d 4a 48 39 	and.    r10,r10,r9
    9b4c:	41 82 ff dc 	beq     9b28 <smu7_get_pp_table_entry_callback_func_v1+0x724>
    9b50:	55 08 08 3c 	slwi    r8,r8,1
    9b54:	7d 08 0a 14 	add     r8,r8,r1
    9b58:	a3 c8 00 1c 	lhz     r30,28(r8)
    9b5c:	4b ff fd 5c 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9b60:	3d 40 00 01 	lis     r10,1
    9b64:	7d 4a 40 30 	slw     r10,r10,r8
    9b68:	7d 4a 48 39 	and.    r10,r10,r9
    9b6c:	40 a2 fb bc 	bne     9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9b70:	2c 08 00 00 	cmpwi   r8,0
    9b74:	39 48 ff ff 	addi    r10,r8,-1
    9b78:	41 82 01 34 	beq     9cac <smu7_get_pp_table_entry_callback_func_v1+0x8a8>
    9b7c:	71 06 00 01 	andi.   r6,r8,1
    9b80:	3c 80 00 01 	lis     r4,1
    9b84:	41 82 00 14 	beq     9b98 <smu7_get_pp_table_entry_callback_func_v1+0x794>
    9b88:	7c 86 50 30 	slw     r6,r4,r10
    9b8c:	7c c6 48 39 	and.    r6,r6,r9
    9b90:	41 a2 00 24 	beq     9bb4 <smu7_get_pp_table_entry_callback_func_v1+0x7b0>
    9b94:	48 00 00 9c 	b       9c30 <smu7_get_pp_table_entry_callback_func_v1+0x82c>
    9b98:	7c 86 50 30 	slw     r6,r4,r10
    9b9c:	7c c6 48 39 	and.    r6,r6,r9
    9ba0:	40 82 00 90 	bne     9c30 <smu7_get_pp_table_entry_callback_func_v1+0x82c>
    9ba4:	39 4a ff ff 	addi    r10,r10,-1
    9ba8:	7c 86 50 30 	slw     r6,r4,r10
    9bac:	7c c6 48 39 	and.    r6,r6,r9
    9bb0:	40 82 00 80 	bne     9c30 <smu7_get_pp_table_entry_callback_func_v1+0x82c>
    9bb4:	39 4a ff ff 	addi    r10,r10,-1
    9bb8:	2c 0a ff ff 	cmpwi   r10,-1
    9bbc:	40 82 ff dc 	bne     9b98 <smu7_get_pp_table_entry_callback_func_v1+0x794>
    9bc0:	2c 08 00 06 	cmpwi   r8,6
    9bc4:	39 08 00 01 	addi    r8,r8,1
    9bc8:	41 a2 fb 60 	beq     9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9bcc:	71 0a 00 01 	andi.   r10,r8,1
    9bd0:	3c c0 00 01 	lis     r6,1
    9bd4:	40 82 00 30 	bne     9c04 <smu7_get_pp_table_entry_callback_func_v1+0x800>
    9bd8:	7c ca 40 30 	slw     r10,r6,r8
    9bdc:	7d 4a 48 39 	and.    r10,r10,r9
    9be0:	41 a2 00 18 	beq     9bf8 <smu7_get_pp_table_entry_callback_func_v1+0x7f4>
    9be4:	48 00 00 2c 	b       9c10 <smu7_get_pp_table_entry_callback_func_v1+0x80c>
    9be8:	39 08 00 01 	addi    r8,r8,1
    9bec:	7c ca 40 30 	slw     r10,r6,r8
    9bf0:	7d 4a 48 39 	and.    r10,r10,r9
    9bf4:	40 82 00 1c 	bne     9c10 <smu7_get_pp_table_entry_callback_func_v1+0x80c>
    9bf8:	39 08 00 01 	addi    r8,r8,1
    9bfc:	2c 08 00 07 	cmpwi   r8,7
    9c00:	41 a2 fb 28 	beq     9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9c04:	7c ca 40 30 	slw     r10,r6,r8
    9c08:	7d 4a 48 39 	and.    r10,r10,r9
    9c0c:	41 82 ff dc 	beq     9be8 <smu7_get_pp_table_entry_callback_func_v1+0x7e4>
    9c10:	55 08 08 3c 	slwi    r8,r8,1
    9c14:	7d 08 0a 14 	add     r8,r8,r1
    9c18:	a2 e8 00 1c 	lhz     r23,28(r8)
    9c1c:	4b ff fb 0c 	b       9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9c20:	55 49 08 3c 	slwi    r9,r10,1
    9c24:	7d 29 0a 14 	add     r9,r9,r1
    9c28:	a3 c9 00 1c 	lhz     r30,28(r9)
    9c2c:	4b ff fc 8c 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9c30:	55 49 08 3c 	slwi    r9,r10,1
    9c34:	7d 29 0a 14 	add     r9,r9,r1
    9c38:	a2 e9 00 1c 	lhz     r23,28(r9)
    9c3c:	4b ff fa ec 	b       9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9c40:	3c 80 00 00 	lis     r4,0
    9c44:	3c 60 00 00 	lis     r3,0
    9c48:	38 84 00 00 	addi    r4,r4,0
    9c4c:	38 63 00 00 	addi    r3,r3,0
    9c50:	38 84 03 14 	addi    r4,r4,788
    9c54:	38 63 07 e0 	addi    r3,r3,2016
    9c58:	48 00 00 01 	bl      9c58 <smu7_get_pp_table_entry_callback_func_v1+0x854>
    9c5c:	2c 03 00 00 	cmpwi   r3,0
    9c60:	40 82 00 78 	bne     9cd8 <smu7_get_pp_table_entry_callback_func_v1+0x8d4>
    9c64:	38 60 ff ea 	li      r3,-22
    9c68:	4b ff fc 60 	b       98c8 <smu7_get_pp_table_entry_callback_func_v1+0x4c4>
    9c6c:	3c 80 00 00 	lis     r4,0
    9c70:	3c 60 00 00 	lis     r3,0
    9c74:	38 84 00 00 	addi    r4,r4,0
    9c78:	38 63 00 00 	addi    r3,r3,0
    9c7c:	38 84 03 14 	addi    r4,r4,788
    9c80:	38 63 07 c4 	addi    r3,r3,1988
    9c84:	48 00 00 01 	bl      9c84 <smu7_get_pp_table_entry_callback_func_v1+0x880>
    9c88:	2c 03 00 00 	cmpwi   r3,0
    9c8c:	41 82 ff d8 	beq     9c64 <smu7_get_pp_table_entry_callback_func_v1+0x860>
    9c90:	3c 80 00 00 	lis     r4,0
    9c94:	3c 60 00 00 	lis     r3,0
    9c98:	38 84 00 00 	addi    r4,r4,0
    9c9c:	38 63 00 00 	addi    r3,r3,0
    9ca0:	48 00 00 01 	bl      9ca0 <smu7_get_pp_table_entry_callback_func_v1+0x89c>
    9ca4:	38 60 ff ea 	li      r3,-22
    9ca8:	4b ff fc 20 	b       98c8 <smu7_get_pp_table_entry_callback_func_v1+0x4c4>
    9cac:	39 00 00 01 	li      r8,1
    9cb0:	4b ff ff 1c 	b       9bcc <smu7_get_pp_table_entry_callback_func_v1+0x7c8>
    9cb4:	39 00 00 01 	li      r8,1
    9cb8:	4b ff fe 54 	b       9b0c <smu7_get_pp_table_entry_callback_func_v1+0x708>
    9cbc:	48 00 00 01 	bl      9cbc <smu7_get_pp_table_entry_callback_func_v1+0x8b8>
    9cc0:	3c 60 00 00 	lis     r3,0
    9cc4:	38 63 00 00 	addi    r3,r3,0
    9cc8:	48 00 00 01 	bl      9cc8 <smu7_get_pp_table_entry_callback_func_v1+0x8c4>
    9ccc:	a0 ff 00 94 	lhz     r7,148(r31)
    9cd0:	54 e5 04 3e 	clrlwi  r5,r7,16
    9cd4:	4b ff fa 54 	b       9728 <smu7_get_pp_table_entry_callback_func_v1+0x324>
    9cd8:	3c 80 00 00 	lis     r4,0
    9cdc:	3c 60 00 00 	lis     r3,0
    9ce0:	38 84 00 00 	addi    r4,r4,0
    9ce4:	38 63 00 00 	addi    r3,r3,0
    9ce8:	48 00 00 01 	bl      9ce8 <smu7_get_pp_table_entry_callback_func_v1+0x8e4>
    9cec:	38 60 ff ea 	li      r3,-22
    9cf0:	4b ff fb d8 	b       98c8 <smu7_get_pp_table_entry_callback_func_v1+0x4c4>
    9cf4:	3c 60 00 00 	lis     r3,0
    9cf8:	38 63 00 00 	addi    r3,r3,0
    9cfc:	48 00 00 01 	bl      9cfc <smu7_get_pp_table_entry_callback_func_v1+0x8f8>
    9d00:	4b ff fb b8 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>

Disassembly of section .text.unlikely:
