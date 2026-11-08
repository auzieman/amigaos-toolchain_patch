/*
 * Copyright 2015 Advanced Micro Devices, Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE COPYRIGHT HOLDER(S) OR AUTHOR(S) BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 *
 */



typedef unsigned char uint8_t;typedef unsigned short uint16_t;typedef unsigned int uint32_t;typedef uint32_t u32;
#define EINVAL 22
#define EIO 5
#define ENXIO 6
#define EOPNOTSUPP 95
#define CHIP_POLARIS11 1
#define mmSMC_IND_DATA_11 1
#define mmSMC_MSG_ARG_0 2
#define mmSMC_RESP_0 3
#define mmSMC_MESSAGE_0 4
struct amdgpu_device {void*dev;};
struct pp_hwmgr {int chip_id;void*device;struct amdgpu_device*adev;};
#define pr_info(...) do {}while(0)
#define dev_info(...) do {}while(0)
#define dev_dbg(...) do {}while(0)
#define PP_ASSERT_WITH_CODE(test,msg,action) do {if(!(test)){action;}}while(0)
#define PHM_WAIT_FIELD_UNEQUAL(...) do {}while(0)
static uint8_t ram[512];static uint32_t address,arg,message,response=1,injected=1;
static int smu7_set_smc_sram_address(struct pp_hwmgr*h,uint32_t a,uint32_t limit){(void)h;if(a>=limit)return -EINVAL;address=a;return 0;}
/* Numeric registers, as provided by the kernel accessors. SMC SRAM is MSB-first. */
static void cgs_write_register(void*d,uint32_t reg,uint32_t value) {
 (void)d;
 if(reg==mmSMC_IND_DATA_11){ram[address]=value>>24;ram[address+1]=value>>16;ram[address+2]=value>>8;ram[address+3]=value;}
 else if(reg==mmSMC_MSG_ARG_0)arg=value;
 else if(reg==mmSMC_RESP_0)response=value;
 else if(reg==mmSMC_MESSAGE_0){message=value;response=injected;}
}
static uint32_t cgs_read_register(void*d,uint32_t reg){(void)d;(void)reg;return ((uint32_t)ram[address]<<24)|((uint32_t)ram[address+1]<<16)|((uint32_t)ram[address+2]<<8)|ram[address+3];}
#define PHM_READ_FIELD(...) response
int main(void);
static void emit(const char *p, unsigned n) {
#ifdef __powerpc__
 register unsigned r0 __asm__("r0")=4;
 register unsigned r3 __asm__("r3")=1;
 register const char *r4 __asm__("r4")=p;
 register unsigned r5 __asm__("r5")=n;
 __asm__ volatile("sc" : "+r"(r0),"+r"(r3) : "r"(r4),"r"(r5) : "cr0","memory");
#else
 long result;
 __asm__ volatile("syscall" : "=a"(result) : "0"(1L),"D"(1L),"S"(p),"d"((unsigned long)n) : "rcx","r11","memory");
#endif
}
static void hex(uint32_t n) {
 char b[9];const char *digits="0123456789abcdef";
 for(unsigned i=0;i<8;i++) b[i]=digits[(n >> (28-i*4))&15];
 b[8]=' ';emit(b,9);
}
void _start(void) {
 int r=main();
#ifdef __powerpc__
 register unsigned r0 __asm__("r0")=1;
 register unsigned r3 __asm__("r3")=r;
 __asm__ volatile("sc" : "+r"(r0),"+r"(r3) : : "cr0","memory");
#else
 __asm__ volatile("syscall" : : "a"(60L),"D"((long)r) : "rcx","r11","memory");
#endif
 __builtin_unreachable();
}

int smu7_copy_bytes_to_smc(struct pp_hwmgr *hwmgr, uint32_t smc_start_address,
				const uint8_t *src, uint32_t byte_count, uint32_t limit)
{
	int result;
	uint32_t data = 0;
	uint32_t original_data;
	uint32_t addr = 0;
	uint32_t extra_shift;

	PP_ASSERT_WITH_CODE((0 == (3 & smc_start_address)), "SMC address must be 4 byte aligned.", return -EINVAL);
	PP_ASSERT_WITH_CODE((limit > (smc_start_address + byte_count)), "SMC address is beyond the SMC RAM area.", return -EINVAL);

	addr = smc_start_address;

	while (byte_count >= 4) {
	/* Bytes are written into the SMC addres space with the MSB first. */
		data = src[0] * 0x1000000 + src[1] * 0x10000 + src[2] * 0x100 + src[3];

		result = smu7_set_smc_sram_address(hwmgr, addr, limit);

		if (0 != result)
			return result;

		cgs_write_register(hwmgr->device, mmSMC_IND_DATA_11, data);

		src += 4;
		byte_count -= 4;
		addr += 4;
	}

	if (0 != byte_count) {

		data = 0;

		result = smu7_set_smc_sram_address(hwmgr, addr, limit);

		if (0 != result)
			return result;


		original_data = cgs_read_register(hwmgr->device, mmSMC_IND_DATA_11);

		extra_shift = 8 * (4 - byte_count);

		while (byte_count > 0) {
			/* Bytes are written into the SMC addres space with the MSB first. */
			data = (0x100 * data) + *src++;
			byte_count--;
		}

		data <<= extra_shift;

		data |= (original_data & ~((~0UL) << extra_shift));

		result = smu7_set_smc_sram_address(hwmgr, addr, limit);

		if (0 != result)
			return result;

		cgs_write_register(hwmgr->device, mmSMC_IND_DATA_11, data);
	}

	return 0;
}
int smu7_send_msg_to_smc(struct pp_hwmgr *hwmgr, uint16_t msg)
{
	struct amdgpu_device *adev = hwmgr->adev;
	int ret;

	if (hwmgr->chip_id == CHIP_POLARIS11)
		dev_info(adev->dev, "PWR_TRACE smu_msg=%#x enter\n", msg);

	PHM_WAIT_FIELD_UNEQUAL(hwmgr, SMC_RESP_0, SMC_RESP, 0);

	cgs_write_register(hwmgr->device, mmSMC_RESP_0, 0);
	cgs_write_register(hwmgr->device, mmSMC_MESSAGE_0, msg);

	PHM_WAIT_FIELD_UNEQUAL(hwmgr, SMC_RESP_0, SMC_RESP, 0);

	ret = PHM_READ_FIELD(hwmgr->device, SMC_RESP_0, SMC_RESP);

	if (hwmgr->chip_id == CHIP_POLARIS11)
		dev_info(adev->dev, "PWR_TRACE smu_msg=%#x response=%#x\n", msg, ret);

	switch (ret) {
	case 1:
		return 0;
	case 0xFE:
		dev_dbg(adev->dev, "SMU message %#x was not supported\n", msg);
		return -EOPNOTSUPP;
	default:
		dev_info(adev->dev, "SMU message %#x failed: response is %d\n", msg, ret);
		return ret != 0xFFFF ? -EIO : -ENXIO;
	}
}
int smu7_send_msg_to_smc_with_parameter(struct pp_hwmgr *hwmgr, uint16_t msg, uint32_t parameter)
{
	if (hwmgr->chip_id == CHIP_POLARIS11)
		pr_info("PWR_TRACE smu_msg=%#x parameter=%#x\n", msg, parameter);

	PHM_WAIT_FIELD_UNEQUAL(hwmgr, SMC_RESP_0, SMC_RESP, 0);

	cgs_write_register(hwmgr->device, mmSMC_MSG_ARG_0, parameter);

	return smu7_send_msg_to_smc(hwmgr, msg);
}
int main(void) {
 struct amdgpu_device dev={0};struct pp_hwmgr h={CHIP_POLARIS11,0,&dev};
 uint8_t source[128];unsigned transfer_cases=0,message_cases=0;
 for(unsigned i=0;i<128;i++)source[i]=(i*73+19)&255;
 for(unsigned offset=0;offset<16;offset+=4)for(unsigned n=1;n<=64;n++) {
  for(unsigned i=0;i<512;i++)ram[i]=0xa5;
  if(smu7_copy_bytes_to_smc(&h,offset,source,n,512))return 1;
  for(unsigned i=0;i<512;i++) {
   uint8_t expected=(i>=offset&&i<offset+n)?source[i-offset]:0xa5;
   if(ram[i]!=expected)return 2;
  }
  transfer_cases++;
 }
 if(smu7_copy_bytes_to_smc(&h,1,source,4,512)!=-EINVAL)return 3;
 if(smu7_copy_bytes_to_smc(&h,508,source,4,512)!=-EINVAL)return 4;
 uint32_t codes[]={1,0xfe,0xffff,0,2,0x1234};int results[]={0,-EOPNOTSUPP,-ENXIO,-EIO,-EIO,-EIO};
 for(unsigned mask=1;mask<256;mask++)for(unsigned r=0;r<6;r++) {
  injected=codes[r];
  int result=smu7_send_msg_to_smc_with_parameter(&h,0x145,mask);
  if(arg!=mask||message!=0x145||result!=results[r])return 5;
  message_cases++;
 }
 hex(transfer_cases);hex(message_cases);hex(2);emit("\n",1);return 0;
}
