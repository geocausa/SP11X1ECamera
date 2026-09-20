# E004hq — original live-installed second SPMI masked-write callback bypasses earlier timer observer

**OFFLINE PASS, 2026-09-20.** This is a *distinct callback-routing and observer-coverage finding*, not another Windows boot or an attribution of the four idle timer bytes. It reconciles two SHA-pinned original Windows ARM64 OEM binaries, the previously **consumed** byte-original E004hn live interface dump, and the separately consumed E004hp early persistent timer-span watch. No camera, flash, PMIC/SPMI register action, Windows/KD, optical output or Linux native emitter was initiated.

## What the original OEM provider actually publishes

At original `qcspmi8380.sys+0x3e70..+0x3e88`, the provider constructs TWO successive function pointers in its 0x70-byte WDF output interface: `+0x1660` at interface offset **`+0x30`**, and a distinct callback **`+0x1920` at interface offset `+0x38`**. The original `qcpmic8380.sys+0x393c..+0x3974` queries this 0x70-byte interface into PMIC module global `+0x3d010`. Prior E004hn's independent actual Windows KD read at kernel uptime **35.654 s** already captured, byte-for-byte in its unchanged original SP7 transcript:

```text
qcpmic8380+0x3d040  fffff803`3dea1660  fffff803`3dea1920
                     [interface+0x30]     [interface+0x38]
```

Thus the *second callback pointer really was present in the live original Windows PMIC interface*, not merely an orphaned static driver symbol. However, E004hn did not set a breakpoint on `+0x1920`, execute it or read a timer register. An installed pointer is not evidence that the callback was invoked.

## Verified original alternate callback control flow

Original `qcspmi8380.sys+0x1920` accepts a caller-supplied packed selector in **w2**, requested value in **w3**, and mask in **w4**. The original provider decodes the bus/SID/address fields or takes its legacy context-derived branch, then attempts a **one-byte controller read** via the shared controller helper `qcspmi8380+0x64d8`: it sets `w0=1` at `+0x1ad8` and calls the helper at **`+0x1b38`**. If that read fails, original `+0x1b3c` branches around the write. On the zero-return path, it combines the old byte with the caller's mask/value at `+0x1b54..+0x1b64`:

`new_byte = (old_byte & ~mask) | (requested_value & mask)` (low eight bits).

It then invokes the **controller helper directly again** at original **`+0x1b70`**, using the previous successful zero return as its operation argument, with count one and its newly composed byte in a temporary buffer. The original `+0x1920` read–modify–write block has **NO direct call to `qcspmi8380+0x1660`**; it invokes `+0x64d8` for its controller access instead. This proves an additional software *write-capable* route that an entry-only `+0x1660` trap does not cover. It does not prove a successful physical write, and no actual value/mask for a timer-address invocation has been seen. Setting synthetic mask `0xff` and value `0x93` yields `0x93` under the original arithmetic, but this arithmetic example is **not evidence of such an OEM call**.

## Why the consumed E004hp no-match cannot exclude this route

E004hp installed a persistent, filtered software breakpoint at **`qcspmi8380+0x1660`**, plus a separate unfiltered one-shot positive control at adjacent **`+0x1664`**. The early control genuinely hit a *non-timer* transaction, and the filtered breakpoint remained active through the final bounded debugger pause with no matching timer-span marker. Both breakpoints belong to the `+0x1660` function and do **not** observe the separate entry at `+0x1920` or the common controller helper `+0x64d8`. Moreover, E004hp's early debugger action had an explicitly recorded syntax error and manual recovery; its original window and limitations remain unchanged, not recast as a comprehensive negative result.

**Bounded new conclusion:** the actual Windows driver published a second, independent SPMI callback that **can construct a one-byte write without entering the earlier watched callback**. Whether this path was *ever called*, addressed `ee3e..ee41`, produced or retained the observed idle `0x93`, or successfully wrote PMIC silicon is still UNKNOWN. A pointer published into PMIC's interface structure also does not, by itself, prove a particular PMIC caller used it. Pre-OS initialization, other drivers, alternative controller paths and hardware defaults remain unresolved.

## Next distinct, discriminating observation

If another independently scoped early Windows session becomes warranted, the observer should cover **both** original `qcspmi8380+0x1660` and `+0x1920` *or* their common controller `+0x64d8`, with validated WinDbg action syntax and an actual non-timer positive control. The original `+0x1920` interface signature is not the same as `+0x1660`—**w4 is a mask**, not a byte count—so replaying E004hp's `w2/w4` address-span filter at `+0x1920` would be invalid. A timer-address match would need actual bus/SID, original caller, requested mask/value (handled privately rather than logged indiscriminately), operation type, software return and controller status before identifying a *candidate* writer. To claim the **first** writer requires starting early enough to cover initialization or independent pre-OS evidence. No debugger software trace establishes actual LED irradiance, drive current, a measured pulse or autonomous OFF on host freeze/stuck strobe. Do NOT automatically authorize Linux emitter/PAM from it.

Run offline under verified protected Golden:

```sh
python3 experiments/E004-front-ir-vd55g0/e004hq-spmi-masked-rmw-alternate-timer-bus-path/verify_alternate.py
python3 experiments/E004-front-ir-vd55g0/e004hq-spmi-masked-rmw-alternate-timer-bus-path/test_alternate.py
```

The SHA-pinned original `qcspmi8380.sys`/`qcpmic8380.sys` remain only in the pre-existing local driver archive. `evidence/RESULT.json` records exact callback RVAs, original opcode checks and hashes of earlier consumed independent sources; no original Windows binary, KDNET key, extra live trace, camera frame or biometric template is committed. **48 mutation/negative cases** reject changed original provider/consumer instructions, callback slots and fabricated E004hp coverage; no new physical experiment was performed. E004fs/E004ge physical optical/electrical/host-failure cutoff gate stays BLOCKED; Linux native flash/emitter patches and PAM/login remain UNINSTALLED/OFF.
