# E004he — live-selected OEM four-channel callback table, subtype-0 versus timer route

**OFFLINE PASS, 2026-09-20.** This stage reconciles the **new E004hd actual Windows in-memory handler pointer** with the previous E004fi/E004fl/E004gi static OEM flash/timer findings and re-verifies the full cross-driver command/handler map against BOTH original SHA-pinned Windows ARM64 driver images. It does not independently discover an additional hardware writer or repeat a consumed KD/camera session.

E004hd's fresh *read-only* KD session proved that after normal Windows initialization PMIC global `qcpmic8380+0x3b8d8` points at module `+0x39470`; dereferencing that LIVE table at offset `0x90` reaches `+0x285c0`, the OEM four-channel module/channel callback. The same original static table has the following distinct commands and PMIC functions:

| Flash request | Original 32-bit IOCTL | PMIC input bytes | Slot relative to live four-channel table | OEM PMIC callback |
| --- | --- | ---: | ---: | --- |
| Current | `0x802f0fb0` | 6 | `+0x38` | `+0x270c0` |
| Timer | `0x802f0fac` | 16 | `+0x28` | `+0x26d50` |
| Trigger input | `0x802f0fcc` | 4 | `+0x70` | `+0x27f20` |
| Trigger mode | `0x802f0fd0` | 20 | `+0x80` | `+0x281e0` |
| Strobe module/channels | `0x802f0fc8` | 4 | `+0x90` | `+0x285c0` |

Each command above is verified twice: original flash-side literal and original PMIC-side constant, matching ARM64 dispatcher compare/branch and input-size check, plus the original four-channel function pointer in `+0x39470`. In particular the flash timer helper `qccamflash8380+0x4dd0` constructs a **16-byte** request and dispatches `0x802f0fac` into the separate PMIC **timer** callback `+0x26d50`; the flash module/channel wrapper `+0x4d58` constructs a **four-byte** request `0x802f0fc8`, whose actual Windows-idle handler target was proved in E004hd to be `+0x285c0`. The latter original callback requests masked module-enable `0xee46` before channel-enable `0xee4e`, but contains no direct call to the original timer helper.

The **normal subtype-0 original flash dispatch** at `+0x5b7c..+0x5c64` has an explicitly checked direct sequence: set current (`+0x5bd4`), set trigger input (`+0x5c24`), set mode (`+0x5c50`) and request module/channel strobe (`+0x5c64`, sending bytes `[1,1,0,1]`). Original ARM64 subtype selection branches around the *type-2* direct timer-helper call at `+0x5b2c`, and the other original direct timer call is in the separate configuration routine at `+0x4938`. The verifier checks the complete original flash executable's two direct calls to the timer helper, not merely one selected trace. This **does not exclude** indirect/lifecycle calls, an earlier boot/software or pre-OS PMIC timer request, another driver/firmware writer, or the timer's actual autonomous enforcement. It is consistent with the previously consumed E004gb normal 12-frame OEM preview showing NO matched PMIC timer-register helper activity during that bounded session and the separately consumed Golden idle read of four `0x93` timer bytes. The first real writer of those bytes remains unknown.

**Engineering consequence:** do not infer from OEM subtype-0's software request sequence that Linux can safely arm the emitter without independently establishing its timer state, actual allowed output, physical pulse behavior and autonomous fault-off. These are different questions from locating original callback pointers. The E004fs/E004ge physical qualification gate stays BLOCKED, Linux emitter/flash candidate patches UNINSTALLED, and PAM/login unchanged.

Run `python3 experiments/E004-front-ir-vd55g0/e004he-original-subtype0-live-table-timer-route/verify_route.py` and `python3 experiments/E004-front-ir-vd55g0/e004he-original-subtype0-live-table-timer-route/test_route.py` on protected Golden. Both original OEM binaries are SHA-pinned; **19 in-memory negative tests** reject altered IOCTLs, instructions and runtime callback-table slots. The original E004hd live KD transcript is consumed, only its immutable result is read offline, and no proprietary executable or new physical data is committed.

**Next distinct high-signal lead:** investigate **pre-driver/pre-OS timer ownership or a different configuration request that initializes `ee3e..ee41`**; the normal subtype-0 direct command branch is now fully accounted for on the observed selected table. Separately advance the fail-closed offline face-worker boundary without representing public-photo inference as working dark-room recognition or Windows Hello security parity.
