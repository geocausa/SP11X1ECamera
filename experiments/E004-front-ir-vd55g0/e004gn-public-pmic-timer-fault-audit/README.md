# E004gn — published PM8550 flash timer and status evidence; local register mapping

**PASS OFFLINE SOURCE AUDIT / physical emitter safety BLOCKED.** This is step 1 of the autonomous follow-up: inspect public Linux/Qualcomm sources and the hash-pinned local four-channel PMIC flash driver; do not repeat a consumed Golden register read, Windows/KD capture, or emit any IR light.

## Public references and what they actually say

- Kernel PM8550 device tree: https://github.com/torvalds/linux/blob/master/arch/arm64/boot/dts/qcom/pm8550.dtsi — exposes a flash controller at offset 0xee00, disabled by default. This is a Linux IP block description, not a physical Surface LED wiring diagram.
- Public Qualcomm flash driver: https://codebrowser.dev/linux/linux/drivers/leds/flash/leds-qcom-flash.c.html — four-channel layout includes status3 offset 0x09, per-channel timer 0x3e..0x41, module enable 0x46, hardware-strobe selection 0x4a..0x4d, and channel enable 0x4e. Its fault-getter interprets channel-specific status3 bits as LED_FAULT_TIMEOUT. The source calls bit 7 of timer register an enable flag and describes 10 ms nominal steps. A software-reported timeout fault is not a measured physical pulse or guarantee that a held-high/retriggered strobe stays off.
- Qualcomm-author Linux flash driver submission: https://lkml.iu.edu/2302.0/02949.html — describes 3/4 channels and shared LED channels, with these register fields and software actions; it is not a PM8550 silicon electrical characterization or independent safety certification.
- Linux devicetree flash binding: https://github.com/torvalds/linux/blob/master/Documentation/devicetree/bindings/leds/qcom,spmi-flash-led.yaml — led-sources, flash-max-microamp and flash-max-timeout-us are **board-policy configuration** properties, not physical calibrated emitter measurements. The SP11 Golden PM8550 flash node has no child mapping and stays disabled. Do not populate it by guessing a safe current/timeout.
- 2025 Qualcomm-authored torch-current clamp fix: https://www.spinics.net/lists/kernel/msg5785237.html — describes a separate flash-current clamp **when the safety timer is disabled**, and a torch configuration update. This is not evidence that the enabled timer always terminates optical output on a stuck high strobe. The local isolated Linux source also declares REG_TORCH_CLAMP; do not mistake a current clamp for a validated optical exposure limit.

## Exact local reconciliation and next discriminating question

The hash-pinned isolated four-channel driver maps STATUS3 to offset 0x09. **Conditional** on the earlier SP11 candidate PM8550 flash base of 0xee00/SID1, that yields candidate SPMI address 0xee09. The existing four-channel fault getter tests bit 0 for source 1 and bit 6 for source 4, the channel pair whose software control writes were recorded during the consumed E004gb Windows helper trace. E004fx previously observed timer config bytes 0x93 at idle and E004fy observed module and channel OFF; the read identities are consumed and **must not be repeated**. No STATUS3 value or fault-latch behavior has been measured by E004gn.

A **separately planned, strictly bounded passive STATUS3 observation** may in future help identify a software-visible timeout-fault indication, but first establish whether the relevant fault bits are latched, clear-on-read, and safe to observe without altering state; do not do speculative register sweeps or infer physical cutoff from a status bit. The more consequential missing distinctions remain: timer starts on WHICH edge, whether held-high or retriggering can restart it, whether firmware/another PMIC independently forces module OFF on host failure, and the assembled emitter's actual current/irradiance. The available public driver, devicetree and OEM source do **not** answer these physical questions.

Run from repository root:

    python3 experiments/E004-front-ir-vd55g0/e004gn-public-pmic-timer-fault-audit/verify_static.py
    python3 experiments/E004-front-ir-vd55g0/e004gn-public-pmic-timer-fault-audit/test_static.py

The verifier pins and parses the *already archived* isolated Linux source and previously consumed idle result, emits a non-image summary, and rejects nine mutated status/register/source/evidence fixtures. It does not access /dev/spmi, i2c, camera, LED sysfs, Windows, KDNET or firmware; Golden and login untouched. **No new hardware timer guarantee or emitter permission has been established.**
