# Fresh SP11 Windows E004wp current rear-light oracle

PHYSICAL WINDOWS RGB ORACLE PASSED, SINGLE-USE ID CONSUMED/TASK RETIRED, GOLDEN RETURNED. Distinct single-use Windows identity
E004wp, NEVER reuse E004wn or its Scheduled Task. Uses fresh interactive
Geoca Windows Scheduled Task and WriteAllText scalar result. Exclusive
CreateNew consumed marker and a 300s watchdog reboot MUST be established
BEFORE either front/rear visible Color VideoRecord NV12 WinRT stream opens.

Eight frames each front1080/rear4K, native CPU NV12 luma sampled each
64th horizontal pixel/all rows and p01/p50/p95/p99, mean, fractions
below20/32, spatial 8x8 tile std, horizontal64/vertical32-pixel sampled
absolute Y differences. Nominal WinRT auto exposure read, no control
changes or IR/illuminator. Just one 960x540 rear grayscale PNG
derived from every fourth 4K NV12 Y sample and nominal 16-235->0-255
display mapping is generated strictly in the SP11 Windows user's private
Documents folder. This PNG is NOT full-color, not an image-quality proof;
no photo, thumbnail, pixels or image hash is returned to tools, Git or
another machine. The Windows operator can view this locally for geometry;
scalar brightness/contrast are the only remote analysis. No Linux OS
suspend/resume, no persistent EFI boot order or Golden change.

No current optical illumination or rear physical field-of-view was
independently verified. Comparing with prior Linux E004mp is NOT a
same-time/same-control Windows ISP sensor parity experiment.

## Actual current Windows result — 2026-09-23 ~11:58 BST

SP11 booted Windows through direct EFI BootNext (persistent BootOrder and
saved Golden unmodified), ran the fresh interactive Geoca task under a
hash-pinned source, consumed unique local CreateNew marker and set the
300-second shutdown/reboot BEFORE opening either Color VideoRecord
WinRT NV12 camera. Front1080 and rear4K each returned eight CPU frames,
no IR, illuminator, test pattern or control change. Task exited0 and
was unregistered at 11:59 BST; Windows event1074 verifies bounded
return shutdown was scheduled at 11:58:09 BST. At 12:04:49 BST SP11
returned automatically to protected Golden Linux boot
`fe4bcab8-a209-4466-819e-0ce7fbeabc03`; safety guard found no
pending experimental boot, camera nodes/modules/processes or tracked
Git changes; EFI BootOrder was unchanged.

**Windows rear is NOT too dark in its current view:** eight native rear
3840x2160 NV12 frames showed mean Y149.151–150.412, p01 Y118–119,
p50 Y151–152, p99 Y169–171, and ZERO sampled pixels below Y64.
8x8 tile-mean std Y11.458–12.058, horizontal64-pixel mean absolute
Y difference3.320–3.388, vertical32-pixel difference3.289–3.325.
The front mean Y124.874–125.193 and p99 Y254–255. Both WinRT RGB
ExposureControl.Auto=true, nominal value5000 ticks; this is NOT a
verified sensor register exposure readback. Previous independent fresh
Windows E004wn captured rear mean Y148.237–148.554 at ~11:16 BST,
consistent with current Windows auto-rendered bright rear. Neither
scene geometry, physical illumination nor Windows exposure was matched
to Linux E004mp ~11:34 BST, and Linux RGB PNG p99 is NOT the same
statistic as Windows native NV12 mean. The nonuniform Windows brightness
shows measurable spatial contrast but alone does not certify a
recognizable object, color fidelity, true optical SNR or OEM parity.

Exactly ONE 960x540 private rear grayscale PNG, derived from the
4K native NV12 luma plane and nominal studio-to-full display mapping,
was saved ONLY on SP11 Windows at
`C:\Users\Geoca\Documents\SP11-Camera-E004wp-Current-Rear-Light\REAR-WINDOWS-PRIVATE-GRAYSCALE-960x540.png`.
This is intentionally not full-color or full-resolution. The folder
ACL allows only Geoca, SYSTEM and Administrators. The PNG was locally
verified as PNG with 960x540 dimensions; pixels were NEVER retrieved,
transferred, displayed to assistant, hashed, committed or analyzed
outside SP11 Windows. The user can inspect it directly when they boot
Windows. The repository and SP7 relay received only numeric scalar
RESULT.json, never the grayscale image. Its scalar-only archived
`evidence/RESULT.json` and `SUMMARY.json` contain current capture
measurements; Windows-original scalar SHA is recorded in transfer
provenance (not an image hash). NEVER reuse E004wp identity.

The diagnosis is that Windows can auto-expose/render a bright rear
corner, while the existing Linux fixed-gain/near-max-current-exposure
software proxy still outputs a very dark RGB image. It does NOT prove
that the corner is bright in native RAW under equivalent exposure,
or that Linux OV13858 hardware is faulty; lighting, processing and
capture times were not matched. Preserve protected IR OFF and Golden;
next image-quality acceptance still needs a fixed visible-lit target,
independent dark reference, and locally inspected real scene detail.
