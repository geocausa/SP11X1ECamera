# E004fl: IR trigger and initial timing authority

PASS offline. No camera opened or PMIC registers accessed. E004fj establishes
which PMIC table is active; this experiment decodes its trigger/timer callbacks
and replays E004d's exact initial sensor packet against the Surface package.

## Derived facts

| Operation | Flash literal RVA | PMIC literal RVA | Active-table offset | Callback RVA |
| --- | --- | --- | --- | --- |
| Trigger input selector 802f0fcc | 6238 | 7c14 | 70 | 27f20 |
| Trigger mode 802f0fd0 | 623c | 7c18 | 80 | 281e0 |
| Safety timer 802f0fac | 4e80 | 7bf8 | 28 | 26d50 |

All addresses are relative to the exact drivers pinned in evidence/RESULT.json.
Manual dispatch review: PMIC 71ec..735c validates 4/20-byte payloads and loads
the stated table slots. Flash type-0 configuration 5bcc..5c64 sets current,
selects an input, supplies five words [1,1,0,1,0], then arms logical LED1.

PMIC 27f20..28074 writes the input selector shifted by four under mask 70 to
all four strobe registers ee4a..ee4d. The flash caller chooses its input selector
from a platform identifier; the actual selector remains unobserved. The current
Linux four-channel field includes bits 0..6 and writes upper selector bits zero;
this must match the actual Windows selection before relying on that behavior.

PMIC 281e0..283e8 interprets the first three payload bytes as LED selection,
then words at +4/+8/+c as hardware/edge/polarity fields. The type-0 payload
therefore writes value 5 under mask 7 to ee4a and paired ee4d: hardware trigger,
level-sensitive, active high, matching the Linux driver's bit definitions.
It also clears bit 0 of ee67 when hardware triggering is selected. The semantic
meaning and reset/firmware state of this common bit remain unresolved; Linux's
existing qcom-flash source has no explicit ee67 access.

PMIC 26d50..26f20 accepts enabled timer requests from 10 through 1280 ms,
encodes floor((ms-10)/10) with enable bit 7, and writes paired channels using
table 36d48 = ee3e..ee41. Disabled requests write zero. Flash helper 4dd0..4e70
can request 1270 ms for logical LEDs 1 and 2 (register value fe), but the
inspected type-0 branch does not call it. That does not prove the timer's live
state: other callers and previous state exist. Do not import 1270 ms as board
pulse policy.

E004d's hash-pinned live InitialConfig packet explicitly writes GPIO1 0468=02,
edge delays 046d=00/046e=00, initial exposure 044e..044f=100 lines, line length
1200 and frame length 1955. This proves initialization, not subsequent exposure.
ST UM2829 sections 18.1..18.4 describe the strobe envelope and signed line shifts:
https://www.st.com/resource/en/user_manual/um2829-how-to-integrate-and-configure-the-vd55g0-device-from-a-hardware-and-software-perspective-stmicroelectronics.pdf
At the Linux-measured 137.6 MHz pixel clock, zero shifts and 100 lines calculate
to 872.09 us and 5.115% frame duty. This is arithmetic, not a Windows clock or
optical measurement, and does not establish permissible sustained operation.

## Reproduce and limits

Run `python3 experiments/E004-front-ir-vd55g0/e004fl-ir-trigger-timing-authority/verify_timing.py`.
It checks exact binaries, dispatch constants/pointers, timer tables and all 1271
accepted integer-ms encodings; it reruns the prior sensor decoder and requires
byte-derived equality with the recorded packet/package reconstruction. Handler
semantics above were manually reviewed; constant checks are not a replacement
for control-flow or live validation. No proprietary binary/disassembly is added.

Next observe Windows' actual type-0 requests and exposed streaming timing with
a fresh bounded identity. Keep both native flash patches uninstalled until the
input selector, common bit and bounded pulse policy are resolved. Golden remains
permanent and Linux SecureISP remains inactive.
