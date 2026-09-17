# E004fn: Windows flash observer with parser validation

**PASS live request sequence; consumed and Golden-restored.** Follow-up to E004fm's incomplete trace. One fresh Windows
boot, one normal IR capture, maximum 12 frames/five seconds, no exposure/current
SETs, no protected property SETs, no saved images. Baseline ea5d377; Golden boot
aec4c427-6fee-4590-9a30-c6eaa888295f. No native module/DT changes.

Use the installed flash binary hash pinned by E004fh. Discover its fresh module
base via SP7 KD after .reload. generate_kd.py emits a nested-condition observer
with literal permitted dump lengths 4/6/16/20 bytes, bp0 spelling and 32-hit cap.
Before arming, execute validate.kd during an idle break. It exercises seven cases
using the same formatter: supported lengths, unsupported lengths and null input.
Only a mapped PE header and debugger pseudo-register are used. Require all seven
case-done markers, four expected header dumps and final resume with no parser
error. Do not open the camera if validation fails. Watch SP7 and resume immediately
if any command errors; g in a file is not an error-recovery guarantee.

Then arm the one helper breakpoint, resume, run the bounded capture.ps1 once,
remove breakpoint and verify Windows cleanup. Capture is derived from E004fm's
successful routine with only the identity changed. It reads standard exposure
properties, which do not prove sensor exposure. Do not infer live timeout state
from absent timer requests or infer physical current from requested current.

Record all results, reboot Golden, verify unchanged default/order and no camera
activity, stop only the owned debugger after shutdown, retire and push evidence.
No same-boot stream retry. Linux illumination and SecureISP remain inactive.

## Live result

All seven idle parser cases passed; the four expected mapped-header reads were
bounded to their literal lengths. The fresh capture then acquired 12 NV12
644x604 frames and stopped normally, with five auto-resumed helper hits:

| Order | Command | Observed payload interpretation |
| --- | --- | --- |
| 1 | 802f0fb0 | LED current requests [700,0,0] mA |
| 2 | 802f0fcc | Trigger input selector 0 |
| 3 | 802f0fd0 | Five words [1,1,0,1,0] |
| 4 | 802f0fc8 | LED1 and module enable [1,0,0,1] |
| 5 | 802f0fc8 | Disable [0,0,0,0] |

Combined with E004fj's active table and E004fl's handler decoding, this confirms
that the native driver's selector 0 / hardware / level / active-high mode matches
the Windows request for sources 1 and 4. The mode handler also requests clearing
common ee67 bit 0. These are call arguments and static semantics, not observed
register-write returns, physical current, pulse width or image-quality parity.

No timer request appeared at the observed flash helper during this capture.
The five-hit count stayed below the 32-hit cap. Absence here does not establish
timer state or rule out writes by other callers. All 13 standard exposure
readings remained Auto=True, 0.5 ms; actual sensor exposure remains unproven.

The breakpoint was removed and the empty list verified before normal reboot.
Golden boot cd5253ff-bffa-495f-895d-79831524a6ff has unchanged BootOrder, empty
next_entry and no camera modules/nodes/processes. Only the owned SP7 debugger was
stopped after shutdown. Exact command files are retained as consumed evidence;
never execute them on a later boot because their module addresses are obsolete.
verify_result.py verifies the five payloads, parser gate, capture, cleanup and
Golden return. Native illumination remains off.
