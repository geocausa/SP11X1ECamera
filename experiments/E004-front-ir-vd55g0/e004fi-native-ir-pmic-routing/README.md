# E004fi: conditional native IR PMIC routing

**PASS static conditional mapping. Runtime branch and physical wiring remain open.**
All analysis is offline against the exact flash and PMIC drivers whose installed
hashes E004fh confirmed. No PMIC commands or emitter activation occurred.

## Derived chain

The flash driver opens interface 20952871-af3d-4a8a-9e47-cb346507b95b
(flash RVA d858, PMIC RVA 36fb8). Its current, strobe and timer commands are
recognized by qcpmic8380. Dispatch checks payload lengths and calls the selected
hardware table. The four-channel table at PMIC RVA 39470 contains callbacks:

| Purpose | Flash command | Payload bytes | Callback RVA |
| --- | --- | --- | --- |
| Target current | 802f0fb0 | 6 | 270c0 |
| Strobe | 802f0fc8 | 4 | 285c0 |
| Safety timer | 802f0fac | 16 | 26d50 |

The initializer at RVA 21010 selects this table when the input descriptor's
field at +4 is 0x31 or 0x49 (decision 21088..210b4, assignments 210e8..21104).
It initializes paired-channel bytes to [3,2,4,4]. Other supported descriptor
values use a different table. **No claim is made yet which branch ran on SP11.**
The driver global at RVA 3b8c8 contains a register-access identifier (+0), an
initialization argument (+4), old/new table pointers (+8/+10), initialized flag
(+18), and pairing bytes (+19). These names describe use, not public ABI types.

In the four-channel branch, logical LED1 therefore uses hardware channels 0 and
3, and LED2 uses 1 and 2. The strobe callback combines the base enable bit with
its paired-channel bit (286a0..287c4), writing a four-bit mask at 0xee4e. LED1
alone yields mask 0x9. Current registers are 0xee42..0xee45; resolution is 0xee49;
module enable is 0xee46. These match Linux's four-channel register layout.

For the installed 700 mA request, Windows selects 12.5 mA resolution and writes
current code 27 to each paired channel (270c0..27538): nominal 350 mA each.
Linux's existing current splitting gives the same code for a two-channel LED
at 700 mA. This is arithmetic parity for this request, not measured current or
parity for every possible requested value. If confirmed at runtime, standard
Linux led-sources = <1 4> can represent the pairing without new channel policy.
Do not apply this device-tree proposal until the active branch is verified.

Run `python3 verify_routing.py` from this directory. It pins input hashes and
checks command constants, interface GUID, table targets, register tables and
700 mA arithmetic. The control-flow interpretation above was manually inspected;
the verifier is not an emulator or a proof of runtime selection. Full binary
disassembly stays local under ignored build/ and is never committed.

## Exposure and strobe constraint

ST UM2829 Rev 2, sections 18.1–18.4, describes strobe as the integration envelope,
with signed line-based start/end shifts. GPIOs are specified active in streaming
only; configuring them in standby is supported. This is sensor documentation,
not a measurement of SP11's complete light circuit. Source:
https://www.st.com/resource/en/user_manual/um2829-how-to-integrate-and-configure-the-vd55g0-device-from-a-hardware-and-software-perspective-stmicroelectronics.pdf

With zero edge shifts assumed, our measured 137.6 MHz pixel clock, 1200 clocks per
line and 1955-line frame imply the following *hypothetical* strobe envelopes:

| Exposure lines | Pulse duration (ms) | Duty cycle (%) |
| --- | --- | --- |
| 100 | 0.8721 | 5.1151 |
| 1000 | 8.7209 | 51.1509 |
| 1891 | 16.4913 | 96.7263 |

These are calculations, not observations or recommended limits. Actual delay
registers, polarity, PMIC timeout behavior and permitted emitter duty cycle must
be verified. The Linux 10 ms timeout granularity cannot by itself justify an
arbitrary exposure range with illumination enabled. Keep exposure/gain transport
work separate from permission to arm the light.

## Next smallest observation

A read-only Windows kernel snapshot of qcpmic8380+3b8c8 (32 bytes) can determine
whether the four-channel table and [3,2] pairing were selected. Capture it while
idle, resume immediately, and return to Golden. Do not issue flash requests,
modify the table, or open a camera as part of that observation.
