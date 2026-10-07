# Rear-only Windows screen baseline — fresh01

E-NATIVE-REAR-WINDOWS-SCREEN-01. User priority at2026-10-07T20:37:51Z:
room light OFF; rear camera reportedly faces SP7 screen. Complete rear before
front calibration. This supersedes the preceding front-meter NEXT instructions.

Hypothesis: the same SP11 OEM Windows rear Color/VideoRecord path can deliver
3840x2160 NV12 using its normal automatic controls and preserve an advancing,
full-resolution rear-only baseline under this reported scene.
Evidence tier P (physical Windows output); Windows oracle for Linux L2 ISP configuration/L3 buffer layout,
L4 controls/focus and L5 ordinary libcamera delivery. No Linux ISP authorization.

Source base0ae6419f4a1585de23540da8dd2e00cbd560c4da. Reuses the tested front WinRT
reader/layout skeleton, independently writes native NV12/private native-Y files.
Changes: measure-rear.ps1, run-once.ps1, this README and current handoff/state.
Offline SP7 native PowerShell5.1 PASS: WinRT NV12 layout; constant scalar stats;
3840x2160 raw12441600bytes and native-Y PGM8294417bytes; duplicate write rejection.
Offline mode neither activates any camera nor consumes identity. Repeat that
offline validation on SP11 Windows before live task start.

Live mode requires SP11 DESKTOP-AQ4SMTC and protected root ACL, atomically
creates CONSUMED.txt before camera access and establishes240second return reboot.
Only exact Surface Camera Rear is initialized; front and IR never opened.
Select exactly one3840x2160 NV12 30/1 advertised format, validate delivered
planes/extent without guessed stride; wait5s then16 sparse samples500ms apart.
Require16 strictly advancing source timestamps. This does NOT measure30fps.
Windows exposure/white-balance/ISO values are API reports, not sensor registers;
no automatic control setters, effects/AI requests or driver configuration changes.

Preserve exact CPU NV12 buffers at indices8,12,15 plus native Y PGM at12,
PRIVATE on same SP11 ONLY. Never export pixels/PGM/NV12/thumbs/spatial arrays or
image-derived hashes through PiMaster/chat/Git/SP7. Global scalar aggregates,
code, format/plane metadata and source-script hashes are permitted. Directory
ACL limited to Geoca,SYSTEM,Administrators before any camera access.
Windows private root: C:\Users\Geoca\Documents\SP11-Camera-Native-Rear-Screen-20261007-01
Task SP11-Native-Rear-Screen-20261007-01: interactive Geoca, ON-DEMAND/no triggers, one Start only;
wrapper unregisters exact task after run. Existing consumed ID must never rearm.

Expected: one clean reader start/stop,16 advancing timestamps,3 exact-size private
NV12 files and one native-Y PGM, scalar controls/format/luminance recorded.
Rollback: one-use Windows EFI BootNext, persistent BootOrder unchanged; bounded
Windows reboot returns protected Golden Linux. Golden kernel/audio/display/touch/
power/USB assets untouched and exact Golden hashes checked before/after:
vmlinuz bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a
initrd ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d
DTB 2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00
Current Golden efcd9f1f-9608-48fe-8612-7b51a3dfb95c, no camera process/nodes/modules.

Scene limitations: no measured lux, independently confirmed FOV/scene continuity
or registered healthy-screen ROI yet. SP7 brightness hardware readback26
at2026-10-07T20:38:32.7020979Z; no brightness/content changes made.
Its permanently dark LOWER LCD band is not a camera fault. Restrict later
screen comparison to independently registered healthy upper display ROI.
This baseline alone does not prove Linux rear processed output or optical parity.
Next: resume source-built native rear ISP integration with a single explicit
delivery gate; front meter/AE calibration remains deferred.

## Completed — consumed, never rerun

Windows physical run PASS at20:47:13.623..20:47:27.459UTC,16 strictly advancing
samples; private full-resolution NV12 indices8/12/15 and nativeY PGM12 exact sizes.
Reader Stop and capture Dispose successful; task unregistered and wrapperexit0.
Private Windows root above retained; read-only NTFS copied originals ONLY to
/home/geoca/Pictures/SP11-Camera-Private-Native-Rear-Screen-20261007-01
with0700directory/0600files; partition unmounted afterwards. No pixels, spatial
arrays or image-derived hashes exported or committed.
Global sparse Ymean55.234..55.527,median55.322; P95=150/P99=158 all16.
These include the whole frame and are NOT registered healthy-screen-only IQ.
No lux/FOV/matched scene or optical parity claim. ExposureAuto APItrue/value5000
ticks, WBauto null/5000Kelvin and ISO0 are API outputs, not physical sensor truth.
Original Windows SOURCE.json is the preparation snapshot; consumed RESULT and
TASK-RETIRED markers are authoritative runtime evidence.
Derived scalar record docs/NATIVE-RGB-WINDOWS-REAR-SCREEN-01-20261007.json.

Golden return5a4d7226-d3b1-4c39-b94f-9d16ce4572ce verified; protected hashes and
persistent EFIorder unchanged,BootNext/GRUBnext empty,camera processes/nodes/
modules absent. Native44/33/66 unchanged; Windows2streams/2IDs/4boots,
combined70boots/35identities. Front calibration deferred until rear finished.
Next gate: executable rear packet-isolated semantic bootstrap and actual consumer,
then generation/stop-safe hardware delivery and private healthy-screen ROI IQ.
