# E004gk — additional Windows ARM64 flash auxiliary ON/OFF paths (offline PASS)

A new offline extension of E004gg executes the **original SHA-256-pinned Windows qccamflash8380.sys ARM64 instructions** in a bounded AArch64 CPU emulator. We do not load Windows, boot the SP11 again, repeat E004gb's consumed KD/capture, access the PMIC or illuminate the LED. Only Windows logging and the flash-command transport are mocked.

The full original PE direct-call map locates auxiliary RVA 0x6db0 at caller 0x5900 and auxiliary RVA 0x6e28 at callers 0x5924 and 0x5a44. Original instructions at 0x6db0 produce flash transport command 0x802f0fc8 and four-byte ON payload [1,0,0,1]. Original instructions at 0x6e28 produce the same command with the OFF payload [0,0,0,0]. When the mocked command transport returns a Windows error, both auxiliary routines return 1 rather than 0; the software caller can observe a reported failure. The test preserves the original Windows flash OFF wrapper instruction sequence as well as these additional caller instructions. Eight negative cases reject unsupported callback entries, invalid injected results and changed prior emulator source.

This confirms that Windows has an **additional software OFF-request route**, beyond the subtype-0 flash OFF path analyzed in E004gf/E004gg. It does **not** establish that the OEM normal IR preview executes this particular auxiliary route or that all suspend/remove/host-crash paths reach it. An error result is not proof of the physical LED state. Neither auxiliary software route constitutes an independently enforced PMIC hard cutoff when host execution or the SPMI bus fails.

Reproduce on SP11 Golden from repository root:

    python3 experiments/E004-front-ir-vd55g0/e004gk-windows-flash-teardown-cpu-emulation/emulate_teardown.py
    python3 experiments/E004-front-ir-vd55g0/e004gk-windows-flash-teardown-cpu-emulation/test_teardown.py

Do not reproduce E004gb's Windows boot/flash/capture or E004fx/E004fy idle reads. The CPU emulator's flash transport is always mocked and never opens hardware. Only derived software control-flow facts are committed. E004fs/E004ge independent measured current, real optical irradiance/pulse and autonomous stuck-strobe/host-fault OFF evidence remain BLOCKED; Linux IR emitter OFF, no login/PAM modification.
