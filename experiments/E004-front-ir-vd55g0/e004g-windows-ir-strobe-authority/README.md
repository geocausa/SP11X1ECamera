# E004g — Windows IR strobe/illumination authority

Status: **PASS / offline only**.

This stage resolves why the final VD55G0 Windows configuration must not be replayed blindly.

The exact Surface PCFG contains the front-IR packed descriptor `0x01000110` at file offset `0x38`. Using field semantics already recovered from the exact installed `qccamplatform8380.sys`, it decodes to:

- front-facing;
- **flash present = 1**;
- flash index 0;
- flash/CCI timer index 0;
- **flash trigger type 0**;
- CCI0/master0;
- CSIPHY0;
- Face Authentication bit set;
- flash/shutter type 0.

The exact installed `qccamflash8380.sys` has distinct strobe-configuration branches. Trigger type 1 installs the `IRLED_CCI_Trigger_Callback` and uses the `CameraIRLED_Trigger` path. Trigger type 2 performs target-current/safety-timer setup. Other values enter the explicitly logged software-strobe fallback. Trigger type **0**, used by this SP11 IR slot, enters a separate hardware-strobe configuration path that programs flash/PMIC state and enables its low-level strobe control.

E004d proved the sensor's final 43-write Windows block contains exactly one GPIO1 strobe-selector write: `0x0468=0x02`. ST is used only as a naming dictionary for value 2 = STROBE; the register/value itself is Windows authority.

Therefore `0x0468=0x02` is treated as **illumination-coupled** and remains prohibited on Linux until its physical-light behavior in software standby is separately bounded.

The remaining **42 final Windows writes** contain no direct GPIO1 strobe-selector write and are the next safe configuration subset. They may be tested only in SW_STBY with CAMSS/V4L2/streaming/external illumination absent.

Unknown remains explicit: static Windows evidence does not prove whether merely selecting the strobe function in SW_STBY emits a physical pulse. No claim is made either way.
