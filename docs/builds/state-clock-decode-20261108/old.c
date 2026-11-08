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


#define NULL ((void*)0)
#pragma pack(push,1)
typedef struct _ATOM_Tonga_POWERPLAYTABLE {
	ATOM_COMMON_TABLE_HEADER sHeader;

	UCHAR  ucTableRevision;
	USHORT usTableSize;						/*the size of header structure */

	ULONG	ulGoldenPPID;
	ULONG	ulGoldenRevision;
	USHORT	usFormatID;

	USHORT	usVoltageTime;					 /*in microseconds */
	ULONG	ulPlatformCaps;					  /*See ATOM_Tonga_CAPS_* */

	ULONG	ulMaxODEngineClock; 			   /*For Overdrive.  */
	ULONG	ulMaxODMemoryClock; 			   /*For Overdrive. */

	USHORT	usPowerControlLimit;
	USHORT	usUlvVoltageOffset;				  /*in mv units */

	USHORT	usStateArrayOffset;				  /*points to ATOM_Tonga_State_Array */
	USHORT	usFanTableOffset;				  /*points to ATOM_Tonga_Fan_Table */
	USHORT	usThermalControllerOffset;		   /*points to ATOM_Tonga_Thermal_Controller */
	USHORT	usReserv;						   /*CustomThermalPolicy removed for Tonga. Keep this filed as reserved. */

	USHORT	usMclkDependencyTableOffset;	   /*points to ATOM_Tonga_MCLK_Dependency_Table */
	USHORT	usSclkDependencyTableOffset;	   /*points to ATOM_Tonga_SCLK_Dependency_Table */
	USHORT	usVddcLookupTableOffset;		   /*points to ATOM_Tonga_Voltage_Lookup_Table */
	USHORT	usVddgfxLookupTableOffset; 		/*points to ATOM_Tonga_Voltage_Lookup_Table */

	USHORT	usMMDependencyTableOffset;		  /*points to ATOM_Tonga_MM_Dependency_Table */

	USHORT	usVCEStateTableOffset;			   /*points to ATOM_Tonga_VCE_State_Table; */

	USHORT	usPPMTableOffset;				  /*points to ATOM_Tonga_PPM_Table */
	USHORT	usPowerTuneTableOffset;			  /*points to ATOM_PowerTune_Table */

	USHORT	usHardLimitTableOffset; 		   /*points to ATOM_Tonga_Hard_Limit_Table */

	USHORT	usPCIETableOffset;				  /*points to ATOM_Tonga_PCIE_Table */

	USHORT	usGPIOTableOffset;				  /*points to ATOM_Tonga_GPIO_Table */

	USHORT	usReserved[6];					   /*TODO: modify reserved size to fit structure aligning */
} ATOM_Tonga_POWERPLAYTABLE;
typedef struct _ATOM_Tonga_State {
	UCHAR  ucEngineClockIndexHigh;
	UCHAR  ucEngineClockIndexLow;

	UCHAR  ucMemoryClockIndexHigh;
	UCHAR  ucMemoryClockIndexLow;

	UCHAR  ucPCIEGenLow;
	UCHAR  ucPCIEGenHigh;

	UCHAR  ucPCIELaneLow;
	UCHAR  ucPCIELaneHigh;

	USHORT usClassification;
	ULONG ulCapsAndSettings;
	USHORT usClassification2;
	UCHAR  ucUnused[4];
} ATOM_Tonga_State;
typedef struct _ATOM_Tonga_MCLK_Dependency_Record {
	UCHAR  ucVddcInd;	/* Vddc voltage */
	USHORT usVddci;
	USHORT usVddgfxOffset;	/* Offset relative to Vddc voltage */
	USHORT usMvdd;
	ULONG ulMclk;
	USHORT usReserved;
} ATOM_Tonga_MCLK_Dependency_Record;
typedef struct _ATOM_Tonga_MCLK_Dependency_Table {
	UCHAR ucRevId;
	UCHAR ucNumEntries;
	ATOM_Tonga_MCLK_Dependency_Record entries[] __counted_by(ucNumEntries);
} ATOM_Tonga_MCLK_Dependency_Table;
typedef struct _ATOM_Tonga_SCLK_Dependency_Record {
	UCHAR  ucVddInd;											/* Base voltage */
	USHORT usVddcOffset;										/* Offset relative to base voltage */
	ULONG ulSclk;
	USHORT usEdcCurrent;
	UCHAR  ucReliabilityTemperature;
	UCHAR  ucCKSVOffsetandDisable;							  /* Bits 0~6: Voltage offset for CKS, Bit 7: Disable/enable for the SCLK level. */
} ATOM_Tonga_SCLK_Dependency_Record;
typedef struct _ATOM_Tonga_SCLK_Dependency_Table {
	UCHAR ucRevId;
	UCHAR ucNumEntries;
	ATOM_Tonga_SCLK_Dependency_Record entries[] __counted_by(ucNumEntries);
} ATOM_Tonga_SCLK_Dependency_Table;
typedef struct _ATOM_Polaris_SCLK_Dependency_Record {
	UCHAR  ucVddInd;											/* Base voltage */
	USHORT usVddcOffset;										/* Offset relative to base voltage */
	ULONG ulSclk;
	USHORT usEdcCurrent;
	UCHAR  ucReliabilityTemperature;
	UCHAR  ucCKSVOffsetandDisable;			/* Bits 0~6: Voltage offset for CKS, Bit 7: Disable/enable for the SCLK level. */
	ULONG  ulSclkOffset;
} ATOM_Polaris_SCLK_Dependency_Record;
typedef struct _ATOM_Polaris_SCLK_Dependency_Table {
	UCHAR ucRevId;
	UCHAR ucNumEntries;
	ATOM_Polaris_SCLK_Dependency_Record entries[] __counted_by(ucNumEntries);
} ATOM_Polaris_SCLK_Dependency_Table;
typedef struct _PPTable_Generic_SubTable_Header {
	UCHAR  ucRevId;
} PPTable_Generic_SubTable_Header;
#pragma pack(pop)
#define ATOM_Tonga_DISALLOW_ON_DC                       0x00004000
#define ATOM_Tonga_ENABLE_VARIBRIGHT                    0x00008000

#define PP_ASSERT_WITH_CODE(test,msg,action) do {if(!(test)){action;}}while(0)
#define SMU_MAX_LEVELS_GRAPHICS 0
#define DPMTABLE_OD_UPDATE_SCLK 1
#define DPMTABLE_OD_UPDATE_MCLK 2
#define DPMTABLE_UPDATE_SCLK 4
#define DPMTABLE_UPDATE_MCLK 8
#define SMU7_MINIMUM_ENGINE_CLOCK 10000
struct smu7_performance_level {u32 engine_clock,memory_clock,pcie_gen,pcie_lane;};
struct smu7_power_state {unsigned performance_level_count;struct smu7_performance_level performance_levels[8];};
struct pp_power_state {struct smu7_power_state hardware;
 struct {u32 ui_label,flags;bool temporary_state,to_be_deleted;}classification;
 struct {bool disallowOnDC;u32 supportedPowerLevels;}validation;
 struct {u32 lanes;}pcie;
 struct {bool disableFrameModulation,limitRefreshrate,enableVariBright;}display;
 struct {u32 VCLK,DCLK;}uvd_clocks;struct {u32 min,max;}temperatures;};
struct smu7_single_dpm_table {unsigned count;struct {u32 value;bool enabled;}dpm_levels[8];};
struct smu7_hwmgr {u32 pcie_gen_cap,pcie_lane_cap,need_update_smu7_dpm_table;
 struct {struct smu7_single_dpm_table sclk_table,mclk_table;}dpm_table;
 struct {u32 min_clock_in_sr,num_existing_displays;}display_timing;};
struct pp_hwmgr {void*backend;bool od_enabled;struct {unsigned hardwareActivityPerformanceLevels;}platform_descriptor;struct {unsigned num_display;}*display_config;};
struct phm_set_power_state_input {const struct smu7_power_state*pnew_state;};
struct PP_Clocks {u32 engineClockInSR;};
static const struct smu7_power_state*cast_const_phw_smu7_power_state(const struct smu7_power_state*p){return p;}
static u32 get_pcie_gen_support(u32 caps,u32 value){(void)caps;return value;}
static u32 get_pcie_lane_support(u32 caps,u32 value){(void)caps;return value;}
static unsigned smum_get_mac_definition(struct pp_hwmgr*h,unsigned type){(void)h;(void)type;return 8;}
static void put16(void*p,u16 v){u8*b=p;b[0]=v;b[1]=v>>8;}
static unsigned mask(const struct smu7_single_dpm_table*t){unsigned m=0;for(unsigned i=0;i<t->count;i++)if(t->dpm_levels[i].enabled)m|=1<<i;return m;}
static int smu7_get_pp_table_entry_callback_func_v1(struct pp_hwmgr *hwmgr,
		void *state, struct pp_power_state *power_state,
		void *pp_table, uint32_t classification_flag)
{
	struct smu7_hwmgr *data = (struct smu7_hwmgr *)(hwmgr->backend);
	struct smu7_power_state  *smu7_power_state =
			(struct smu7_power_state *)(&(power_state->hardware));
	struct smu7_performance_level *performance_level;
	ATOM_Tonga_State *state_entry = (ATOM_Tonga_State *)state;
	ATOM_Tonga_POWERPLAYTABLE *powerplay_table =
			(ATOM_Tonga_POWERPLAYTABLE *)pp_table;
	PPTable_Generic_SubTable_Header *sclk_dep_table =
			(PPTable_Generic_SubTable_Header *)
			(((unsigned long)powerplay_table) +
				le16_to_cpu(powerplay_table->usSclkDependencyTableOffset));

	ATOM_Tonga_MCLK_Dependency_Table *mclk_dep_table =
			(ATOM_Tonga_MCLK_Dependency_Table *)
			(((unsigned long)powerplay_table) +
				le16_to_cpu(powerplay_table->usMclkDependencyTableOffset));

	/* The following fields are not initialized here: id orderedList allStatesList */
	power_state->classification.ui_label =
			(le16_to_cpu(state_entry->usClassification) &
			ATOM_PPLIB_CLASSIFICATION_UI_MASK) >>
			ATOM_PPLIB_CLASSIFICATION_UI_SHIFT;
	power_state->classification.flags = classification_flag;
	/* NOTE: There is a classification2 flag in BIOS that is not being used right now */

	power_state->classification.temporary_state = false;
	power_state->classification.to_be_deleted = false;

	power_state->validation.disallowOnDC =
			(0 != (le32_to_cpu(state_entry->ulCapsAndSettings) &
					ATOM_Tonga_DISALLOW_ON_DC));

	power_state->pcie.lanes = 0;

	power_state->display.disableFrameModulation = false;
	power_state->display.limitRefreshrate = false;
	power_state->display.enableVariBright =
			(0 != (le32_to_cpu(state_entry->ulCapsAndSettings) &
					ATOM_Tonga_ENABLE_VARIBRIGHT));

	power_state->validation.supportedPowerLevels = 0;
	power_state->uvd_clocks.VCLK = 0;
	power_state->uvd_clocks.DCLK = 0;
	power_state->temperatures.min = 0;
	power_state->temperatures.max = 0;

	performance_level = &(smu7_power_state->performance_levels
			[smu7_power_state->performance_level_count++]);

	PP_ASSERT_WITH_CODE(
			(smu7_power_state->performance_level_count < smum_get_mac_definition(hwmgr, SMU_MAX_LEVELS_GRAPHICS)),
			"Performance levels exceeds SMC limit!",
			return -EINVAL);

	PP_ASSERT_WITH_CODE(
			(smu7_power_state->performance_level_count <
					hwmgr->platform_descriptor.hardwareActivityPerformanceLevels),
			"Performance levels exceeds Driver limit!",
			return -EINVAL);

	/* Performance levels are arranged from low to high. */
	performance_level->memory_clock = mclk_dep_table->entries
			[state_entry->ucMemoryClockIndexLow].ulMclk;
	if (sclk_dep_table->ucRevId == 0)
		performance_level->engine_clock = ((ATOM_Tonga_SCLK_Dependency_Table *)sclk_dep_table)->entries
			[state_entry->ucEngineClockIndexLow].ulSclk;
	else if (sclk_dep_table->ucRevId == 1)
		performance_level->engine_clock = ((ATOM_Polaris_SCLK_Dependency_Table *)sclk_dep_table)->entries
			[state_entry->ucEngineClockIndexLow].ulSclk;
	performance_level->pcie_gen = get_pcie_gen_support(data->pcie_gen_cap,
			state_entry->ucPCIEGenLow);
	performance_level->pcie_lane = get_pcie_lane_support(data->pcie_lane_cap,
			state_entry->ucPCIELaneLow);

	performance_level = &(smu7_power_state->performance_levels
			[smu7_power_state->performance_level_count++]);
	performance_level->memory_clock = mclk_dep_table->entries
			[state_entry->ucMemoryClockIndexHigh].ulMclk;

	if (sclk_dep_table->ucRevId == 0)
		performance_level->engine_clock = ((ATOM_Tonga_SCLK_Dependency_Table *)sclk_dep_table)->entries
			[state_entry->ucEngineClockIndexHigh].ulSclk;
	else if (sclk_dep_table->ucRevId == 1)
		performance_level->engine_clock = ((ATOM_Polaris_SCLK_Dependency_Table *)sclk_dep_table)->entries
			[state_entry->ucEngineClockIndexHigh].ulSclk;

	performance_level->pcie_gen = get_pcie_gen_support(data->pcie_gen_cap,
			state_entry->ucPCIEGenHigh);
	performance_level->pcie_lane = get_pcie_lane_support(data->pcie_lane_cap,
			state_entry->ucPCIELaneHigh);

	return 0;
}static int smu7_find_dpm_states_clocks_in_dpm_table(struct pp_hwmgr *hwmgr, const void *input)
{
	const struct phm_set_power_state_input *states =
			(const struct phm_set_power_state_input *)input;
	const struct smu7_power_state *smu7_ps =
			cast_const_phw_smu7_power_state(states->pnew_state);
	struct smu7_hwmgr *data = (struct smu7_hwmgr *)(hwmgr->backend);
	struct smu7_single_dpm_table *sclk_table = &(data->dpm_table.sclk_table);
	uint32_t sclk = smu7_ps->performance_levels
			[smu7_ps->performance_level_count - 1].engine_clock;
	struct smu7_single_dpm_table *mclk_table = &(data->dpm_table.mclk_table);
	uint32_t mclk = smu7_ps->performance_levels
			[smu7_ps->performance_level_count - 1].memory_clock;
	struct PP_Clocks min_clocks = {0};
	uint32_t i;

	for (i = 0; i < sclk_table->count; i++) {
		if (sclk == sclk_table->dpm_levels[i].value)
			break;
	}

	if (i >= sclk_table->count) {
		if (sclk > sclk_table->dpm_levels[i-1].value) {
			data->need_update_smu7_dpm_table |= DPMTABLE_OD_UPDATE_SCLK;
			sclk_table->dpm_levels[i-1].value = sclk;
		}
	} else {
	/* TODO: Check SCLK in DAL's minimum clocks
	 * in case DeepSleep divider update is required.
	 */
		if (data->display_timing.min_clock_in_sr != min_clocks.engineClockInSR &&
			(min_clocks.engineClockInSR >= SMU7_MINIMUM_ENGINE_CLOCK ||
				data->display_timing.min_clock_in_sr >= SMU7_MINIMUM_ENGINE_CLOCK))
			data->need_update_smu7_dpm_table |= DPMTABLE_UPDATE_SCLK;
	}

	for (i = 0; i < mclk_table->count; i++) {
		if (mclk == mclk_table->dpm_levels[i].value)
			break;
	}

	if (i >= mclk_table->count) {
		if (mclk > mclk_table->dpm_levels[i-1].value) {
			data->need_update_smu7_dpm_table |= DPMTABLE_OD_UPDATE_MCLK;
			mclk_table->dpm_levels[i-1].value = mclk;
		}
	}

	if (data->display_timing.num_existing_displays != hwmgr->display_config->num_display)
		data->need_update_smu7_dpm_table |= DPMTABLE_UPDATE_MCLK;

	return 0;
}static int smu7_trim_single_dpm_states(struct pp_hwmgr *hwmgr,
			  struct smu7_single_dpm_table *dpm_table,
			uint32_t low_limit, uint32_t high_limit)
{
	uint32_t i;

	/* force the trim if mclk_switching is disabled to prevent flicker */
	bool force_trim = (low_limit == high_limit);
	for (i = 0; i < dpm_table->count; i++) {
	/*skip the trim if od is enabled*/
		if ((!hwmgr->od_enabled || force_trim)
			&& (dpm_table->dpm_levels[i].value < low_limit
			|| dpm_table->dpm_levels[i].value > high_limit))
			dpm_table->dpm_levels[i].enabled = false;
		else
			dpm_table->dpm_levels[i].enabled = true;
	}

	return 0;
}
#define FIXED 0

int main(void) {
 u32 clocks[]={21400,33500,50300,69700,87400,101900,104300,107100};
 u8 blob[2048]={0};ATOM_Tonga_POWERPLAYTABLE*pp=(void*)blob;
 put16(&pp->usSclkDependencyTableOffset,256);put16(&pp->usMclkDependencyTableOffset,1024);
 ATOM_Tonga_MCLK_Dependency_Table*mem=(void*)(blob+1024);mem->ucNumEntries=8;
 for(unsigned i=0;i<8;i++)put_unaligned_le32(30000+i*10000,&mem->entries[i].ulMclk);
 for(unsigned rev=0;rev<2;rev++) {
  PPTable_Generic_SubTable_Header*hdr=(void*)(blob+256);hdr->ucRevId=rev;
  for(unsigned i=0;i<8;i++) {
   if(rev==0)put_unaligned_le32(clocks[i],&((ATOM_Tonga_SCLK_Dependency_Table*)hdr)->entries[i].ulSclk);
   else put_unaligned_le32(clocks[i],&((ATOM_Polaris_SCLK_Dependency_Table*)hdr)->entries[i].ulSclk);
  }
  for(unsigned lo=0;lo<8;lo++)for(unsigned hi=lo;hi<8;hi++) {
   ATOM_Tonga_State raw={0};raw.ucEngineClockIndexLow=lo;raw.ucEngineClockIndexHigh=hi;raw.ucMemoryClockIndexLow=lo;raw.ucMemoryClockIndexHigh=hi;
   struct pp_power_state state={0};struct smu7_hwmgr data={0};
   struct pp_hwmgr h={.backend=&data,.platform_descriptor={8}};typeof(*h.display_config)config={0};h.display_config=&config;
   if(smu7_get_pp_table_entry_callback_func_v1(&h,&raw,&state,pp,0))return 1;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
   u32 low=FIXED?clocks[lo]:__builtin_bswap32(clocks[lo]);u32 high=FIXED?clocks[hi]:__builtin_bswap32(clocks[hi]);
#else
   u32 low=clocks[lo],high=clocks[hi];
#endif
   if(state.hardware.performance_levels[0].engine_clock!=low||state.hardware.performance_levels[1].engine_clock!=high)return 2;
   u32 ml=30000+lo*10000,mh=30000+hi*10000;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
   if(!FIXED){ml=__builtin_bswap32(ml);mh=__builtin_bswap32(mh);}
#endif
   if(state.hardware.performance_levels[0].memory_clock!=ml||state.hardware.performance_levels[1].memory_clock!=mh)return 6;
   for(unsigned i=0;i<8;i++){data.dpm_table.sclk_table.dpm_levels[i].value=clocks[i];data.dpm_table.mclk_table.dpm_levels[i].value=30000+i*10000;}
   data.dpm_table.sclk_table.count=8;data.dpm_table.mclk_table.count=8;
   struct phm_set_power_state_input input={&state.hardware};
   if(smu7_find_dpm_states_clocks_in_dpm_table(&h,&input))return 3;
   smu7_trim_single_dpm_states(&h,&data.dpm_table.sclk_table,low,high);
   smu7_trim_single_dpm_states(&h,&data.dpm_table.mclk_table,ml,mh);
   hex(rev);hex(lo);hex(hi);hex(low);hex(high);hex(data.dpm_table.sclk_table.dpm_levels[7].value);hex(mask(&data.dpm_table.sclk_table));hex(ml);hex(mh);hex(data.dpm_table.mclk_table.dpm_levels[7].value);hex(mask(&data.dpm_table.mclk_table));emit("\n",1);
   if(FIXED || __BYTE_ORDER__ != __ORDER_BIG_ENDIAN__) {
    unsigned expected=((1u<<(hi+1))-1)&~((1u<<lo)-1);
    if(mask(&data.dpm_table.sclk_table)!=expected||data.dpm_table.sclk_table.dpm_levels[7].value!=107100)return 4;
    if(mask(&data.dpm_table.mclk_table)!=expected||data.dpm_table.mclk_table.dpm_levels[7].value!=100000)return 7;
   }
  }
 }
 return 0;
}
