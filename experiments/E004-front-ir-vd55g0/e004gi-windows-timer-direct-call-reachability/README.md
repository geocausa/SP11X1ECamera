# E004gi — Windows flash timer call graph, offline, PASS

The SHA-256-pinned original Windows ARM64 qccamflash8380.sys was disassembled across its full .text section to enumerate **all direct BL calls** to the flash timer helper (RVA 0x4dd0). Exactly two direct callers were found: RVA 0x4938 in a separate configuration routine starting at 0x48c8, and RVA 0x5b2c in a dispatch branch explicitly entered when the operation subtype equals 2.

The normal subtype-0 branch in the observed flash dispatch starts at RVA 0x5b7c and proceeds through RVA 0x5c64 without a direct BL to the timer helper. The subtype-2 path programs current, then requests a nominal enabled timer from the helper at 0x5b2c. A separate routine at 0x48c8 also orders current → timer → strobe. This narrows what a direct normal subtype-0 dispatch can explain, but does **not** prove what all indirect callers, earlier initialization, firmware or the PMIC itself can do. E004gb's previously consumed bounded Windows trace already recorded no timer-access hook hit; it is only verified offline here, not repeated.

In particular, E004gh's exact Windows PMIC CPU emulator accurately describes the **timer callback if called**, not proof that the subtype-0 OEM IR preview called it or that physical timer enforcement occurred. Golden's earlier idle timer byte 0x93 cannot resolve streaming-time timer state. Do not infer that no hardware timer exists because the subtype-0 branch does not directly call this particular helper.

To reproduce on SP11 protected Golden without hardware access:

    python3 experiments/E004-front-ir-vd55g0/e004gi-windows-timer-direct-call-reachability/verify_callgraph.py
    python3 experiments/E004-front-ir-vd55g0/e004gi-windows-timer-direct-call-reachability/test_callgraph.py

The first script pins the original Windows PE hash, exact two direct timer calls, other relevant helper call sites and subtype branch conditions; it reconciles only the already archived E004gb result contract. The second corrupts twelve individual synthetic instruction/archive contracts and confirms they are rejected. No proprietary binary, full disassembly, images, PMIC values or credentials are committed.

**Next useful software target:** trace other indirect PMIC timer call sites / system initialization and the sensor/flash power-off path. An independently proven emitter electrical cutoff, measured current, optical irradiance and pulse duration remain absent. No Windows/KD, camera boot, PMIC write/read, LED activation or Golden change in E004gi. E004fs/E004ge emitter gates remain BLOCKED.
