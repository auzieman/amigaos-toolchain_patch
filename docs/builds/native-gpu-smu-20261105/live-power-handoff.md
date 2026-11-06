# Live power and display handoff probe

Read-only SSH probe on the running A1222, 2026-11-05. No GPU reset, PCI configuration writes, driver rebind, firmware changes or reboot performed.

Radeon 0001:01:00.0 reports power_state D0, power/control on, runtime_status active, runtime_suspended_time 0 and boot_vga 1. No driver is bound. PCI enable is 0 after probe failure; this observation does not establish the state during initialization or justify writing enable manually. BAR resources remain assigned. No registered framebuffer exists: /proc/fb is empty, /sys/class/graphics contains only fbcon, and /sys/class/drm contains only version.

Device-tree chosen/linux,stdout-path names /soc@fffe00000/display@10000 (the onboard DIU), whereas the captured physical screen is Radeon HDMI. The platform device fffe10000.display exists, compatible fsl,diu and fsl,p1022-diu, but has no bound driver. No fsl-diu-fb driver directory was found. The board patch explicitly describes its initial serial/PCI slice as lacking DIU board hooks. An enabled generic CONFIG_FB_FSL_DIU is therefore not proof of usable onboard display support. No DIU initialization attempted.

Conclusion: no evidence that PCI runtime suspension explains the Radeon failure. Existing complete earlier logs remain authoritative for the SMU startup failure; the current dmesg ring has wrapped and retains only the final -22 probe error. Firmware stdout metadata does not provide a Linux framebuffer handoff automatically. Audit native SMU initialization and board display support separately. No confirmed fix or graphical acceptance.
