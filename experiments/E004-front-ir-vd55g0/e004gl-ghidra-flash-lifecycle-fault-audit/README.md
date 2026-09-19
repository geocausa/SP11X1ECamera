# E004gl — Ghidra and original Windows ARM64 flash lifecycle fault audit

PASS offline; native IR emitter remains OFF. SP11 already has Ghidra 12.0.4; no download or machine change was required. VerifyFlashLifecycleGhidra.java decompiles the exact SHA-pinned OEM qccamflash8380.sys and qcpmic8380.sys on protected SP11 Golden Linux, checks target function identities, source-level helper request order, and the PMIC timer callback's indirect-dispatch-table reference. verify_ghidra.py imports each driver into a temporary, deleted headless Ghidra project and accepts only expected PASS markers. Decompiled proprietary Windows driver text is not stored in Git.

Ghidra's Windows flash-start function RVA 0x48c8 requests current, timer, then strobe-on and checks their returns, while its earlier active-state branch requests strobe-off and does NOT check the off-request return value before proceeding. The Windows flash-stop function RVA 0x4828 clears its software-active flag only after a successful off helper. The Windows PMIC module callback RVA 0x285c0 requests module disable (0xee46) before channel disable (0xee4e); Ghidra identifies the timer callback RVA 0x26d50 in the PMIC indirect dispatch table. These are software findings, not physical output evidence.

emulate_flash_lifecycle.py also executes the original SHA-pinned Windows ARM64 machine instructions in a disposable Unicorn CPU VM with current/timer/strobe/Windows helpers mocked. Seven synthetic scenarios establish the following:

- With a prior-active flag set, an injected OFF request error does not stop the original start routine from requesting current, timer and strobe-on, returning software success when the later requests succeed. A failed mocked request does not prove the physical LED remained on.
- When new current or timer requests fail, the function reports failure before new strobe-on. When new strobe-on fails, the function reports failure and keeps its active flag cleared, without making a further best-effort OFF call in this examined routine. These request outcomes cannot establish actual electrical LED state.
- When normal stop's mocked OFF request fails, the function reports failure and retains its active flag; normal stop clears that flag on success. Neither path is an autonomous electrical cutoff.

test_flash_lifecycle.py rejects eight drifted/invalid fixtures and checks the critical original-instruction fault branches. The isolated Linux flash patches remain uninstalled and do not gain hardware authority from software parity. A future Linux implementation should fail closed after a previous OFF error instead of silently rearming; best-effort software disarm still cannot guarantee off when hardware communication fails.

Offline reproduction from repository root:

    python3 experiments/E004-front-ir-vd55g0/e004gl-ghidra-flash-lifecycle-fault-audit/verify_ghidra.py
    python3 experiments/E004-front-ir-vd55g0/e004gl-ghidra-flash-lifecycle-fault-audit/emulate_flash_lifecycle.py
    python3 experiments/E004-front-ir-vd55g0/e004gl-ghidra-flash-lifecycle-fault-audit/test_flash_lifecycle.py

No Windows/KD or consumed E004gb one-shot was repeated. No PMIC, camera, emitter, Golden, firmware, kernel, sensor or login mutations occurred. A mocked bus fault is not a physically measured LED fault. E004fs/E004ge remain BLOCKED pending independent actual LED current, optical exposure/pulse and autonomous off under stuck-strobe and host-failure validation on SP11.
