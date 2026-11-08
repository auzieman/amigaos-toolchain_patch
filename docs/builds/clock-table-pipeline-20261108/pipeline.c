/*
 * Copyright 2007-8 Advanced Micro Devices, Inc.
 * Copyright 2008 Red Hat Inc.
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
 * Authors: Dave Airlie
 *          Alex Deucher
 */


typedef unsigned char uint8_t;typedef unsigned short uint16_t;typedef unsigned int uint32_t;
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef _Bool bool;
#define true 1
#define false 0
#define EINVAL 22
#define __counted_by(x)
#define offsetof(t,f) __builtin_offsetof(t,f)
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define ATOM_BIG_ENDIAN 1
#define __BIG_ENDIAN 4321
#define cpu_to_le32(x) __builtin_bswap32(x)
#define le32_to_cpu(x) __builtin_bswap32(x)
#define le16_to_cpu(x) __builtin_bswap16(x)
#else
#define ATOM_BIG_ENDIAN 0
#define cpu_to_le32(x) (x)
#define le32_to_cpu(x) (x)
#define le16_to_cpu(x) (x)
#endif
typedef uint32_t ULONG;typedef uint16_t USHORT;typedef uint8_t UCHAR;
typedef signed char CHAR;typedef int LONG;
#include "/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-001/source/drivers/gpu/drm/amd/include/atombios.h"

static uint32_t get_unaligned_le32(const void *p) {
 const uint8_t*b=p;return (uint32_t)b[0]|((uint32_t)b[1]<<8)|((uint32_t)b[2]<<16)|((uint32_t)b[3]<<24);
}
static void put_unaligned_le32(uint32_t n,void*p) {
 uint8_t*b=p;b[0]=n;b[1]=n>>8;b[2]=n>>16;b[3]=n>>24;
}
void *memset(void*p,int c,__SIZE_TYPE__ n) {
 volatile unsigned char*b=p;for(__SIZE_TYPE__ i=0;i<n;i++){b[i]=c;}return p;
}
int main(void);
void *memcpy(void *dst, const void *src, __SIZE_TYPE__ n) {
 volatile unsigned char *d=dst; const volatile unsigned char *s=src;
 for (__SIZE_TYPE__ i=0;i<n;i++) { d[i]=s[i]; }
 return dst;
}
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


typedef unsigned long long uint64_t;typedef uint64_t u64;
#define NULL ((void*)0)
#define CHIP_POLARIS11 1
#define PP_INIT_CALL(h,expr) (expr)
#define pr_info(...) do {}while(0)
#define PP_ASSERT_WITH_CODE(test,msg,action) do {if(!(test)){action;}}while(0)
#define PHM_PlatformCaps_SclkDeepSleep 1
#define PPSMC_DISPLAY_WATERMARK_LOW 0
#define NUM_SCLK_RANGE 8
#define do_div(n,b) ((n)/=(b))
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define cpu_to_be32(x) (x)
#define cpu_to_be16(x) (x)
#define be32_to_cpu(x) (x)
#define be16_to_cpu(x) (x)
#else
#define cpu_to_be32(x) __builtin_bswap32(x)
#define cpu_to_be16(x) __builtin_bswap16(x)
#define be32_to_cpu(x) __builtin_bswap32(x)
#define be16_to_cpu(x) __builtin_bswap16(x)
#endif
#include "/srv/data1/tabor-build/linux-live-001/work/e2e-usb-20261108-003/source/drivers/gpu/drm/amd/pm/powerplay/inc/pp_endian.h"
/* The ATOM parameter word is LE: frequency[23:0], flags[31:24].
 * Converting a value before assigning a 24-bit C bitfield truncates it on BE.
 * Read/write the complete parameter word, avoiding native bitfield layout.
 */
static inline void amdgpu_atom_set_clock_word(void *word, uint32_t clock, uint8_t flags)
{
	put_unaligned_le32((clock & 0x00ffffff) | ((uint32_t)flags << 24), word);
}

static inline uint32_t amdgpu_atom_clock_word_frequency(const void *word)
{
	return get_unaligned_le32(word) & 0x00ffffff;
}

static inline uint8_t amdgpu_atom_clock_word_flags(const void *word)
{
	return get_unaligned_le32(word) >> 24;
}

typedef uint32_t SMU_VoltageLevel;
#pragma pack(push,1)
struct sclkFcwRange_t {
	uint8_t  vco_setting;
	uint8_t  postdiv;
	uint16_t fcw_pcc;

	uint16_t fcw_trans_upper;
	uint16_t fcw_trans_lower;
};
typedef struct sclkFcwRange_t sclkFcwRange_t;
struct SMU_SclkSetting {
	uint32_t    SclkFrequency;
	uint16_t    Fcw_int;
	uint16_t    Fcw_frac;
	uint16_t    Pcc_fcw_int;
	uint8_t     PllRange;
	uint8_t     SSc_En;
	uint16_t    Sclk_slew_rate;
	uint16_t    Pcc_up_slew_rate;
	uint16_t    Pcc_down_slew_rate;
	uint16_t    Fcw1_int;
	uint16_t    Fcw1_frac;
	uint16_t    Sclk_ss_slew_rate;
};
typedef struct SMU_SclkSetting SMU_SclkSetting;
struct SMU74_Discrete_GraphicsLevel {
	SMU_VoltageLevel MinVoltage;
	uint8_t     pcieDpmLevel;
	uint8_t     DeepSleepDivId;
	uint16_t    ActivityLevel;
	uint32_t    CgSpllFuncCntl3;
	uint32_t    CgSpllFuncCntl4;
	uint32_t    CcPwrDynRm;
	uint32_t    CcPwrDynRm1;
	uint8_t     SclkDid;
	uint8_t     padding;
	uint8_t     EnabledForActivity;
	uint8_t     EnabledForThrottle;
	uint8_t     UpHyst;
	uint8_t     DownHyst;
	uint8_t     VoltageDownHyst;
	uint8_t     PowerThrottle;
	SMU_SclkSetting SclkSetting;
};
typedef struct SMU74_Discrete_GraphicsLevel SMU74_Discrete_GraphicsLevel;
struct SMU74_Discrete_MemoryLevel {
	SMU_VoltageLevel MinVoltage;
	uint32_t    MinMvdd;

	uint32_t    MclkFrequency;

	uint8_t     StutterEnable;
	uint8_t     EnabledForThrottle;
	uint8_t     EnabledForActivity;
	uint8_t     padding_0;

	uint8_t     UpHyst;
	uint8_t     DownHyst;
	uint8_t     VoltageDownHyst;
	uint8_t     padding_1;

	uint16_t    ActivityLevel;
	uint8_t     DisplayWatermark;
	uint8_t     Reserved;
};
typedef struct SMU74_Discrete_MemoryLevel SMU74_Discrete_MemoryLevel;
#pragma pack(pop)
struct pp_atomctrl_clock_dividers_ai {
	u16 usSclk_fcw_frac;
	u16  usSclk_fcw_int;
	u8   ucSclkPostDiv;
	u8   ucSclkVcoMode;
	u8   ucSclkPllRange;
	u8   ucSscEnable;
	u16  usSsc_fcw1_frac;
	u16  usSsc_fcw1_int;
	u16  usReserved;
	u16  usPcc_fcw_int;
	u16  usSsc_fcw_slew_frac;
	u16  usPcc_fcw_slew_frac;
};
typedef struct pp_atomctrl_clock_dividers_ai pp_atomctrl_clock_dividers_ai;

#define PHM_READ_FIELD(...) 0

struct phm_ppt_v1_clock_voltage_dependency_table {u32 tag;};
typedef struct phm_ppt_v1_clock_voltage_dependency_table phm_ppt_v1_clock_voltage_dependency_table;
struct phm_ppt_v1_information {phm_ppt_v1_clock_voltage_dependency_table *vdd_dep_on_sclk,*vdd_dep_on_mclk;};
struct profile {u32 sclk_activity,sclk_up_hyst,sclk_down_hyst,mclk_activity,mclk_up_hyst,mclk_down_hyst;};
struct timing {u32 min_clock_in_sr,num_existing_displays,vrefresh;};
struct smu7_hwmgr {struct profile current_profile_setting;struct timing display_timing;
 struct {phm_ppt_v1_clock_voltage_dependency_table vdd_dependency_on_sclk,vdd_dependency_on_mclk;} odn_dpm_table;
 u32 update_up_hyst,update_down_hyst,up_hyst,down_hyst;};
typedef struct {sclkFcwRange_t SclkFcwRangeTable[8];} SMU74_Discrete_DpmTable;
struct polaris10_smumgr {SMU74_Discrete_DpmTable smc_state_table;struct {u32 trans_lower_frequency,trans_upper_frequency;}range_table[8];};
struct atom_context {int unused;};
struct amdgpu_device {void*dev;struct {struct atom_context*atom_context;}mode_info;};
struct config {u32 min_core_set_clock_in_sr,num_display,vrefresh;};
struct pp_hwmgr {struct amdgpu_device*adev;void*backend,*smu_backend,*pptable,*device;bool od_enabled;u32 chip_id;struct config*display_config;struct {u32 platformCaps;}platform_descriptor;};
static int phm_cap_enabled(u32 caps,u32 cap){return !!(caps&cap);}
static u32 amdgpu_asic_get_xclk(struct amdgpu_device*a){(void)a;return 2700;}
static u32 smu7_get_sleep_divider_id_from_clock(u32 clock,u32 min){return clock>min?2:0;}
static int polaris10_get_dependency_volt_by_clk(struct pp_hwmgr*h,struct phm_ppt_v1_clock_voltage_dependency_table*t,u32 clock,SMU_VoltageLevel*v,u32*mvdd){(void)h;*v=(clock^0x1234abcd)+t->tag;*mvdd=(clock^0x76543210)+t->tag;return 0;}
static const struct {u32 clock;u16 integer,fraction;u8 range,ssc;} observed[]={{21400,34,15728,0,1},{33500,53,39321,0,1},{50300,40,15728,1,1},{69700,55,49807,1,1},{87400,34,62914,2,1},{101900,40,49807,2,1},{104300,41,47185,2,1},{107100,42,55050,2,1}};
static int atom_failure;static u32 last_request;
static void put_le16(void*p,u16 v){u8*b=p;b[0]=v;b[1]=v>>8;}
static int amdgpu_atom_execute_table(struct atom_context*c,int index,u32*buffer,int size) {
 (void)c;(void)index;(void)size;last_request=get_unaligned_le32(buffer);
 if(atom_failure)return -5;
 COMPUTE_GPU_CLOCK_OUTPUT_PARAMETERS_V1_7*p=(void*)buffer;
 unsigned k=0;while(k<8 && observed[k].clock!=(last_request&0xffffff))k++;if(k==8)return -5;
 put_le16(&p->usSclk_fcw_frac,observed[k].fraction);put_le16(&p->usSclk_fcw_int,observed[k].integer);
 p->ucSclkPostDiv=3;p->ucSclkVcoMode=1;p->ucSclkPllRange=observed[k].range;p->ucSscEnable=observed[k].ssc;
 put_le16(&p->usSsc_fcw1_frac,0x3456);put_le16(&p->usSsc_fcw1_int,0x4567);
 put_le16(&p->usPcc_fcw_int,0x5678);put_le16(&p->usSsc_fcw_slew_frac,0x6789);put_le16(&p->usPcc_fcw_slew_frac,0x789a);
 return 0;
}
static u8 ram[512];static u32 address;
#define mmSMC_IND_DATA_11 1
static int smu7_set_smc_sram_address(struct pp_hwmgr*h,u32 a,u32 limit){(void)h;if(a>=limit)return -EINVAL;address=a;return 0;}
static void cgs_write_register(void*d,u32 r,u32 v){(void)d;(void)r;ram[address]=v>>24;ram[address+1]=v>>16;ram[address+2]=v>>8;ram[address+3]=v;}
static u32 cgs_read_register(void*d,u32 r){(void)d;(void)r;return ((u32)ram[address]<<24)|((u32)ram[address+1]<<16)|((u32)ram[address+2]<<8)|ram[address+3];}
int atomctrl_get_engine_pll_dividers_ai(struct pp_hwmgr *hwmgr,
		uint32_t clock_value,
		pp_atomctrl_clock_dividers_ai *dividers)
{
	struct amdgpu_device *adev = hwmgr->adev;
	COMPUTE_GPU_CLOCK_OUTPUT_PARAMETERS_V1_7 pll_patameters;
	int result;

	amdgpu_atom_set_clock_word(&pll_patameters.ulClock, clock_value,
				COMPUTE_GPUCLK_INPUT_FLAG_SCLK);

	if (hwmgr->chip_id == CHIP_POLARIS11)
		pr_info("ATOM_CLOCK atomctrl_get_engine_pll_dividers_ai clock=%u request=%08x\n",
			clock_value, get_unaligned_le32(&pll_patameters.ulClock));

	result = PP_INIT_CALL(hwmgr, amdgpu_atom_execute_table(adev->mode_info.atom_context,
		 GetIndexIntoMasterTable(COMMAND, ComputeMemoryEnginePLL),
		(uint32_t *)&pll_patameters, sizeof(pll_patameters)));

	if (0 == result) {
		if (hwmgr->chip_id == CHIP_POLARIS11)
			pr_info("ATOM_CLOCK ai fcw_int=%u fcw_frac=%u pll_range=%u ssc=%u\n",
				le16_to_cpu(pll_patameters.usSclk_fcw_int),
				le16_to_cpu(pll_patameters.usSclk_fcw_frac),
				pll_patameters.ucSclkPllRange, pll_patameters.ucSscEnable);
		dividers->usSclk_fcw_frac     = le16_to_cpu(pll_patameters.usSclk_fcw_frac);
		dividers->usSclk_fcw_int      = le16_to_cpu(pll_patameters.usSclk_fcw_int);
		dividers->ucSclkPostDiv       = pll_patameters.ucSclkPostDiv;
		dividers->ucSclkVcoMode       = pll_patameters.ucSclkVcoMode;
		dividers->ucSclkPllRange      = pll_patameters.ucSclkPllRange;
		dividers->ucSscEnable         = pll_patameters.ucSscEnable;
		dividers->usSsc_fcw1_frac     = le16_to_cpu(pll_patameters.usSsc_fcw1_frac);
		dividers->usSsc_fcw1_int      = le16_to_cpu(pll_patameters.usSsc_fcw1_int);
		dividers->usPcc_fcw_int       = le16_to_cpu(pll_patameters.usPcc_fcw_int);
		dividers->usSsc_fcw_slew_frac = le16_to_cpu(pll_patameters.usSsc_fcw_slew_frac);
		dividers->usPcc_fcw_slew_frac = le16_to_cpu(pll_patameters.usPcc_fcw_slew_frac);
	}
	return result;
}
static int polaris10_calculate_sclk_params(struct pp_hwmgr *hwmgr,
		uint32_t clock, SMU_SclkSetting *sclk_setting)
{
	struct polaris10_smumgr *smu_data = (struct polaris10_smumgr *)(hwmgr->smu_backend);
	const SMU74_Discrete_DpmTable *table = &(smu_data->smc_state_table);
	struct pp_atomctrl_clock_dividers_ai dividers;
	uint32_t ref_clock;
	uint32_t pcc_target_percent, pcc_target_freq, ss_target_percent, ss_target_freq;
	uint8_t i;
	int result;
	uint64_t temp;

	sclk_setting->SclkFrequency = clock;
	/* get the engine clock dividers for this clock value */
	result = atomctrl_get_engine_pll_dividers_ai(hwmgr, clock,  &dividers);
	if (result == 0) {
		sclk_setting->Fcw_int = dividers.usSclk_fcw_int;
		sclk_setting->Fcw_frac = dividers.usSclk_fcw_frac;
		sclk_setting->Pcc_fcw_int = dividers.usPcc_fcw_int;
		sclk_setting->PllRange = dividers.ucSclkPllRange;
		sclk_setting->Sclk_slew_rate = 0x400;
		sclk_setting->Pcc_up_slew_rate = dividers.usPcc_fcw_slew_frac;
		sclk_setting->Pcc_down_slew_rate = 0xffff;
		sclk_setting->SSc_En = dividers.ucSscEnable;
		sclk_setting->Fcw1_int = dividers.usSsc_fcw1_int;
		sclk_setting->Fcw1_frac = dividers.usSsc_fcw1_frac;
		sclk_setting->Sclk_ss_slew_rate = dividers.usSsc_fcw_slew_frac;
		return result;
	}

	ref_clock = amdgpu_asic_get_xclk((struct amdgpu_device *)hwmgr->adev);

	for (i = 0; i < NUM_SCLK_RANGE; i++) {
		if (clock > smu_data->range_table[i].trans_lower_frequency
		&& clock <= smu_data->range_table[i].trans_upper_frequency) {
			sclk_setting->PllRange = i;
			break;
		}
	}

	sclk_setting->Fcw_int = (uint16_t)((clock << table->SclkFcwRangeTable[sclk_setting->PllRange].postdiv) / ref_clock);
	temp = clock << table->SclkFcwRangeTable[sclk_setting->PllRange].postdiv;
	temp <<= 0x10;
	do_div(temp, ref_clock);
	sclk_setting->Fcw_frac = temp & 0xffff;

	pcc_target_percent = 10; /*  Hardcode 10% for now. */
	pcc_target_freq = clock - (clock * pcc_target_percent / 100);
	sclk_setting->Pcc_fcw_int = (uint16_t)((pcc_target_freq << table->SclkFcwRangeTable[sclk_setting->PllRange].postdiv) / ref_clock);

	ss_target_percent = 2; /*  Hardcode 2% for now. */
	sclk_setting->SSc_En = 0;
	if (ss_target_percent) {
		sclk_setting->SSc_En = 1;
		ss_target_freq = clock - (clock * ss_target_percent / 100);
		sclk_setting->Fcw1_int = (uint16_t)((ss_target_freq << table->SclkFcwRangeTable[sclk_setting->PllRange].postdiv) / ref_clock);
		temp = ss_target_freq << table->SclkFcwRangeTable[sclk_setting->PllRange].postdiv;
		temp <<= 0x10;
		do_div(temp, ref_clock);
		sclk_setting->Fcw1_frac = temp & 0xffff;
	}

	return 0;
}
static int polaris10_populate_single_graphic_level(struct pp_hwmgr *hwmgr,
		uint32_t clock, struct SMU74_Discrete_GraphicsLevel *level)
{
	int result;
	/* PP_Clocks minClocks; */
	uint32_t mvdd;
	struct smu7_hwmgr *data = (struct smu7_hwmgr *)(hwmgr->backend);
	struct phm_ppt_v1_information *table_info =
			(struct phm_ppt_v1_information *)(hwmgr->pptable);
	SMU_SclkSetting curr_sclk_setting = { 0 };
	phm_ppt_v1_clock_voltage_dependency_table *vdd_dep_table = NULL;

	result = polaris10_calculate_sclk_params(hwmgr, clock, &curr_sclk_setting);

	if (hwmgr->od_enabled)
		vdd_dep_table = (phm_ppt_v1_clock_voltage_dependency_table *)&data->odn_dpm_table.vdd_dependency_on_sclk;
	else
		vdd_dep_table = table_info->vdd_dep_on_sclk;

	/* populate graphics levels */
	result = polaris10_get_dependency_volt_by_clk(hwmgr,
			vdd_dep_table, clock,
			&level->MinVoltage, &mvdd);

	PP_ASSERT_WITH_CODE((0 == result),
			"can not find VDDC voltage value for "
			"VDDC engine clock dependency table",
			return result);
	level->ActivityLevel = data->current_profile_setting.sclk_activity;

	level->CcPwrDynRm = 0;
	level->CcPwrDynRm1 = 0;
	level->EnabledForActivity = 0;
	level->EnabledForThrottle = 1;
	level->UpHyst = data->current_profile_setting.sclk_up_hyst;
	level->DownHyst = data->current_profile_setting.sclk_down_hyst;
	level->VoltageDownHyst = 0;
	level->PowerThrottle = 0;
	data->display_timing.min_clock_in_sr = hwmgr->display_config->min_core_set_clock_in_sr;

	if (phm_cap_enabled(hwmgr->platform_descriptor.platformCaps, PHM_PlatformCaps_SclkDeepSleep))
		level->DeepSleepDivId = smu7_get_sleep_divider_id_from_clock(clock,
								hwmgr->display_config->min_core_set_clock_in_sr);

	/* Default to slow, highest DPM level will be
	 * set to PPSMC_DISPLAY_WATERMARK_LOW later.
	 */
	if (data->update_up_hyst)
		level->UpHyst = (uint8_t)data->up_hyst;
	if (data->update_down_hyst)
		level->DownHyst = (uint8_t)data->down_hyst;

	level->SclkSetting = curr_sclk_setting;

	CONVERT_FROM_HOST_TO_SMC_UL(level->MinVoltage);
	CONVERT_FROM_HOST_TO_SMC_UL(level->CcPwrDynRm);
	CONVERT_FROM_HOST_TO_SMC_UL(level->CcPwrDynRm1);
	CONVERT_FROM_HOST_TO_SMC_US(level->ActivityLevel);
	CONVERT_FROM_HOST_TO_SMC_UL(level->SclkSetting.SclkFrequency);
	CONVERT_FROM_HOST_TO_SMC_US(level->SclkSetting.Fcw_int);
	CONVERT_FROM_HOST_TO_SMC_US(level->SclkSetting.Fcw_frac);
	CONVERT_FROM_HOST_TO_SMC_US(level->SclkSetting.Pcc_fcw_int);
	CONVERT_FROM_HOST_TO_SMC_US(level->SclkSetting.Sclk_slew_rate);
	CONVERT_FROM_HOST_TO_SMC_US(level->SclkSetting.Pcc_up_slew_rate);
	CONVERT_FROM_HOST_TO_SMC_US(level->SclkSetting.Pcc_down_slew_rate);
	CONVERT_FROM_HOST_TO_SMC_US(level->SclkSetting.Fcw1_int);
	CONVERT_FROM_HOST_TO_SMC_US(level->SclkSetting.Fcw1_frac);
	CONVERT_FROM_HOST_TO_SMC_US(level->SclkSetting.Sclk_ss_slew_rate);
	return 0;
}
static int polaris10_populate_single_memory_level(struct pp_hwmgr *hwmgr,
		uint32_t clock, struct SMU74_Discrete_MemoryLevel *mem_level)
{
	struct smu7_hwmgr *data = (struct smu7_hwmgr *)(hwmgr->backend);
	struct phm_ppt_v1_information *table_info =
			(struct phm_ppt_v1_information *)(hwmgr->pptable);
	int result = 0;
	uint32_t mclk_stutter_mode_threshold = 40000;
	phm_ppt_v1_clock_voltage_dependency_table *vdd_dep_table = NULL;


	if (hwmgr->od_enabled)
		vdd_dep_table = (phm_ppt_v1_clock_voltage_dependency_table *)&data->odn_dpm_table.vdd_dependency_on_mclk;
	else
		vdd_dep_table = table_info->vdd_dep_on_mclk;

	if (vdd_dep_table) {
		result = polaris10_get_dependency_volt_by_clk(hwmgr,
				vdd_dep_table, clock,
				&mem_level->MinVoltage, &mem_level->MinMvdd);
		PP_ASSERT_WITH_CODE((0 == result),
				"can not find MinVddc voltage value from memory "
				"VDDC voltage dependency table", return result);
	}

	mem_level->MclkFrequency = clock;
	mem_level->EnabledForThrottle = 1;
	mem_level->EnabledForActivity = 0;
	mem_level->UpHyst = data->current_profile_setting.mclk_up_hyst;
	mem_level->DownHyst = data->current_profile_setting.mclk_down_hyst;
	mem_level->VoltageDownHyst = 0;
	mem_level->ActivityLevel = data->current_profile_setting.mclk_activity;
	mem_level->StutterEnable = false;
	mem_level->DisplayWatermark = PPSMC_DISPLAY_WATERMARK_LOW;

	data->display_timing.num_existing_displays = hwmgr->display_config->num_display;
	data->display_timing.vrefresh = hwmgr->display_config->vrefresh;

	if (mclk_stutter_mode_threshold &&
		(clock <= mclk_stutter_mode_threshold) &&
		(PHM_READ_FIELD(hwmgr->device, DPG_PIPE_STUTTER_CONTROL,
				STUTTER_ENABLE) & 0x1) &&
		(data->display_timing.num_existing_displays <= 2) &&
		data->display_timing.num_existing_displays)
		mem_level->StutterEnable = true;

	if (!result) {
		CONVERT_FROM_HOST_TO_SMC_UL(mem_level->MinMvdd);
		CONVERT_FROM_HOST_TO_SMC_UL(mem_level->MclkFrequency);
		CONVERT_FROM_HOST_TO_SMC_US(mem_level->ActivityLevel);
		CONVERT_FROM_HOST_TO_SMC_UL(mem_level->MinVoltage);
	}
	return result;
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
int main(void) {
 struct amdgpu_device adev={0};struct smu7_hwmgr data={0};struct polaris10_smumgr smu={0};
 phm_ppt_v1_clock_voltage_dependency_table dep={7};struct phm_ppt_v1_information info={&dep,&dep};struct config cfg={10000,1,60};
 struct pp_hwmgr h={.adev=&adev,.backend=&data,.smu_backend=&smu,.pptable=&info,.display_config=&cfg,.chip_id=CHIP_POLARIS11};
 data.current_profile_setting=(struct profile){0x1234,3,4,0x5678,5,6};data.up_hyst=8;data.down_hyst=9;
 data.odn_dpm_table.vdd_dependency_on_sclk.tag=11;data.odn_dpm_table.vdd_dependency_on_mclk.tag=13;
 smu.range_table[0].trans_upper_frequency=0xffffffff;smu.smc_state_table.SclkFcwRangeTable[0].postdiv=1;
 u32 clocks[]={21400,33500,50300,69700,87400,101900,104300,107100};
 for(unsigned fail=0;fail<2;fail++)for(unsigned od=0;od<2;od++)for(unsigned deep=0;deep<2;deep++)for(unsigned hyst=0;hyst<4;hyst++)for(unsigned i=0;i<8;i++) {
  struct SMU74_Discrete_GraphicsLevel g={0};struct SMU74_Discrete_MemoryLevel m={0};
  atom_failure=fail;h.od_enabled=od;h.platform_descriptor.platformCaps=deep;data.update_up_hyst=hyst&1;data.update_down_hyst=hyst&2;
  if(polaris10_populate_single_graphic_level(&h,clocks[i],&g)||polaris10_populate_single_memory_level(&h,clocks[i],&m))return 1;
  if(last_request!=(clocks[i]|0x01000000))return 2;
  if(be32_to_cpu(g.SclkSetting.SclkFrequency)!=clocks[i]||be32_to_cpu(m.MclkFrequency)!=clocks[i])return 3;
  if(!fail&&(be16_to_cpu(g.SclkSetting.Fcw_int)!=observed[i].integer||be16_to_cpu(g.SclkSetting.Fcw_frac)!=observed[i].fraction||be16_to_cpu(g.SclkSetting.Pcc_up_slew_rate)!=0x789a||be16_to_cpu(g.SclkSetting.Sclk_ss_slew_rate)!=0x6789))return 4;
  if(be16_to_cpu(g.ActivityLevel)!=0x1234||be16_to_cpu(m.ActivityLevel)!=0x5678)return 5;
  if(be32_to_cpu(g.MinVoltage)!=(clocks[i]^0x1234abcd)+(od?11:7))return 6;
  if(be32_to_cpu(m.MinMvdd)!=(clocks[i]^0x76543210)+(od?13:7))return 7;
  if(smu7_copy_bytes_to_smc(&h,0,(u8*)&g,sizeof(g),512)||smu7_copy_bytes_to_smc(&h,128,(u8*)&m,sizeof(m),512))return 8;
  for(unsigned j=0;j<sizeof(g);j++)if(ram[j]!=((u8*)&g)[j])return 9;
  for(unsigned j=0;j<sizeof(m);j++)if(ram[128+j]!=((u8*)&m)[j])return 10;
  emit((char*)&g,sizeof(g));emit((char*)&m,sizeof(m));
 }
 return 0;
}
