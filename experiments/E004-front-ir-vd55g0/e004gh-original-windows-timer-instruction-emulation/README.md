# E004gh — Windows ARM64 timer callback CPU emulation (offline PASS)

Replays the **original, SHA-pinned Windows qcpmic8380.sys ARM64 machine instructions** for its timer callback at RVA 0x26d50 using the disposable, in-memory Unicorn AArch64 emulator from E004gg. Windows logging and masked PMIC writes are intercepted in emulator memory; no Windows driver is loaded or executed on SP11 hardware, no PMIC is accessed and no emitter is enabled. The existing E004fx passive Golden timer snapshot is *read as archived evidence only*; E004fx is consumed and is not repeated.

On synthetic timer requests, the callback calculates enabled code 0x80 | floor((ms-10)/10) for 10–1280 nominal ms, and zero when disabled. The executable callback requests ee3e and ee41 for logical LED1, then ee3f and ee40 for the other pairing, and makes a fifth ee40 clear request, as observed in this narrowly scoped VM fixture. This is the **observed requested write order under this synthetic input and mocked environment**, not proof that the actual Windows camera exercises this callback, nor that the PMIC independently enforces those times. E004gb's bounded normal type-0 preview did not observe a timer-helper access. The archived Golden idle timer byte 0x93 matches the *software handler's encoding for a nominal 200 ms request* but does not establish Windows streaming-time state or emitted pulse duration.

Injected failures at each of five mocked PMIC writes exercise the original CPU's paired-write error handling: both requests within a logical pair are attempted and any error aborts before the next logical group. A masked bus-write helper returning success is not a physical readback. The timer register is not tested under hardware stuck-high or host-halt faults, and neither nominal 200 ms nor nominal 1280 ms is an approved duration for real LED emission.

Reproduce on protected SP11 Golden from the repository root:

    python3 experiments/E004-front-ir-vd55g0/e004gh-original-windows-timer-instruction-emulation/emulate_timer.py
    python3 experiments/E004-front-ir-vd55g0/e004gh-original-windows-timer-instruction-emulation/test_timer.py

Both scripts fail closed on drifted prior-emulator source, invalid synthetic requests and unexpected CPU request ordering. Their output deliberately contains no proprietary PE bytes or biometric images. E004fs/E004ge **remain blocked**: independent electrical and optical measurements, real strobe timing, verified hardware-independent shutdown and expert evaluation are missing. No Linux flash patch, login integration, camera activity or Golden modification.
