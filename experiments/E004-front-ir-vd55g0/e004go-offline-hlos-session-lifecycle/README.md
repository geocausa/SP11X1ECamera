# E004go — offline HLOS diagnostic session lifecycle (PASS, no device/auth)

This is an isolated userspace service **protocol prototype**, not a camera daemon, hardware IR safety device or face authenticator. It consumes **only aggregate JSON** from the existing E004gc C signal diagnostic; no image or facial template enters this controller. The emitter remains OFF. An ordinary unprotected HLOS process cannot assert the protections of Windows Hello or SecurePD.

The one-shot session accepts exactly one batch of 1..16 strictly typed, ordered signal-metric frames within a caller-injected monotonic tick budget. It rejects altered/duplicate JSON keys, nonfinite/nonnumeric/out-of-range values, unexpected image/template/authentication fields, incorrect frame counts, reordering, invalid clock ticks, deadlines, and second starts/accepts. Cancellation, timeout, malformed input and out-of-order requests become non-rearmable terminal states; a fresh offline object is needed for another diagnostic. The only completion report says 'offline-session-diagnostic-only' and explicitly reports no authentication, no login/unlock authorization, no autonomous hardware cutoff and no LED activation. **There is no authentication or device API.** The tick-based budget is tested only when a caller invokes a method; it does NOT run a watchdog independently if the host stalls.

Run from repository root:

    python3 src/sp11-camera-hlos-worker/test-offline-session-gate.py

The regression explores 1,024 adversarial state/event sequences, malformed telemetry, all frame counts 1..16 and exact deadline boundaries; it also compiles the existing **real C diagnostic** in a temporary directory and feeds one synthetic 16-frame uniform-gray NV12 batch through it, then consumes the resulting real JSON through the session controller. It uses no archived real ambient optical frames, retains no images and does not alter the HLOS pixel-parity core, login, camera, firmware, kernel, Golden or LED configuration. This is transport/session failure-handling groundwork only; it does not evaluate face detection, matching, liveness, consent or biometric false-accept rates.

Hard separation: E004fs/E004ge independent optical/current/pulse/hardware-autonomous fault-cutoff gate still BLOCKED. Nothing about this offline session protocol or a timed host callback authorizes native illumination. E004gb/E004fu and all prior Windows/optical one-shots remain consumed and untouched.
