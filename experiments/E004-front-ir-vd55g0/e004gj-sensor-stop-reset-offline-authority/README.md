# E004gj — OEM sensor stop command and Linux reset fallback (offline PASS)

This stage examines the **sensor-side** stop path without repeating any consumed Windows or Linux camera boot. The exact OEM Surface VD55G0 package is SHA-256 pinned, and its register-list entry ID 1880 contains one write of 0x0202 = 0x01. The locally pinned ST VD55G0 register naming dictionary describes 0x0202 = 1 as STOP_STREAM. Package entry 1867 also contains 0x0201 = 1 along with state polls, compatible with a start sequence. The 0x0202 entry is **an installed OEM stop-command candidate**, not an independently observed Windows stop callback invocation or physical GPIO readback.

The current Linux native sensor driver uses the same 0x0202 = 1 stop request, polls the command until self-cleared, then waits for sensor FSM SW_STBY. If stop/poll fails, its source asserts the sensor reset GPIO and releases its runtime PM reference. Its stream-start path requires all four sensor GPIO selectors to be disabled (1,1,1,1). This is **code-level logic and prior independent unilluminated Linux stream-stop evidence**, not verification that the PMIC flash output is disconnected from a stuck sensor GPIO or will autonomously shut off if the host freezes, the bus fails or the PMIC ignores the reset.

Reproduce offline on SP11 Golden:

    python3 experiments/E004-front-ir-vd55g0/e004gj-sensor-stop-reset-offline-authority/verify_sensor_stop.py
    python3 experiments/E004-front-ir-vd55g0/e004gj-sensor-stop-reset-offline-authority/test_sensor_stop.py

The verifier pins the OEM package, parses exactly the entry 1880 stop register row and two separate 0x0448 configuration rows, and checks the source-level Linux command/poll/standby/reset ordering and disabled GPIO selectors. Nine negative tests reject changed package bytes, source command, state and reset code, or ST naming reference. It does not execute the original Windows sensor stop routine or replay E004fu's consumed unilluminated capture. No original OEM package bytes, proprietary DLL/SYS, optical imagery or extracted firmware are committed.

**Safety:** The OEM stream-stop candidate and Linux GPIO-reset fallback establish plausible software paths for stopping sensor streaming; neither is an autonomous verified flash-LED electrical cutoff. E004fs/E004ge remain BLOCKED until independent physical current/irradiance, emitted pulse and host-fault/stuck-trigger shutdown are established. No PMIC register read/write, IR activation, Windows/KD run, camera reboot, login/PAM or Golden modification occurred.
