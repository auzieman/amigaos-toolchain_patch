
/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-003/output/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_hwmgr.o:     file format elf32-powerpc


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
    9564:	40 80 06 f8 	bge     9c5c <smu7_get_pp_table_entry_callback_func_v1+0x858>
    9568:	a0 ff 00 94 	lhz     r7,148(r31)
    956c:	81 3d 01 24 	lwz     r9,292(r29)
    9570:	54 e5 04 3e 	clrlwi  r5,r7,16
    9574:	7c 05 48 40 	cmplw   r5,r9
    9578:	40 80 06 b8 	bge     9c30 <smu7_get_pp_table_entry_callback_func_v1+0x82c>
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
    95b4:	7d 08 1b 78 	or      r8,r8,r3
    95b8:	55 49 40 2e 	slwi    r9,r10,8
    95bc:	7d 29 43 78 	or      r9,r9,r8
    95c0:	7c 89 4b 78 	or      r9,r4,r9
    95c4:	91 26 00 9c 	stw     r9,156(r6)
    95c8:	7d 3c c8 ae 	lbzx    r9,r28,r25
    95cc:	2c 09 00 00 	cmpwi   r9,0
    95d0:	41 82 00 ec 	beq     96bc <smu7_get_pp_table_entry_callback_func_v1+0x2b8>
    95d4:	2c 09 00 01 	cmpwi   r9,1
    95d8:	41 82 03 b0 	beq     9988 <smu7_get_pp_table_entry_callback_func_v1+0x584>
    95dc:	81 18 08 28 	lwz     r8,2088(r24)
    95e0:	39 40 00 01 	li      r10,1
    95e4:	55 09 04 3e 	clrlwi  r9,r8,16
    95e8:	28 09 00 02 	cmplwi  r9,2
    95ec:	41 82 00 38 	beq     9624 <smu7_get_pp_table_entry_callback_func_v1+0x220>
    95f0:	28 09 00 04 	cmplwi  r9,4
    95f4:	39 40 00 02 	li      r10,2
    95f8:	41 82 00 2c 	beq     9624 <smu7_get_pp_table_entry_callback_func_v1+0x220>
    95fc:	28 09 00 01 	cmplwi  r9,1
    9600:	39 40 00 00 	li      r10,0
    9604:	41 82 00 20 	beq     9624 <smu7_get_pp_table_entry_callback_func_v1+0x220>
    9608:	89 3e 00 04 	lbz     r9,4(r30)
    960c:	75 0a 00 04 	andis.  r10,r8,4
    9610:	7d 2a 4b 78 	mr      r10,r9
    9614:	40 82 03 0c 	bne     9920 <smu7_get_pp_table_entry_callback_func_v1+0x51c>
    9618:	75 08 00 02 	andis.  r8,r8,2
    961c:	39 40 00 00 	li      r10,0
    9620:	40 82 03 0c 	bne     992c <smu7_get_pp_table_entry_callback_func_v1+0x528>
    9624:	3f a0 00 00 	lis     r29,0
    9628:	3b bd 00 00 	addi    r29,r29,0
    962c:	57 69 10 3a 	slwi    r9,r27,2
    9630:	a1 1d 03 06 	lhz     r8,774(r29)
    9634:	7d 3f 4a 14 	add     r9,r31,r9
    9638:	b1 49 00 a4 	sth     r10,164(r9)
    963c:	3d 40 00 08 	lis     r10,8
    9640:	a0 9d 03 08 	lhz     r4,776(r29)
    9644:	a0 dd 03 0a 	lhz     r6,778(r29)
    9648:	b1 01 00 1c 	sth     r8,28(r1)
    964c:	a1 1d 03 0c 	lhz     r8,780(r29)
    9650:	81 38 08 2c 	lwz     r9,2092(r24)
    9654:	b0 81 00 1e 	sth     r4,30(r1)
    9658:	b0 c1 00 20 	sth     r6,32(r1)
    965c:	a0 9d 03 0e 	lhz     r4,782(r29)
    9660:	7c 09 50 00 	cmpw    r9,r10
    9664:	a0 dd 03 10 	lhz     r6,784(r29)
    9668:	b1 01 00 22 	sth     r8,34(r1)
    966c:	a1 1d 03 12 	lhz     r8,786(r29)
    9670:	8a fe 00 06 	lbz     r23,6(r30)
    9674:	b0 81 00 24 	sth     r4,36(r1)
    9678:	b0 c1 00 26 	sth     r6,38(r1)
    967c:	b1 01 00 28 	sth     r8,40(r1)
    9680:	41 82 03 a4 	beq     9a24 <smu7_get_pp_table_entry_callback_func_v1+0x620>
    9684:	7c 09 50 40 	cmplw   r9,r10
    9688:	41 81 00 70 	bgt     96f8 <smu7_get_pp_table_entry_callback_func_v1+0x2f4>
    968c:	3d 40 00 02 	lis     r10,2
    9690:	7c 09 50 00 	cmpw    r9,r10
    9694:	41 82 03 88 	beq     9a1c <smu7_get_pp_table_entry_callback_func_v1+0x618>
    9698:	7c 09 50 40 	cmplw   r9,r10
    969c:	41 81 02 68 	bgt     9904 <smu7_get_pp_table_entry_callback_func_v1+0x500>
    96a0:	2c 09 00 00 	cmpwi   r9,0
    96a4:	41 82 06 0c 	beq     9cb0 <smu7_get_pp_table_entry_callback_func_v1+0x8ac>
    96a8:	3d 40 00 01 	lis     r10,1
    96ac:	7c 09 50 00 	cmpw    r9,r10
    96b0:	40 82 03 7c 	bne     9a2c <smu7_get_pp_table_entry_callback_func_v1+0x628>
    96b4:	3a e0 00 01 	li      r23,1
    96b8:	48 00 00 68 	b       9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    96bc:	89 3e 00 01 	lbz     r9,1(r30)
    96c0:	1d 29 00 0b 	mulli   r9,r9,11
    96c4:	7d 36 4a 14 	add     r9,r22,r9
    96c8:	88 69 00 05 	lbz     r3,5(r9)
    96cc:	89 09 00 06 	lbz     r8,6(r9)
    96d0:	89 49 00 07 	lbz     r10,7(r9)
    96d4:	88 89 00 08 	lbz     r4,8(r9)
    96d8:	54 63 c0 0e 	slwi    r3,r3,24
    96dc:	55 08 80 1e 	slwi    r8,r8,16
    96e0:	7d 08 1b 78 	or      r8,r8,r3
    96e4:	55 49 40 2e 	slwi    r9,r10,8
    96e8:	7d 29 43 78 	or      r9,r9,r8
    96ec:	7c 89 4b 78 	or      r9,r4,r9
    96f0:	91 26 00 a0 	stw     r9,160(r6)
    96f4:	4b ff fe e8 	b       95dc <smu7_get_pp_table_entry_callback_func_v1+0x1d8>
    96f8:	3d 40 00 20 	lis     r10,32
    96fc:	7c 09 50 00 	cmpw    r9,r10
    9700:	41 82 03 7c 	beq     9a7c <smu7_get_pp_table_entry_callback_func_v1+0x678>
    9704:	3d 40 00 40 	lis     r10,64
    9708:	7c 09 50 00 	cmpw    r9,r10
    970c:	41 82 02 0c 	beq     9918 <smu7_get_pp_table_entry_callback_func_v1+0x514>
    9710:	3d 40 00 10 	lis     r10,16
    9714:	7c 09 50 00 	cmpw    r9,r10
    9718:	40 82 03 14 	bne     9a2c <smu7_get_pp_table_entry_callback_func_v1+0x628>
    971c:	3a e0 00 0c 	li      r23,12
    9720:	57 7b 10 3a 	slwi    r27,r27,2
    9724:	38 e7 00 01 	addi    r7,r7,1
    9728:	7d 3f da 14 	add     r9,r31,r27
    972c:	54 bb 08 3c 	slwi    r27,r5,1
    9730:	b2 e9 00 a6 	sth     r23,166(r9)
    9734:	7f 7b 2a 14 	add     r27,r27,r5
    9738:	b0 ff 00 94 	sth     r7,148(r31)
    973c:	57 67 10 3a 	slwi    r7,r27,2
    9740:	7c ff 3a 14 	add     r7,r31,r7
    9744:	89 3e 00 02 	lbz     r9,2(r30)
    9748:	1d 29 00 0d 	mulli   r9,r9,13
    974c:	7d 3a 4a 14 	add     r9,r26,r9
    9750:	88 a9 00 09 	lbz     r5,9(r9)
    9754:	89 09 00 0a 	lbz     r8,10(r9)
    9758:	89 49 00 0b 	lbz     r10,11(r9)
    975c:	88 c9 00 0c 	lbz     r6,12(r9)
    9760:	54 a5 c0 0e 	slwi    r5,r5,24
    9764:	55 08 80 1e 	slwi    r8,r8,16
    9768:	7d 08 2b 78 	or      r8,r8,r5
    976c:	55 49 40 2e 	slwi    r9,r10,8
    9770:	7d 29 43 78 	or      r9,r9,r8
    9774:	7c c9 4b 78 	or      r9,r6,r9
    9778:	91 27 00 9c 	stw     r9,156(r7)
    977c:	7d 3c c8 ae 	lbzx    r9,r28,r25
    9780:	2c 09 00 00 	cmpwi   r9,0
    9784:	40 82 01 c0 	bne     9944 <smu7_get_pp_table_entry_callback_func_v1+0x540>
    9788:	89 3e 00 00 	lbz     r9,0(r30)
    978c:	1d 29 00 0b 	mulli   r9,r9,11
    9790:	7d 36 4a 14 	add     r9,r22,r9
    9794:	88 a9 00 05 	lbz     r5,5(r9)
    9798:	89 09 00 06 	lbz     r8,6(r9)
    979c:	89 49 00 07 	lbz     r10,7(r9)
    97a0:	88 c9 00 08 	lbz     r6,8(r9)
    97a4:	54 a5 c0 0e 	slwi    r5,r5,24
    97a8:	55 08 80 1e 	slwi    r8,r8,16
    97ac:	7d 08 2b 78 	or      r8,r8,r5
    97b0:	55 49 40 2e 	slwi    r9,r10,8
    97b4:	7d 29 43 78 	or      r9,r9,r8
    97b8:	7c c9 4b 78 	or      r9,r6,r9
    97bc:	91 27 00 a0 	stw     r9,160(r7)
    97c0:	81 18 08 28 	lwz     r8,2088(r24)
    97c4:	39 40 00 01 	li      r10,1
    97c8:	55 09 04 3e 	clrlwi  r9,r8,16
    97cc:	28 09 00 02 	cmplwi  r9,2
    97d0:	41 82 00 4c 	beq     981c <smu7_get_pp_table_entry_callback_func_v1+0x418>
    97d4:	28 09 00 04 	cmplwi  r9,4
    97d8:	39 40 00 02 	li      r10,2
    97dc:	41 82 00 40 	beq     981c <smu7_get_pp_table_entry_callback_func_v1+0x418>
    97e0:	28 09 00 01 	cmplwi  r9,1
    97e4:	39 40 00 00 	li      r10,0
    97e8:	41 82 00 34 	beq     981c <smu7_get_pp_table_entry_callback_func_v1+0x418>
    97ec:	89 3e 00 05 	lbz     r9,5(r30)
    97f0:	75 0a 00 04 	andis.  r10,r8,4
    97f4:	7d 2a 4b 78 	mr      r10,r9
    97f8:	40 82 02 8c 	bne     9a84 <smu7_get_pp_table_entry_callback_func_v1+0x680>
    97fc:	75 08 00 02 	andis.  r8,r8,2
    9800:	39 40 00 00 	li      r10,0
    9804:	41 a2 00 18 	beq     981c <smu7_get_pp_table_entry_callback_func_v1+0x418>
    9808:	39 29 ff ff 	addi    r9,r9,-1
    980c:	55 29 04 3e 	clrlwi  r9,r9,16
    9810:	39 40 00 01 	li      r10,1
    9814:	28 09 00 01 	cmplwi  r9,1
    9818:	7d 40 50 5e 	iselgt  r10,0,r10
    981c:	57 69 10 3a 	slwi    r9,r27,2
    9820:	a1 1d 03 06 	lhz     r8,774(r29)
    9824:	7d 3f 4a 14 	add     r9,r31,r9
    9828:	a0 7d 03 08 	lhz     r3,776(r29)
    982c:	b1 49 00 a4 	sth     r10,164(r9)
    9830:	3d 40 00 08 	lis     r10,8
    9834:	a0 9d 03 0a 	lhz     r4,778(r29)
    9838:	b1 01 00 1c 	sth     r8,28(r1)
    983c:	81 38 08 2c 	lwz     r9,2092(r24)
    9840:	a0 bd 03 0c 	lhz     r5,780(r29)
    9844:	a0 dd 03 0e 	lhz     r6,782(r29)
    9848:	a0 fd 03 10 	lhz     r7,784(r29)
    984c:	7c 09 50 00 	cmpw    r9,r10
    9850:	a1 1d 03 12 	lhz     r8,786(r29)
    9854:	8b de 00 07 	lbz     r30,7(r30)
    9858:	b0 61 00 1e 	sth     r3,30(r1)
    985c:	b0 81 00 20 	sth     r4,32(r1)
    9860:	b0 a1 00 22 	sth     r5,34(r1)
    9864:	b0 c1 00 24 	sth     r6,36(r1)
    9868:	b0 e1 00 26 	sth     r7,38(r1)
    986c:	b1 01 00 28 	sth     r8,40(r1)
    9870:	41 82 01 a4 	beq     9a14 <smu7_get_pp_table_entry_callback_func_v1+0x610>
    9874:	7c 09 50 40 	cmplw   r9,r10
    9878:	41 81 00 e4 	bgt     995c <smu7_get_pp_table_entry_callback_func_v1+0x558>
    987c:	3d 40 00 02 	lis     r10,2
    9880:	7c 09 50 00 	cmpw    r9,r10
    9884:	41 82 01 88 	beq     9a0c <smu7_get_pp_table_entry_callback_func_v1+0x608>
    9888:	7c 09 50 40 	cmplw   r9,r10
    988c:	41 81 01 0c 	bgt     9998 <smu7_get_pp_table_entry_callback_func_v1+0x594>
    9890:	2c 09 00 00 	cmpwi   r9,0
    9894:	41 82 04 50 	beq     9ce4 <smu7_get_pp_table_entry_callback_func_v1+0x8e0>
    9898:	3d 40 00 01 	lis     r10,1
    989c:	7c 09 50 00 	cmpw    r9,r10
    98a0:	40 82 01 0c 	bne     99ac <smu7_get_pp_table_entry_callback_func_v1+0x5a8>
    98a4:	3b c0 00 01 	li      r30,1
    98a8:	57 7b 10 3a 	slwi    r27,r27,2
    98ac:	38 60 00 00 	li      r3,0
    98b0:	7f 7f da 14 	add     r27,r31,r27
    98b4:	b3 db 00 a6 	sth     r30,166(r27)
    98b8:	81 41 00 2c 	lwz     r10,44(r1)
    98bc:	81 22 03 88 	lwz     r9,904(r2)
    98c0:	7d 4a 4a 79 	xor.    r10,r10,r9
    98c4:	39 20 00 00 	li      r9,0
    98c8:	40 82 03 e4 	bne     9cac <smu7_get_pp_table_entry_callback_func_v1+0x8a8>
    98cc:	80 01 00 64 	lwz     r0,100(r1)
    98d0:	82 c1 00 38 	lwz     r22,56(r1)
    98d4:	82 e1 00 3c 	lwz     r23,60(r1)
    98d8:	83 01 00 40 	lwz     r24,64(r1)
    98dc:	7c 08 03 a6 	mtlr    r0
    98e0:	83 21 00 44 	lwz     r25,68(r1)
    98e4:	83 41 00 48 	lwz     r26,72(r1)
    98e8:	83 61 00 4c 	lwz     r27,76(r1)
    98ec:	83 81 00 50 	lwz     r28,80(r1)
    98f0:	83 a1 00 54 	lwz     r29,84(r1)
    98f4:	83 c1 00 58 	lwz     r30,88(r1)
    98f8:	83 e1 00 5c 	lwz     r31,92(r1)
    98fc:	38 21 00 60 	addi    r1,r1,96
    9900:	4e 80 00 20 	blr
    9904:	3d 40 00 04 	lis     r10,4
    9908:	7c 09 50 00 	cmpw    r9,r10
    990c:	40 82 01 20 	bne     9a2c <smu7_get_pp_table_entry_callback_func_v1+0x628>
    9910:	3a e0 00 04 	li      r23,4
    9914:	4b ff fe 0c 	b       9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9918:	3a e0 00 20 	li      r23,32
    991c:	4b ff fe 04 	b       9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9920:	2c 09 00 02 	cmpwi   r9,2
    9924:	40 82 fc f4 	bne     9618 <smu7_get_pp_table_entry_callback_func_v1+0x214>
    9928:	4b ff fc fc 	b       9624 <smu7_get_pp_table_entry_callback_func_v1+0x220>
    992c:	39 29 ff ff 	addi    r9,r9,-1
    9930:	39 40 00 01 	li      r10,1
    9934:	55 29 04 3e 	clrlwi  r9,r9,16
    9938:	28 09 00 01 	cmplwi  r9,1
    993c:	7d 40 50 5e 	iselgt  r10,0,r10
    9940:	4b ff fc e4 	b       9624 <smu7_get_pp_table_entry_callback_func_v1+0x220>
    9944:	2c 09 00 01 	cmpwi   r9,1
    9948:	40 82 fe 78 	bne     97c0 <smu7_get_pp_table_entry_callback_func_v1+0x3bc>
    994c:	89 3e 00 00 	lbz     r9,0(r30)
    9950:	55 2a 20 36 	slwi    r10,r9,4
    9954:	7d 29 50 50 	subf    r9,r9,r10
    9958:	4b ff fe 38 	b       9790 <smu7_get_pp_table_entry_callback_func_v1+0x38c>
    995c:	3d 40 00 20 	lis     r10,32
    9960:	7c 09 50 00 	cmpw    r9,r10
    9964:	41 82 00 a0 	beq     9a04 <smu7_get_pp_table_entry_callback_func_v1+0x600>
    9968:	3d 40 00 40 	lis     r10,64
    996c:	7c 09 50 00 	cmpw    r9,r10
    9970:	41 82 00 8c 	beq     99fc <smu7_get_pp_table_entry_callback_func_v1+0x5f8>
    9974:	3d 40 00 10 	lis     r10,16
    9978:	7c 09 50 00 	cmpw    r9,r10
    997c:	40 82 00 30 	bne     99ac <smu7_get_pp_table_entry_callback_func_v1+0x5a8>
    9980:	3b c0 00 0c 	li      r30,12
    9984:	4b ff ff 24 	b       98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    9988:	89 3e 00 01 	lbz     r9,1(r30)
    998c:	55 2a 20 36 	slwi    r10,r9,4
    9990:	7d 29 50 50 	subf    r9,r9,r10
    9994:	4b ff fd 30 	b       96c4 <smu7_get_pp_table_entry_callback_func_v1+0x2c0>
    9998:	3d 40 00 04 	lis     r10,4
    999c:	7c 09 50 00 	cmpw    r9,r10
    99a0:	40 82 00 0c 	bne     99ac <smu7_get_pp_table_entry_callback_func_v1+0x5a8>
    99a4:	3b c0 00 04 	li      r30,4
    99a8:	4b ff ff 00 	b       98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    99ac:	39 41 00 30 	addi    r10,r1,48
    99b0:	57 c7 04 3e 	clrlwi  r7,r30,16
    99b4:	a4 ca ff ec 	lhzu    r6,-20(r10)
    99b8:	39 00 00 00 	li      r8,0
    99bc:	7c 07 30 00 	cmpw    r7,r6
    99c0:	41 82 00 d0 	beq     9a90 <smu7_get_pp_table_entry_callback_func_v1+0x68c>
    99c4:	39 00 00 01 	li      r8,1
    99c8:	a0 ca 00 02 	lhz     r6,2(r10)
    99cc:	39 4a 00 02 	addi    r10,r10,2
    99d0:	7c 07 30 00 	cmpw    r7,r6
    99d4:	41 82 00 bc 	beq     9a90 <smu7_get_pp_table_entry_callback_func_v1+0x68c>
    99d8:	a0 ca 00 02 	lhz     r6,2(r10)
    99dc:	39 08 00 01 	addi    r8,r8,1
    99e0:	39 4a 00 02 	addi    r10,r10,2
    99e4:	7c 07 30 00 	cmpw    r7,r6
    99e8:	41 82 00 a8 	beq     9a90 <smu7_get_pp_table_entry_callback_func_v1+0x68c>
    99ec:	39 08 00 01 	addi    r8,r8,1
    99f0:	2c 08 00 07 	cmpwi   r8,7
    99f4:	40 82 ff d4 	bne     99c8 <smu7_get_pp_table_entry_callback_func_v1+0x5c4>
    99f8:	4b ff fe b0 	b       98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    99fc:	3b c0 00 20 	li      r30,32
    9a00:	4b ff fe a8 	b       98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    9a04:	3b c0 00 10 	li      r30,16
    9a08:	4b ff fe a0 	b       98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    9a0c:	3b c0 00 02 	li      r30,2
    9a10:	4b ff fe 98 	b       98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    9a14:	3b c0 00 08 	li      r30,8
    9a18:	4b ff fe 90 	b       98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    9a1c:	3a e0 00 02 	li      r23,2
    9a20:	4b ff fd 00 	b       9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9a24:	3a e0 00 08 	li      r23,8
    9a28:	4b ff fc f8 	b       9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9a2c:	39 41 00 30 	addi    r10,r1,48
    9a30:	56 e6 04 3e 	clrlwi  r6,r23,16
    9a34:	a4 8a ff ec 	lhzu    r4,-20(r10)
    9a38:	39 00 00 00 	li      r8,0
    9a3c:	7c 06 20 00 	cmpw    r6,r4
    9a40:	41 82 01 10 	beq     9b50 <smu7_get_pp_table_entry_callback_func_v1+0x74c>
    9a44:	39 00 00 01 	li      r8,1
    9a48:	a0 8a 00 02 	lhz     r4,2(r10)
    9a4c:	39 4a 00 02 	addi    r10,r10,2
    9a50:	7c 06 20 00 	cmpw    r6,r4
    9a54:	41 82 00 fc 	beq     9b50 <smu7_get_pp_table_entry_callback_func_v1+0x74c>
    9a58:	a0 8a 00 02 	lhz     r4,2(r10)
    9a5c:	39 08 00 01 	addi    r8,r8,1
    9a60:	39 4a 00 02 	addi    r10,r10,2
    9a64:	7c 06 20 00 	cmpw    r6,r4
    9a68:	41 82 00 e8 	beq     9b50 <smu7_get_pp_table_entry_callback_func_v1+0x74c>
    9a6c:	39 08 00 01 	addi    r8,r8,1
    9a70:	2c 08 00 07 	cmpwi   r8,7
    9a74:	40 82 ff d4 	bne     9a48 <smu7_get_pp_table_entry_callback_func_v1+0x644>
    9a78:	4b ff fc a8 	b       9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9a7c:	3a e0 00 10 	li      r23,16
    9a80:	4b ff fc a0 	b       9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9a84:	2c 09 00 02 	cmpwi   r9,2
    9a88:	40 82 fd 74 	bne     97fc <smu7_get_pp_table_entry_callback_func_v1+0x3f8>
    9a8c:	4b ff fd 90 	b       981c <smu7_get_pp_table_entry_callback_func_v1+0x418>
    9a90:	3d 40 00 01 	lis     r10,1
    9a94:	7d 4a 40 30 	slw     r10,r10,r8
    9a98:	7d 4a 48 39 	and.    r10,r10,r9
    9a9c:	40 a2 fe 0c 	bne     98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    9aa0:	2c 08 00 00 	cmpwi   r8,0
    9aa4:	39 48 ff ff 	addi    r10,r8,-1
    9aa8:	41 82 01 fc 	beq     9ca4 <smu7_get_pp_table_entry_callback_func_v1+0x8a0>
    9aac:	71 07 00 01 	andi.   r7,r8,1
    9ab0:	3c c0 00 01 	lis     r6,1
    9ab4:	41 82 00 14 	beq     9ac8 <smu7_get_pp_table_entry_callback_func_v1+0x6c4>
    9ab8:	7c c7 50 30 	slw     r7,r6,r10
    9abc:	7c e7 48 39 	and.    r7,r7,r9
    9ac0:	41 a2 00 24 	beq     9ae4 <smu7_get_pp_table_entry_callback_func_v1+0x6e0>
    9ac4:	48 00 01 4c 	b       9c10 <smu7_get_pp_table_entry_callback_func_v1+0x80c>
    9ac8:	7c c7 50 30 	slw     r7,r6,r10
    9acc:	7c e7 48 39 	and.    r7,r7,r9
    9ad0:	40 82 01 40 	bne     9c10 <smu7_get_pp_table_entry_callback_func_v1+0x80c>
    9ad4:	39 4a ff ff 	addi    r10,r10,-1
    9ad8:	7c c7 50 30 	slw     r7,r6,r10
    9adc:	7c e7 48 39 	and.    r7,r7,r9
    9ae0:	40 82 01 30 	bne     9c10 <smu7_get_pp_table_entry_callback_func_v1+0x80c>
    9ae4:	39 4a ff ff 	addi    r10,r10,-1
    9ae8:	2c 0a ff ff 	cmpwi   r10,-1
    9aec:	40 82 ff dc 	bne     9ac8 <smu7_get_pp_table_entry_callback_func_v1+0x6c4>
    9af0:	2c 08 00 06 	cmpwi   r8,6
    9af4:	39 08 00 01 	addi    r8,r8,1
    9af8:	41 a2 fd b0 	beq     98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    9afc:	71 0a 00 01 	andi.   r10,r8,1
    9b00:	3c e0 00 01 	lis     r7,1
    9b04:	40 82 00 30 	bne     9b34 <smu7_get_pp_table_entry_callback_func_v1+0x730>
    9b08:	7c ea 40 30 	slw     r10,r7,r8
    9b0c:	7d 4a 48 39 	and.    r10,r10,r9
    9b10:	41 a2 00 18 	beq     9b28 <smu7_get_pp_table_entry_callback_func_v1+0x724>
    9b14:	48 00 00 2c 	b       9b40 <smu7_get_pp_table_entry_callback_func_v1+0x73c>
    9b18:	39 08 00 01 	addi    r8,r8,1
    9b1c:	7c ea 40 30 	slw     r10,r7,r8
    9b20:	7d 4a 48 39 	and.    r10,r10,r9
    9b24:	40 82 00 1c 	bne     9b40 <smu7_get_pp_table_entry_callback_func_v1+0x73c>
    9b28:	39 08 00 01 	addi    r8,r8,1
    9b2c:	2c 08 00 07 	cmpwi   r8,7
    9b30:	41 a2 fd 78 	beq     98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    9b34:	7c ea 40 30 	slw     r10,r7,r8
    9b38:	7d 4a 48 39 	and.    r10,r10,r9
    9b3c:	41 82 ff dc 	beq     9b18 <smu7_get_pp_table_entry_callback_func_v1+0x714>
    9b40:	55 08 08 3c 	slwi    r8,r8,1
    9b44:	7d 08 0a 14 	add     r8,r8,r1
    9b48:	a3 c8 00 1c 	lhz     r30,28(r8)
    9b4c:	4b ff fd 5c 	b       98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    9b50:	3d 40 00 01 	lis     r10,1
    9b54:	7d 4a 40 30 	slw     r10,r10,r8
    9b58:	7d 4a 48 39 	and.    r10,r10,r9
    9b5c:	40 a2 fb c4 	bne     9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9b60:	2c 08 00 00 	cmpwi   r8,0
    9b64:	39 48 ff ff 	addi    r10,r8,-1
    9b68:	41 82 01 34 	beq     9c9c <smu7_get_pp_table_entry_callback_func_v1+0x898>
    9b6c:	71 06 00 01 	andi.   r6,r8,1
    9b70:	3c 80 00 01 	lis     r4,1
    9b74:	41 82 00 14 	beq     9b88 <smu7_get_pp_table_entry_callback_func_v1+0x784>
    9b78:	7c 86 50 30 	slw     r6,r4,r10
    9b7c:	7c c6 48 39 	and.    r6,r6,r9
    9b80:	41 a2 00 24 	beq     9ba4 <smu7_get_pp_table_entry_callback_func_v1+0x7a0>
    9b84:	48 00 00 9c 	b       9c20 <smu7_get_pp_table_entry_callback_func_v1+0x81c>
    9b88:	7c 86 50 30 	slw     r6,r4,r10
    9b8c:	7c c6 48 39 	and.    r6,r6,r9
    9b90:	40 82 00 90 	bne     9c20 <smu7_get_pp_table_entry_callback_func_v1+0x81c>
    9b94:	39 4a ff ff 	addi    r10,r10,-1
    9b98:	7c 86 50 30 	slw     r6,r4,r10
    9b9c:	7c c6 48 39 	and.    r6,r6,r9
    9ba0:	40 82 00 80 	bne     9c20 <smu7_get_pp_table_entry_callback_func_v1+0x81c>
    9ba4:	39 4a ff ff 	addi    r10,r10,-1
    9ba8:	2c 0a ff ff 	cmpwi   r10,-1
    9bac:	40 82 ff dc 	bne     9b88 <smu7_get_pp_table_entry_callback_func_v1+0x784>
    9bb0:	2c 08 00 06 	cmpwi   r8,6
    9bb4:	39 08 00 01 	addi    r8,r8,1
    9bb8:	41 a2 fb 68 	beq     9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9bbc:	71 0a 00 01 	andi.   r10,r8,1
    9bc0:	3c c0 00 01 	lis     r6,1
    9bc4:	40 82 00 30 	bne     9bf4 <smu7_get_pp_table_entry_callback_func_v1+0x7f0>
    9bc8:	7c ca 40 30 	slw     r10,r6,r8
    9bcc:	7d 4a 48 39 	and.    r10,r10,r9
    9bd0:	41 a2 00 18 	beq     9be8 <smu7_get_pp_table_entry_callback_func_v1+0x7e4>
    9bd4:	48 00 00 2c 	b       9c00 <smu7_get_pp_table_entry_callback_func_v1+0x7fc>
    9bd8:	39 08 00 01 	addi    r8,r8,1
    9bdc:	7c ca 40 30 	slw     r10,r6,r8
    9be0:	7d 4a 48 39 	and.    r10,r10,r9
    9be4:	40 82 00 1c 	bne     9c00 <smu7_get_pp_table_entry_callback_func_v1+0x7fc>
    9be8:	39 08 00 01 	addi    r8,r8,1
    9bec:	2c 08 00 07 	cmpwi   r8,7
    9bf0:	41 a2 fb 30 	beq     9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9bf4:	7c ca 40 30 	slw     r10,r6,r8
    9bf8:	7d 4a 48 39 	and.    r10,r10,r9
    9bfc:	41 82 ff dc 	beq     9bd8 <smu7_get_pp_table_entry_callback_func_v1+0x7d4>
    9c00:	55 08 08 3c 	slwi    r8,r8,1
    9c04:	7d 08 0a 14 	add     r8,r8,r1
    9c08:	a2 e8 00 1c 	lhz     r23,28(r8)
    9c0c:	4b ff fb 14 	b       9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9c10:	55 49 08 3c 	slwi    r9,r10,1
    9c14:	7d 29 0a 14 	add     r9,r9,r1
    9c18:	a3 c9 00 1c 	lhz     r30,28(r9)
    9c1c:	4b ff fc 8c 	b       98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>
    9c20:	55 49 08 3c 	slwi    r9,r10,1
    9c24:	7d 29 0a 14 	add     r9,r9,r1
    9c28:	a2 e9 00 1c 	lhz     r23,28(r9)
    9c2c:	4b ff fa f4 	b       9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9c30:	3c 80 00 00 	lis     r4,0
    9c34:	3c 60 00 00 	lis     r3,0
    9c38:	38 84 00 00 	addi    r4,r4,0
    9c3c:	38 63 00 00 	addi    r3,r3,0
    9c40:	38 84 03 14 	addi    r4,r4,788
    9c44:	38 63 07 e0 	addi    r3,r3,2016
    9c48:	48 00 00 01 	bl      9c48 <smu7_get_pp_table_entry_callback_func_v1+0x844>
    9c4c:	2c 03 00 00 	cmpwi   r3,0
    9c50:	40 82 00 78 	bne     9cc8 <smu7_get_pp_table_entry_callback_func_v1+0x8c4>
    9c54:	38 60 ff ea 	li      r3,-22
    9c58:	4b ff fc 60 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9c5c:	3c 80 00 00 	lis     r4,0
    9c60:	3c 60 00 00 	lis     r3,0
    9c64:	38 84 00 00 	addi    r4,r4,0
    9c68:	38 63 00 00 	addi    r3,r3,0
    9c6c:	38 84 03 14 	addi    r4,r4,788
    9c70:	38 63 07 c4 	addi    r3,r3,1988
    9c74:	48 00 00 01 	bl      9c74 <smu7_get_pp_table_entry_callback_func_v1+0x870>
    9c78:	2c 03 00 00 	cmpwi   r3,0
    9c7c:	41 82 ff d8 	beq     9c54 <smu7_get_pp_table_entry_callback_func_v1+0x850>
    9c80:	3c 80 00 00 	lis     r4,0
    9c84:	3c 60 00 00 	lis     r3,0
    9c88:	38 84 00 00 	addi    r4,r4,0
    9c8c:	38 63 00 00 	addi    r3,r3,0
    9c90:	48 00 00 01 	bl      9c90 <smu7_get_pp_table_entry_callback_func_v1+0x88c>
    9c94:	38 60 ff ea 	li      r3,-22
    9c98:	4b ff fc 20 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9c9c:	39 00 00 01 	li      r8,1
    9ca0:	4b ff ff 1c 	b       9bbc <smu7_get_pp_table_entry_callback_func_v1+0x7b8>
    9ca4:	39 00 00 01 	li      r8,1
    9ca8:	4b ff fe 54 	b       9afc <smu7_get_pp_table_entry_callback_func_v1+0x6f8>
    9cac:	48 00 00 01 	bl      9cac <smu7_get_pp_table_entry_callback_func_v1+0x8a8>
    9cb0:	3c 60 00 00 	lis     r3,0
    9cb4:	38 63 00 00 	addi    r3,r3,0
    9cb8:	48 00 00 01 	bl      9cb8 <smu7_get_pp_table_entry_callback_func_v1+0x8b4>
    9cbc:	a0 ff 00 94 	lhz     r7,148(r31)
    9cc0:	54 e5 04 3e 	clrlwi  r5,r7,16
    9cc4:	4b ff fa 5c 	b       9720 <smu7_get_pp_table_entry_callback_func_v1+0x31c>
    9cc8:	3c 80 00 00 	lis     r4,0
    9ccc:	3c 60 00 00 	lis     r3,0
    9cd0:	38 84 00 00 	addi    r4,r4,0
    9cd4:	38 63 00 00 	addi    r3,r3,0
    9cd8:	48 00 00 01 	bl      9cd8 <smu7_get_pp_table_entry_callback_func_v1+0x8d4>
    9cdc:	38 60 ff ea 	li      r3,-22
    9ce0:	4b ff fb d8 	b       98b8 <smu7_get_pp_table_entry_callback_func_v1+0x4b4>
    9ce4:	3c 60 00 00 	lis     r3,0
    9ce8:	38 63 00 00 	addi    r3,r3,0
    9cec:	48 00 00 01 	bl      9cec <smu7_get_pp_table_entry_callback_func_v1+0x8e8>
    9cf0:	4b ff fb b8 	b       98a8 <smu7_get_pp_table_entry_callback_func_v1+0x4a4>

Disassembly of section .text.unlikely:
