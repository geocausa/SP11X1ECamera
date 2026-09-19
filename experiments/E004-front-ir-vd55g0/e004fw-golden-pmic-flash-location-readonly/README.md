# E004fw — live Golden flash-PMIC location (read-only metadata)

Status: **PASS — real SP11 Linux Golden device-tree and SPMI metadata; no PMIC registers read and no emitted light**. This is a fresh *metadata-only* experiment. E004ft, E004fu and all earlier one-shot capture identities remain consumed. No camera boot, firmware, module, flash driver or optical hardware was altered.

## Observed mapping and limits

On protected Golden v19c, the live device tree contains exactly one `led-controller@ee00` below `/soc@0/arbiter@c400000/spmi@c42d000/pmic@1`. Its parent declares `qcom,pm8550`; its own compatible strings are `qcom,pm8550-flash-led` and `qcom,spmi-flash-led`, base `0xee00`, and **status=disabled**. The live SPMI node is `/sys/bus/spmi/devices/0-01` with `pmic-spmi` driver and matching parent DT node. Read-only debugfs metadata names regmap `0-01` `pmic-spmi` with range `0-ffff`. The separate PMCs at SPMI IDs 3, 4, 5 and 6 declare `qcom,pmc8380`; they are **not** the PM8550 flash-controller parent. On this Golden boot no camera devices are active.

Combining the *Linux flash-controller node's* base 0xee00 with its already reviewed four-channel driver offset table suggests candidate per-channel flash timer **addresses** 0xee3e–0xee41 on **SPMI 0-01**, rather than blindly reading the other PMC8380 device IDs. This is DT+driver address arithmetic; it **does not** prove actual Surface IR LED physical wiring or that any timer is configured/enforced. The Windows PMIC driver's name containing 8380 is not itself proof of the Linux SPMI SID.

## Reproduction and mandatory gate

`python3 observe_flash_location.py` reads **only** live DT property bytes, SPMI sysfs links and the regmap *name/range metadata*; it intentionally never opens regmap's `registers` or SPMI read/write interfaces. The observation is fail-closed on changed parent SID, flash node/status, driver binding, flash base, regmap metadata, or active camera nodes. `python3 test_observer.py` rejects twelve deliberately corrupted *in-memory fixture* variants. `evidence/RESULT.json` contains only the derived location, status and short property SHA256 hashes, not raw register dumps or unrelated device data.

Before any new **passive timer-value** observation, plan a narrowly bounded read targeting exactly the verified PM8550/SID 1 controller with separate new one-shot identity and Golden rollback, determine whether reads have side effects and whether a single-reg access path is available. Do **not** sweep the entire `/sys/kernel/debug/regmap/0-01/registers` dump merely to find ee3e: that may read unrelated PMIC hardware. Read-only timer values by themselves still cannot establish measured IR pulse duration, optical current/irradiance or autonomous off in host-crash/stuck-trigger conditions. E004fs remains **BLOCKED** and the IR emitter remains OFF.
