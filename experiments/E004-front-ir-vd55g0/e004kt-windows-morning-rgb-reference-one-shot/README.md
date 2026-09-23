# E004kt — fresh morning Windows front/rear RGB luminance oracle

On 2026-09-23 SP11 booted Windows via safe one-shot EFI BootNext 0006.
A NEW `E004kt` PowerShell copy of previously offline-tested E004ks used
its OWN CreateNew consumed marker and ran once in interactive Geoca session.
Windows scheduled an automatic 240-second return reboot BEFORE camera
access; the script read only exact `Surface Camera Front` and `Surface Camera
Rear` *colour* WinRT VideoRecord NV12 CPU buffers, front1920x1080 and
rear3840x2160. Eight scalar luminance samples each, per-64th-pixel horizontal
sampling and all rows. No controls modified, no IR or illumination, no pixel
file/image hash/photo exported. Both readers disposed and one-shot consumed.

Windows morning NV12 sparse sample mean Y front 123.169–123.578 (sampled
min1/max255), rear151.475–151.900 (sampled min86/max194). WinRT
ExposureControl reported Auto=true and nominal 5000 ticks for both; that
is NOT independent sensor-register exposure evidence. In earlier E004mf
Linux morning samples (~12 minutes earlier) *different* statistic app Y p99
front27/rear17 baseline, front59/rear25 with a bounded gain/exposure trial.
These were not simultaneous, geometrically/pixel calibrated or illuminance
matched; nor are mean and p99 the same statistic. Nevertheless their large
qualitative disparity warrants diagnosing Linux AEC/sensor timing/RAW code
black-offset and software tone mapping rather than blaming Linux converter
alone or assuming physically dark rear optics. The older E004ks Windows
reading was also dark under different light (front mean~12/rear~7), so scene
illumination itself can change dramatically across captures.

The original Windows RESULT.json (UTF-8 BOM), fresh source PowerShell,
CONSUMED marker and SHA-256 digest manifest are archived in evidence/. The
user-visible original remains privately on Windows, no optical pixel dump.
After Windows returned protected Golden cd3d87b3-0940-49f8-b204-145a2cbedce6,
the single-use scheduled task's otherwise future trigger was explicitly
removed WITHOUT any camera access, cleanup proof archived, and Windows
rebooted into protected Golden a9dfed2b-7097-4a55-ba9b-67bb693743e4.
EFI BootOrder 0005,0004,0000,0001,0002,0006 unchanged; GRUB saved Golden,
next_entry empty; no camera nodes/modules/processes. NEVER rerun E004kt.
