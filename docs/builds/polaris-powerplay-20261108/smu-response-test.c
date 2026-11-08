
#ifdef FREESTANDING
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
#include "/base/work/gfx-postmap-review-20261107-001/source/include/uapi/asm-generic/errno.h"
#define printf(...) ((void)0)
#else
#include <stdint.h>
#include <errno.h>
#include <stdio.h>
#endif
struct amdgpu_device { void *dev; };
struct pp_hwmgr { struct amdgpu_device *adev; void *device; };
static int response, sent, writes;
#define PHM_WAIT_FIELD_UNEQUAL(...) 0
#define PHM_READ_FIELD(...) response
#define mmSMC_RESP_0 0
#define mmSMC_MESSAGE_0 1
#define dev_dbg(...) ((void)0)
#define dev_info(...) ((void)0)
static void cgs_write_register(void *dev, int reg, int value) {
    (void)dev; writes++; if (reg == mmSMC_MESSAGE_0) sent = value;
}
int old_send_msg(struct pp_hwmgr *hwmgr, uint16_t msg)
{
	struct amdgpu_device *adev = hwmgr->adev;
	int ret;

	PHM_WAIT_FIELD_UNEQUAL(hwmgr, SMC_RESP_0, SMC_RESP, 0);

	ret = PHM_READ_FIELD(hwmgr->device, SMC_RESP_0, SMC_RESP);

	if (ret == 0xFE)
		dev_dbg(adev->dev, "last message was not supported\n");
	else if (ret != 1)
		dev_info(adev->dev,
			"\nlast message was failed ret is %d\n", ret);

	cgs_write_register(hwmgr->device, mmSMC_RESP_0, 0);
	cgs_write_register(hwmgr->device, mmSMC_MESSAGE_0, msg);

	PHM_WAIT_FIELD_UNEQUAL(hwmgr, SMC_RESP_0, SMC_RESP, 0);

	ret = PHM_READ_FIELD(hwmgr->device, SMC_RESP_0, SMC_RESP);

	if (ret == 0xFE)
		dev_dbg(adev->dev, "message %x was not supported\n", msg);
	else if (ret != 1)
		dev_dbg(adev->dev,
			"failed to send message %x ret is %d \n",  msg, ret);

	return 0;
}
int smu7_send_msg_to_smc(struct pp_hwmgr *hwmgr, uint16_t msg)
{
	struct amdgpu_device *adev = hwmgr->adev;
	int ret;

	PHM_WAIT_FIELD_UNEQUAL(hwmgr, SMC_RESP_0, SMC_RESP, 0);

	cgs_write_register(hwmgr->device, mmSMC_RESP_0, 0);
	cgs_write_register(hwmgr->device, mmSMC_MESSAGE_0, msg);

	PHM_WAIT_FIELD_UNEQUAL(hwmgr, SMC_RESP_0, SMC_RESP, 0);

	ret = PHM_READ_FIELD(hwmgr->device, SMC_RESP_0, SMC_RESP);

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


int main(void) {
    struct amdgpu_device adev = {0};
    struct pp_hwmgr h = { &adev, 0 };
    const int values[] = {1, 0xfe, 0, 2, 0xffff};
    const int errors[] = {0, -EOPNOTSUPP, -EIO, -EIO, -ENXIO};
    for (unsigned i = 0; i < sizeof(values)/sizeof(values[0]); i++) {
        response = values[i]; writes = 0; sent = 0;
        int result = smu7_send_msg_to_smc(&h, 0x1234);
        if (result != errors[i] || writes != 2 || sent != 0x1234) return 1;
        int old = old_send_msg(&h, 0x1234);
        if (old != 0) return 2;
        printf("response=%#x legacy=%d corrected=%d PASS\n", response, old, result);
    }
    return 0;
}
#ifdef FREESTANDING
__asm__(".text\n.globl _start\n_start:\n"
        "bl main\nli 0,1\nsc\nb .\n");
#endif
