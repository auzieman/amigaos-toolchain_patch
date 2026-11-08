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
	{ 0x100ea446, 0x00, 0x03, 0x3200, 0, 0, 0, 0, 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { 0x30750000, 0x3000, 0, 0x2600, 0, 0, 0x0004, 0x8f02, 0xffff, 0x2f00, 0x300e, 0x2700 } },
	{ 0x400ea446, 0x01, 0x04, 0x3200, 0, 0, 0, 0, 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { 0x409c0000, 0x2000, 0, 0x1e00, 1, 1, 0x0004, 0x8300, 0xffff, 0x1f00, 0xcb5e, 0x1a00 } },
	{ 0x740ea446, 0x01, 0x00, 0x3200, 0, 0, 0, 0, 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { 0x50c30000, 0x2800, 0, 0x2000, 1, 1, 0x0004, 0x0c02, 0xffff, 0x2700, 0x6433, 0x2100 } },
	{ 0xa40ea446, 0x01, 0x00, 0x3200, 0, 0, 0, 0, 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { 0x60ea0000, 0x3000, 0, 0x2600, 1, 1, 0x0004, 0x8f02, 0xffff, 0x2f00, 0x300e, 0x2700 } },
	{ 0xd80ea446, 0x01, 0x00, 0x3200, 0, 0, 0, 0, 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { 0x70110100, 0x3800, 0, 0x2c00, 1, 1, 0x0004, 0x1203, 0xffff, 0x3600, 0xc9e2, 0x2e00 } },
	{ 0x3c0fa446, 0x01, 0x00, 0x3200, 0, 0, 0, 0, 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { 0x80380100, 0x2000, 0, 0x1e00, 2, 1, 0x0004, 0x8300, 0xffff, 0x1f00, 0xcb5e, 0x1a00 } },
	{ 0x6c0fa446, 0x01, 0x00, 0x3200, 0, 0, 0, 0, 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { 0x905f0100, 0x2400, 0, 0x1e00, 2, 1, 0x0004, 0x8901, 0xffff, 0x2300, 0x314c, 0x1d00 } },
	{ 0xa00fa446, 0x01, 0x00, 0x3200, 0, 0, 0, 0, 0, 0, 0x01, 0x01, 0x0a, 0x00, 0x00, 0x00, { 0xa0860100, 0x2800, 0, 0x2000, 2, 1, 0x0004, 0x0c02, 0xffff, 0x2700, 0x6433, 0x2100 } }
};
static const SMU74_Discrete_MemoryLevel avfs_memory_level_polaris10 __attribute__((used,section(".audit_mem"))) = {
	0x100ea446, 0, 0x30750000, 0x01, 0x01, 0x01, 0x00, 0x00, 0x64, 0x00, 0x00, 0x1f00, 0x00, 0x00};
const uint32_t audit_vr __attribute__((used,section(".audit_vr"))) = 0x01000500;
