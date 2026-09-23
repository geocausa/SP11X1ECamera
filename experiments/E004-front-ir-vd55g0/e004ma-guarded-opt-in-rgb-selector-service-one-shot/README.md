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
