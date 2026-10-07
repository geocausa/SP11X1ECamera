# Front room-light Windows reference — fresh01

E-NATIVE-FRONT-WINDOWS-LIGHT-01. Native WinRT FRONT Color/VideoRecord only.
Derived from already tested E004kt numeric camera probe. Select exact2560x1440
NV12 30/1 source matching Linux03/04 output geometry.16 sparse Y measurements,
horizontal stride64/all rows. CPU data cleared after aggregate computation;
no optical files/hashes/export,IR,drivers modified,AI/effects requested.
Windows normal automatic controls untouched. ExposureControl.Value is only
reported WinRT metadata,not a verified sensor register. ISO optional may be absent.
Frame system-relative timestamps recorded if projection supplies them; never
infer unique hardware cadence just from polling. Media-format scalar properties
recorded by GUID without assigning undocumented semantics.

-OfflineTest has no camera access and does not consume identity. Live mode
atomically creates CONSUMED.txt BEFORE any camera access and establishes a
240-second automatic reboot before opening the source. Run only once in signed-in
SP11 Geoca Windows session via on-demand task with no scheduled trigger.
The wrapper must unregister that exact task after execution. Never rearm consumed.
Windows boot is one-shot direct EFI BootNext; persistent Linux-first/Golden retained.
Room lights user-reported ON18:26:29UTC. Keep scene/camera/position/light unchanged.
No lux measurement or independent scene continuity guarantee. Linux-before03 is
fixed manual controls,Windows auto; diagnostic brightness comparison only unless
settings/range/scene can be separately qualified. Fresh Linux-after04 completes
bracket. Do not call image quality parity from dimensions or raw mean Y alone.

## Completed and consumed

Fresh01 successfully selected and delivered2560x1440 NV12,16 advancing source
timestamps,meanY88.067..89.561. Single live run completed18:46:40.428UTC and
task unregistered. Initial bootstrap guard mistook null trigger list for1 and
removed task beforeStart/noCONSUMED/noRESULT; audit proved zero camera access.
Corrected bootstrap validates exported Task XML actual trigger children0.
Do not reuse this identity. Original metadata/source/manifests private Windows.

Linux03/04 bracket complete; sparse restored-baseline medians5.088229/4.940304,
difference2.907%. Windowsmedian88.255408. This compares automaticWindows against
fixedmanualLinux,not matched sensor exposure/gain or image-quality parity. Scene
identity/FOV/lux unqualified. Source-timestamp uniqueness does not establish FPS.
Both declared full range,official SDK MF GUID/enum checked; no transfer/black
photometric calibration. Derived reports contain no pixels or image hashes.
Timing gate closed: exposure/analogue/digital empirical response2 on both Linux
runs. Next standard libcamera DelayedControls and calibrated bounded AE.
