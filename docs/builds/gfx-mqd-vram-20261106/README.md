# Compute descriptor VRAM placement experiment

BE Polaris11 only, amdgpu_gfx_mqd_sw_init domain changes GTT->VRAM. Require
VRAM (no silent GTT fallback) to make placement evidence unambiguous. KIQ already
uses VRAM. Existing normal queue/graphics tests remain; no parser/ring bypass.
Native CPU staging/publication from previous candidate retained, so this changes
one allocation choice. Upstream default keeps pre-gfx10 compute MQDs in GTT.
Test distinguishes descriptor location/consumer access; it does not by itself
prove a general PCIe/GART or cache-coherency diagnosis.
Fresh R730 gfx-mqd-vram-20261106-001, same pinned6.12.113/source config/patch
chain,4CPU/6GiB/network-none. Build/physical acceptance pending.

Build completed exit0; accepted modular003 .config and Module.symvers byte matches. Module SHA25649e956e9a0655da97ea2db7458c572a8626b4c89fd6180fcf22572a33cd86b99. Retrieved local ignored artifact amdgpu-gfx-mqd-vram.ko. Ready for cold boot test; hardware unverified.

## Physical result

Booted expected kernel/no modules after temporary U-Boot linuxboot command;
module hash verified, rootro, off-board capture. All8 compute publication logs
confirm VRAM addressesf400383000..f400392000, vram1. Control-ring self-test0;
mapping submitted, same PCIe00800000/23 storm and SSH loss. No compute/display
acceptance. Changing MQD placement alone does not fix this failure; do not carry
placement override forward as an accepted fix. New readback candidate returns
to native-staging002 allocation policy so VRAM and GTT descriptors can be compared.
User describes cyan screen; no verified framebuffer/mode acceptance.
