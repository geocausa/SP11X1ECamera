# E004ge — physical IR safety evidence gate: BLOCKED / PHYSICAL ACTION REQUIRED

This stage records the remaining external physical evidence needed for safe native Linux illumination on the actual SP11. It does not prove optical safety, implement flash operation, or authorize the emitter. E004gb and all earlier one-shot identities remain consumed.

## Inventory and evidence

At this checkpoint SP11 on protected Golden Linux exposes only root USB hubs; an SP7 Windows USB/PnP read-only inventory showed only built-in cameras and no identifiable calibrated optical power meter, photodiode/DAQ or oscilloscope. Equipment may exist elsewhere, but no validated physical IR safety dataset is available to this project. Windows OEM previews and PMIC helper requests, and Linux idle timer/module register bytes, do not establish current, optical output, real pulse duration, independent hardware shutdown or physical wiring.

## Physical action required

Arrange a qualified hardware/optical-safety engineer or laboratory with calibrated near-infrared radiometry and electrical pulse/current instrumentation for THIS exact SP11. Before intentional emission, the specialist must design a wavelength-, geometry- and emitter-specific safe test plan; identify LED wiring and autonomous cutoff authority; record physical current/emission pulse and repetition, and evaluate failure-off behavior under host halt, PMIC communication failure and stuck-high strobe. Preserve instrument models, calibration/uncertainties, optical setup, raw traces, and independently written safety determination.

Do not substitute an uncalibrated phone/IR camera, a normal Windows preview, nominal 700mA driver request, PMIC timer register, host watchdog or reboot. Do not disassemble/probe the powered device, stare into the IR emitter, deliberately cause a stuck-on condition or run unbounded tests without a qualified safety plan and controls.

## Offline mechanical gate

The JSON file evidence/PHYSICAL-EVIDENCE-STATUS.json records the five currently missing categories. Run python3 test_gate.py to verify fail-closed behavior. Running python3 gate.py returns exit code 2 and JSON BLOCKED_PHYSICAL_ACTION with five missing categories. Even if every checklist flag is asserted true, status is REQUIRES_INDEPENDENT_EXPERT_REVIEW, emitter_enable_authorized=false and exit code 3. Checklist booleans are NOT scientific measurement data or safety approval.

No Windows/KD, camera, PMIC, emitter, Golden or login changes occurred in this stage. Offline HLOS work can proceed separately, but existing pattern images do not prove usable face imagery or anti-spoofing.
