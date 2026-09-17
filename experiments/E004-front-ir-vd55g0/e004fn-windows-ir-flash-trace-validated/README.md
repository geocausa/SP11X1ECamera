# E004fn: Windows flash observer with parser validation

Prepared, not consumed. Follow-up to E004fm's incomplete trace. One fresh Windows
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
