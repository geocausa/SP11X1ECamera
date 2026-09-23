# E004ma — guarded real front/rear RGB selector via root-private Unix socket

Distinct E004ma single-use, source-pinned guarded camera candidate.
Builds on CONSUMED E004lz physical maintained RGBSession and E004ly
extended software publisher proof, but uses NEITHER consumed identity.
The tested unknown is opt-in ROOT-ONLY control:
rgbctl front -> ordinary uid1000 front1080p V4L2 app first/reopen/
SIGKILL/recovery -> rgbctl rear (full verified publisher stop/STREAMOFF
and neutral graph first) -> ordinary uid1000 rear4K app first/reopen/
SIGKILL/recovery -> rgbctl off -> rgbctl quit.

The root-private UNIX-socket selector server and independently opened
ordinary app clients run as separate processes. Both named virtual
cameras remain discoverable, but only selected sensor route streams.
Unknown or non-root commands are rejected; all accepted commands
use the single maintained RGBSession, owner lease and full fresh
119-edge graph verification.

A distinct automatic Golden-return one-shot validates source-pinned
hardware modules/R4 package/boot manifest, root-only nodes and
assets, virtual permissions and IR standby before ANY camera route
write. Root selector watchdog <=180sec, each publisher service
<=240sec, main candidate <=560sec, no unguarded restarts.
Linux OS-level system suspend/resume/hibernate is prohibited,
IR video/illumination OFF. No saved pixel data, golden changes or
Windows hardware ISP tests. All results need RESULT/CONSUMED archive
and candidate retirement after independent Golden verification.

Finite root-only selector acceptance is NOT a permanent daily camera
service or proof of unbounded multiclient safety, balanced image
quality, auto exposure or Windows visual parity.

## Final E004ma result (2026-09-23): PASS / CONSUMED / RETIRED

Independent real root-private opt-in Unix selector commands front→rear→off→quit
succeeded with exact front1080p/rear4K software NV12. For EACH camera,
three normal uid1000 reader processes received 120 distinct complete
frames, and intentionally killed client recovery retained the same
publisher service invocation. Service publisher SIGTERM/STREAMOFF=143;
full native graph neutral after run; no IR or OS-level system sleep.
Candidate boot 93141fda-ca01-4e24-a97b-6d669a7f54b2 returned to Golden
bc251567-c1a4-4cbb-84eb-6e47474f0eee, default boot preserved.
Candidate boot/service/private assets retired and identity consumed:
NEVER REARM. RESULT.json, CONSUMED.json and evidence/ are authoritative.

Opt-in ROOT-ONLY socket selector acceptance is still a finite guarded
candidate, not a persistent ordinary desktop camera service. Front/rear
sampled luma Y ~16 even though application video delivery passed; optical
scene detail, active autoexposure and quality remain UNKNOWN. Morning
changing light requires a separate fresh safely guarded experiment;
do not infer that app-visible video is correctly exposed.
