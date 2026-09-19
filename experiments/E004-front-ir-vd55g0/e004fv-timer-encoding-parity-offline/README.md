# E004fv — Windows-compatible PMIC timer encoding (OFFLINE)

Status: **PASS — source-level timer-encoding parity and isolated Linux build only. NOT installed or hardware-authorized.** E004fs emitter-current, optical output and independent shutoff requirements remain blocked. E004fv is a fresh static experiment and does not reuse or rearm E004fu or any prior camera/Windows boot.

## Specific, reproducible discrepancy

The hash-pinned E004fk isolated Linux 4-channel qcom-flash source computes the enabled timer register as 0x80 | min(floor(timeout_ms / 10),127). The hash-pinned Windows qcpmic8380 handler recovered in E004fl computes 0x80 | floor((timeout_ms - 10) / 10) for requested timeouts from 10 through 1280 ms, and zero for disabled. Both target the same ee3e..ee41 channel timer registers, but this establishes parity of **software encoding**, not verified optical timer behaviour.

At a nominal 10 ms request, the original Linux driver produces 0x81 while the Windows handler produces 0x80; at 40 ms, 0x84 versus 0x83; at 1270 ms, 0xff versus 0xfe. At 1280 ms, both produce 0xff because the original Linux formula clamps its 7-bit field; that final equality masks the one-step difference at lower requests. This also corrects any loose statement that an encoded 0xff is *physically proven* to mean 1270 ms: Windows' handler assigns it to 1280 ms. Neither physical timing nor permitted optical exposure has been measured on SP11.

## Uninstalled candidate source

The reproducible generate_patch.py produces src/front-ir-vd55g0/illumination/0003-qcom-flash-align-pmic-timer-encoding.patch against **only** the SHA-pinned, uninstalled E004fk source. It leaves the Golden kernel, modules, firmware, device tree, camera and PMIC untouched. The proposed code calculates the Windows-compatible timer byte, rejects unrepresentable nonzero sub-10-ms requests rather than silently enlarging them, and refuses to arm the flash with a disabled/too-small configured timeout. Zero remains a disabling request on the disarm path.

The source patch is **not an illumination safety policy**. It does not set a defensible LED current or total exposure budget, confirm timer registers or GPIO/LED electrical behaviour on the hardware, prove crash/stuck-strobe shutdown, or establish eye safety. Its current default remains 1000 mA and would need separately verified safe configuration before any hypothetical activation. An automatic Golden reboot cannot independently shut off a stuck IR LED.

## Validation and next gate

Run python3 generate_patch.py then python3 verify_result.py (or test_timer_patch.py). The checker SHA-pins the Windows static result and E004fk source, applies the proposed delta to a disposable copy, extracts/compiles the **actual patched C timer helper** and validates all 1271 Windows-accepted integer-ms requests (10–1280), zero disabling, nine invalid sub-step inputs, paired-channel writes and second-channel bus-error propagation under AddressSanitizer/UndefinedBehaviorSanitizer. The isolated kernel flash module was also built cleanly with W=1 against SP11's prepared Golden kernel headers in a temporary build tree, without installation or module loading. Reproducible source patch and concise non-proprietary evidence are committed; kernel objects and any proprietary driver files are not.

Next evidence should distinguish the Windows software timer formula from actual SP11 PMIC channel-timer state/readback, and establish an independently validated physical LED cutoff/current/irradiance envelope across normal capture, camera stop, host crash and stuck trigger. Until then E004fs emitter activation remains explicitly forbidden; face enrollment, liveness and login integration are separate unfinished stages.
