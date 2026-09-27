# E008v — bounded Windows rear normal BF ROI oracle

Status: **STREAM PASS; INTERMEDIATE ROI STAGE NOT OBSERVED**.
Parent: E008u `ee8e3683f3925422dbc73e6a2bca460044c5032c`.

The fresh original-Windows rear color VideoRecord NV12 3840×2160 holder
initialized and started successfully on 2026-09-27. It ran for 12 seconds,
stopped cleanly, and acquired 284 valid 4K handles. During the active stream,
`QcDeviceMFT8380.dll` loaded in the FrameServer process (PID 10428). This
confirms the user-mode MFT owner was present in the live original stack.

An auto-detach CDB probe against a disposable process did not complete
safely, so no debugger was attached to FrameServer and no AF semantic ROI
or BFStats25 intermediate stage was captured. The packet1→2 position shift
therefore remains unattributed; E008u's packet0-only parity is unchanged.
Do not promote the tentative vertical-basis fit or captured ROI coordinates
into the clean driver.

The original holder log and Windows-side safe runtime checkpoint are private
on SP11 at `C:\Users\Geoca\Documents\E008V-holder.log` and
`C:\Users\Geoca\Documents\SP11CameraPrivate\E008v\SAFE-RUNTIME.json`.
No pixels, raw DMI, proprietary binaries, or private logs are committed.
The SP11 returned by ordinary reboot to Golden Linux
`7.1.5-sp11-render-parity-v4+` with saved GRUB
`sp11-audio-fullio-v19c`, empty `next_entry`, no camera nodes/modules/
active processes, and overlap guard PASS.

Next: static decompile of the exact pinned AF/BAF normal ROI mapper and
BFStats25 validation/adjust path; compare the clean offline output against
private packet1–3 DMI. Runtime rear ISP remains denied until exact parity.
