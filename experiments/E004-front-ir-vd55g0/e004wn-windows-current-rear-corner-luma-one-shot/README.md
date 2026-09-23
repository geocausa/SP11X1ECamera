# E004wn current Windows rear-corner optical context (one-shot, PASSED and retired)

Fresh Windows-only numeric oracle on SP11, distinct from consumed E004kt
and all Linux E004m* camera trial identities. Same camera physical
orientation is inferred from unchanged user placement, not calibrated
or independently verified. Run only on authorized Windows SP11 with a
FRESH create-new consumed marker, schedule bounded 300s automatic reboot
BEFORE any front/rear colour VideoRecord NV12 WinRT camera access.

Eight CPU frames per front1080p/rear4K; sample Y every 64th horizontal
pixel and all rows; output mean, P01/P50/P95/P99, dark fractions, 8x8
spatial tile-mean variation and WinRT exposure auto-control state,
no photo/pixel file/image hash export, no IR, no sensor controls changed.
A truly dark Windows rear in this same room/time would support the
user's corner-scene explanation; a brighter rear would support a
Windows-vs-Linux processing/exposure investigation but NOT isolate a
sensor defect without controlled lighting, camera orientation and
matched statistics. The WinRT nominal auto-exposure value is NOT
independent sensor-register verification. Existing Windows one-time
Scheduled Task and boot recovery must be inspected and retired only by
its own original identity; never rerun old task or old E004kt script.

## Actual Windows outcome — 2026-09-23

SP11 booted Windows through the pre-existing direct EFI one-shot, without
altering EFI BootOrder or the Golden GRUB saved entry. A new interactive
Geoca Scheduled Task executed the hash-locked E004wn PowerShell source;
its local unique CreateNew consumed marker preceded a scheduled 300s
return reboot and preceded all camera access. The source-only WinRT
and C# synthetic layout/statistics test had already passed on SP7 and
Windows SP11 without opening any camera. Exactly `Surface Camera Front`
1080p and `Surface Camera Rear` 4K Color VideoRecord NV12 streams each
returned eight CPU frames. Each native frame was sparsely sampled every
64th horizontal pixel and every row. Both WinRT readers stopped and
MediaCapture instances disposed; no controls changed, IR was untouched,
and no image files, pixel arrays or image hashes were exported. The
one-shot task exited 0 and was retired on Windows before reboot.

At approx 11:16 BST the Windows rear measured Y mean 148.237–148.554,
P01 119–120, median 150, P99 169, sampled fraction Y<32 exactly0,
8x8 spatial tile-mean std Y 11.202–11.244. The front mean was
123.268–123.698, P01 16–17, P99 254–255, tile std43.57–44.11.
WinRT ExposureControl reported Auto=true for both with nominal value
5000 ticks; this is NOT direct native Linux-style sensor-register
exposure readback, and a Windows NV12 mean must not be divided by a
Linux RGB PNG P99 or treated as a same-scene matched exposure trial.
The latest Linux E004mh rear baseline app NV12 P99 was31 at approx
10:58 BST (bounded native exposure/gain app P99 37), and rear private
RGB baseline/gain PNG P99 15/20. Its sensor black offset was NOT
calibrated. Physical orientation and ambient intensity at the two times
were not independently verified: even if the rear is pointed at a
relatively featureless corner, Windows can automatically raise that
scene's rendered luma. The Windows rear is **not similarly dark** in
this current capture. Do NOT infer a defective Linux sensor from this
alone; investigate controlled exposure/RAW response and software ISP.

The 300s Windows watchdog returned SP11 automatically to protected
Golden Linux at boot ID 44a8e815-7935-4a4e-a82f-187bb0c6ab1c.
EFI BootCurrent/BootOrder, saved GRUB/next_entry and camera-overlap
safety checks passed. Fresh Windows RESULT.json is archived as
`evidence/RESULT.json` (scalar statistics ONLY), with `SUMMARY.json`
and unique consumed/task-retirement/Golden markers. The Windows-local
original remains in `C:\Users\Geoca\Documents\SP11-Camera-E004wn-Corner-Oracle`.
This identity/script must NEVER be rerun. The next cross-platform trial
requires a fixed, genuinely lit target seen by both boots, matched
statistics and timestamped exposure/control state, without Linux OS
system sleep or protected IR activation.
