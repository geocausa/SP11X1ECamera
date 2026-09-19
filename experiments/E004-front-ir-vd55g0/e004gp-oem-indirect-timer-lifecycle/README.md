# E004gp — original OEM PMIC indirect timer dispatcher, offline PASS

Recovered after a chat stream interruption: SP11 Golden and repository remained clean; the Ghidra headless original qcpmic8380.sys analysis had finished in a temporary working directory. No new Windows boot, KDNET, capture, PMIC access or IR illumination occurred.

## What the original code actually establishes

Ghidra's **original pinned Windows ARM64 PMIC binary** identifies a function-pointer table at RVA 0x39470 and a static reference to it at RVA 0x210f0–0x210f8, where code stores the table pointer into an output structure and sets a software variant tag 0x0203. The original table holds TWO distinct timer callbacks: slot 5 → RVA 0x26d50 (four-channel timer request handler emulated in E004gh) and slot 6 → RVA 0x26f30 (single-channel timer request handler), plus slot 18 → RVA 0x285c0 (four-channel module/channel enable handler previously analyzed in E004gf).

The single-channel handler's Ghidra decompilation also sends a nominal timer request through a masked PMIC-write helper, but its presence does **not** establish which table slot the normal OEM IR preview uses. The OEM flash timer helper was previously mapped in E004gi: two direct Windows flash-driver callers, neither in the normal subtype-0 branch. These callback-table findings strengthen the tracing target for eventual **fresh**, separately authorized runtime work; they do not prove that the original streaming session armed an autonomous timer or that PMIC logic cuts off continuously asserted/retriggered sensor strobe.

## Reproduction and safety

    python3 experiments/E004-front-ir-vd55g0/e004gp-oem-indirect-timer-lifecycle/verify_table.py
    python3 experiments/E004-front-ir-vd55g0/e004gp-oem-indirect-timer-lifecycle/test_table.py

The offline verifier pins the original PMIC PE SHA256 and checks exact source function pointers and ARM64 instructions assigning the table; ten negative mutations cover the global binary hash and separately the table slots and instruction-level invariants. The extracted proprietary PE bytes and full Ghidra decompiled text are **not** committed. Previously completed Ghidra run logs remain temporary local files and are not a substituted Windows live measurement.

E004fs/E004ge remain BLOCKED pending independent actual IR current, irradiance, optical pulse and autonomous electrical fault-off evidence. No live camera, PMIC register or emitter, firmware, Golden or login was altered.
