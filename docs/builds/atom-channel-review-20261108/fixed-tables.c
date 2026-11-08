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


typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
typedef uint32_t SMU_VoltageLevel;
#if __BYTE_ORDER__ == __ORDER_BIG_ENDIAN__
#define cpu_to_be32(x) (x)
#define cpu_to_be16(x) (x)
#define cpu_to_le32(x) __builtin_bswap32(x)
#define ATOM_BIG_ENDIAN 1
#else
#define cpu_to_be32(x) __builtin_bswap32(x)
#define cpu_to_be16(x) __builtin_bswap16(x)
#define cpu_to_le32(x) (x)
#define ATOM_BIG_ENDIAN 0
#endif
#pragma pack(push, 1)
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
static const SMU74_Discrete_GraphicsLevel avfs_graphics_level_polaris10[8] __attribute__((used,section(".audit_gfx"))) = {
	/*  Min      pcie   DeepSleep Activity  CgSpll      CgSpll    CcPwr  CcPwr  Sclk         Enabled      Enabled                       Voltage    Power */
	/* Voltage, DpmLevel, DivId,  Level,  FuncCntl3,  FuncCntl4,  DynRm, DynRm1 Did, Padding,ForActivity, ForThrottle, UpHyst, DownHyst, DownHyst, Throttle */
	{ cpu_to_be32(0x46a40e10), 0x00, 0x03, cpu_to_be16(0x0032), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { cpu_to_be32(0x00007530), cpu_to_be16(0x0030), cpu_to_be16(0x0000), cpu_to_be16(0x0026), 0, 0, cpu_to_be16(0x0400), cpu_to_be16(0x028f), cpu_to_be16(0xffff), cpu_to_be16(0x002f), cpu_to_be16(0x0e30), cpu_to_be16(0x0027) } },
	{ cpu_to_be32(0x46a40e40), 0x01, 0x04, cpu_to_be16(0x0032), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { cpu_to_be32(0x00009c40), cpu_to_be16(0x0020), cpu_to_be16(0x0000), cpu_to_be16(0x001e), 1, 1, cpu_to_be16(0x0400), cpu_to_be16(0x0083), cpu_to_be16(0xffff), cpu_to_be16(0x001f), cpu_to_be16(0x5ecb), cpu_to_be16(0x001a) } },
	{ cpu_to_be32(0x46a40e74), 0x01, 0x00, cpu_to_be16(0x0032), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { cpu_to_be32(0x0000c350), cpu_to_be16(0x0028), cpu_to_be16(0x0000), cpu_to_be16(0x0020), 1, 1, cpu_to_be16(0x0400), cpu_to_be16(0x020c), cpu_to_be16(0xffff), cpu_to_be16(0x0027), cpu_to_be16(0x3364), cpu_to_be16(0x0021) } },
	{ cpu_to_be32(0x46a40ea4), 0x01, 0x00, cpu_to_be16(0x0032), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { cpu_to_be32(0x0000ea60), cpu_to_be16(0x0030), cpu_to_be16(0x0000), cpu_to_be16(0x0026), 1, 1, cpu_to_be16(0x0400), cpu_to_be16(0x028f), cpu_to_be16(0xffff), cpu_to_be16(0x002f), cpu_to_be16(0x0e30), cpu_to_be16(0x0027) } },
	{ cpu_to_be32(0x46a40ed8), 0x01, 0x00, cpu_to_be16(0x0032), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { cpu_to_be32(0x00011170), cpu_to_be16(0x0038), cpu_to_be16(0x0000), cpu_to_be16(0x002c), 1, 1, cpu_to_be16(0x0400), cpu_to_be16(0x0312), cpu_to_be16(0xffff), cpu_to_be16(0x0036), cpu_to_be16(0xe2c9), cpu_to_be16(0x002e) } },
	{ cpu_to_be32(0x46a40f3c), 0x01, 0x00, cpu_to_be16(0x0032), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { cpu_to_be32(0x00013880), cpu_to_be16(0x0020), cpu_to_be16(0x0000), cpu_to_be16(0x001e), 2, 1, cpu_to_be16(0x0400), cpu_to_be16(0x0083), cpu_to_be16(0xffff), cpu_to_be16(0x001f), cpu_to_be16(0x5ecb), cpu_to_be16(0x001a) } },
	{ cpu_to_be32(0x46a40f6c), 0x01, 0x00, cpu_to_be16(0x0032), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { cpu_to_be32(0x00015f90), cpu_to_be16(0x0024), cpu_to_be16(0x0000), cpu_to_be16(0x001e), 2, 1, cpu_to_be16(0x0400), cpu_to_be16(0x0189), cpu_to_be16(0xffff), cpu_to_be16(0x0023), cpu_to_be16(0x4c31), cpu_to_be16(0x001d) } },
	{ cpu_to_be32(0x46a40fa0), 0x01, 0x00, cpu_to_be16(0x0032), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), cpu_to_be32(0x00000000), 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { cpu_to_be32(0x000186a0), cpu_to_be16(0x0028), cpu_to_be16(0x0000), cpu_to_be16(0x0020), 2, 1, cpu_to_be16(0x0400), cpu_to_be16(0x020c), cpu_to_be16(0xffff), cpu_to_be16(0x0027), cpu_to_be16(0x3364), cpu_to_be16(0x0021) } }
};
static const SMU74_Discrete_MemoryLevel avfs_memory_level_polaris10 __attribute__((used,section(".audit_mem"))) = {
	cpu_to_be32(0x46a40e10), cpu_to_be32(0x00000000), cpu_to_be32(0x00007530), 0x01, 0x01, 0x01, 0x00, 0x00, 0x64, 0x00, 0x00, cpu_to_be16(0x001f), 0x00, 0x00};
const uint32_t audit_vr __attribute__((used,section(".audit_vr"))) = cpu_to_be32(0x00050001);
