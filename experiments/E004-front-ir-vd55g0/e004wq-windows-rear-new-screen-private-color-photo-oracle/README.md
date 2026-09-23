# E004wq private rear-camera Windows photo after physically moving SP11/SP7

This is a NEW unique Windows single-use identity, distinct from retired E004wp/E004wn. The SP11 OEM Windows visible Surface Camera Rear Color VideoRecord 3840x2160 NV12 WinRT reader captures eight CPU-only real frames at the factory default with ExposureControl.Auto as an observation, no controls changed, no IR/illuminator or sleep. One genuine 960x540 rear COLOR PNG from nearest-neighbour native 4x4 subsampled Y+UV and one identically aligned grayscale PNG from original native Y are both PRIVATE only on SP11 Windows user Documents, intended for local same-machine comparison with independently captured Linux rear image. Provisional BT709 studio NV12 colour conversion is a rendering assumption, NOT calibrated native OEM YUV colourimetry, sensor colour fidelity or Windows/Linux ISP parity. No optical photos, pixels, preview thumbnails, image hashes or spatial tile/pixel arrays transmitted to ChatGPT, SP7, another host or Git. Only scalar global histogram/contrast reports may travel.

Windows user Geoca test folder is created with individual ACL to Geoca/SYSTEM/Administrators BEFORE any camera access. A Windows task must run under logged-on interactive Geoca identity and inspect exact SHA-256 of this script (code-only). The script uses CREATE_NEW CONSUMED.txt and schedules 300-second Windows system reboot BEFORE any actual camera API opens. It outputs one scalar-only RESULT.json after eight front/rear samples and validates both private PNGs are present. If Windows fails, the independent reboot still returns via persistent protected Golden Linux UEFI BootOrder, direct Windows BootNext one-shot only; a missing/failed Windows agent must not cause the task to open without reboot watchdog. Never reuse E004wq after consumption. User changed physical positions; scene contents may change between separate OS boots, so compare target presence and image geometry, brightness/contrast, not claim pixel-perfect matched scene or recognized screen without local measurement. Archive source-only + scalar results, leave optical PNGs strictly SP11-private.

## Actual 2026-09-23 OEM rear color photo and same-SP11 cross-OS comparison

Actual SP11 Windows OEM Rear Color WinRT default 4K NV12 produced
eight CPU frames with nominal automatic exposure and native luma
Y mean67.26–67.49, P99=175; front native1080p also eight frames.
One original rear 960x540 RGB colour (provisional BT709
NV12-to-RGB private preview) and identical-time grayscale photo
were verified locally on SP11 Windows; ACL Geoca/SYSTEM/
Administrators only. Task single-use consumed, exited0 and
unregistered. Windows originally scheduled 300s reboot BEFORE
opening cameras; automatic protected Golden Linux boot
0f6f6337-9eca-4547-8400-516ba7c88a13 observed, preserved EFI
BootOrder/Golden saved_entry, no pending camera/IR processes.
NTFS was subsequently mounted strictly READ ONLY on SAME SP11,
then unmounted cleanly after computing SCALAR-only real original
photo comparison and a user-private local side-by-side PNG.

Identical Windows private gray and current Linux original rear
gain color photo sampled native original pixels with 8x stride
to 480x270 (Windows OEM 4K decimated4x to960, then2x; Linux
4K decimated8x). Windows matched display gray meanY60.256 /
median45 versus Linux matched RGB meanY36.923 / median15.353.
Windows display-bright area Y>=96 covers25.4753% of image vs
Linux10.8102%; 99.7645% of Linux-bright pixels are ALSO bright
at the same coordinates in Windows. Coarse sigma8 spatial
correlation0.902659 (bounded small-shift best0.912981),
strong support that the SAME broad scene was sampled across
both OS boots, consistent with user moving SP7 monitor into
SP11 rear FOV. Windows renders a much larger bright region,
while Linux current opt-in gain rendering retains dark background
and only the brightest part of that corresponding region. The
matched fine sigma2 highpass correlation0.000851 (bounded
small-shift best0.091969) cannot verify recognized fine detail,
real sensor noise or Windows OEM processing parity. Separate
Windows and Linux sensor exposure/gain, scene content, backlight
brightness and capture times (~10minutes) were NOT controlled;
Windows colour preview was provisionally BT709-rendered only.
No screen text/object identity independently recognized; no
white-balance, accurate colour or full ISP image-quality parity
claimed. Linux E004nd ORIGINAL complete one-shot FAILED an
independent RAW10 frame600 timing gate 91.489ms after gain settle
vs required300ms, even though both optical photos and native
control restoration occurred. Preserve this original FAIL.

SP11 user-private side-by-side viewing file created from
both genuine original captures using EXACT native4x decimation
to each960x540 panel (not bilinear):
/home/geoca/Pictures/SP11-Camera-Private-E004wq/PRIVATE-SP11-REAR-NEW-SP7-SCREEN-WINDOWS-vs-LINUX.png
Owner geoca dir0700/photo0600, NEVER exported from SP11.
Original OEM Windows color and grayscale photos remain only in
C:/Users/Geoca/Documents/SP11-Camera-E004wq-Screen-Oracle/
and original Linux front/rear baseline+gain photos only in
/home/geoca/Pictures/SP11-Camera-Private-E004nd/.
No optical photos, pixels, private screen contents, RAW source
bytes, thumbnails, spatial heatmaps or image-derived hashes
were transferred through Fabric, returned to assistant/chat
or included in Git. Only original OEM scalar RESULT.json,
same-SP11 scalar matches, source-only scripts and text provenance
are retained for reproducibility. Next review Linux low-light
shadow/highlight handling with independently measured native
exposure/control and a fixed illuminated screen/neutral/dark
reference rather than treating global brightness tone as detail
or promoting opt-in changes to daily Golden.
