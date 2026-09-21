# E004ks Windows RGB numeric luminance reference

Fresh bounded Windows oracle to investigate nearly-black E004kr Linux front/rear samples. Uses exact existing Surface Camera Front/Rear colour VideoRecord source groups and default NV12 front1080p/rear4K. Eight in-memory luminance samples per camera after2seconds settling. No IR source, sensor/driver/3A control writes, pixel files or frame hashes. CPU bytes are cleared after aggregation. Timing and unique-frame identity are not proven; this is not a controlled scene or colour calibration.

Preflight on authorized SP7 passed PowerShell parsing, compiled numeric known-value test, and synthetic WinRT NV12 bitmap layout/copy/statistics; no camera opened. Host-bound SP11 live path creates an exclusive consumed marker before any camera operation and schedules a240second reboot first. Every reader/capture is disposed. Linux-to-Windows uses existing checked one-time EFI BootNext helper, preserving Golden GRUB default and EFI BootOrder. Results are numeric JSON only. Never rerun E004ks after its marker exists.

API sources: Microsoft SoftwareBitmap.CopyToBuffer and BitmapBuffer.GetPlaneDescription documentation. Luma stride must equal width with zero start offset; unexpected layouts fail rather than being guessed.
https://learn.microsoft.com/en-us/uwp/api/windows.graphics.imaging.softwarebitmap.copytobuffer
https://learn.microsoft.com/en-us/uwp/api/windows.graphics.imaging.bitmapbuffer.getplanedescription

## Actual result
PASS eight numeric samples per camera, no optical files/hash export and no control writes. Front NV12 1920x1080 meanY11.544–12.618, sampledY5..152. Rear NV123840x2160 meanY7.170–7.630, sampledY0..27. These Windows observations also have low luma overall; the front spans a wider sampled range than E004kr LinuxY15..17. Neither scene nor exposure/transfer/range/FOV was controlled across the OS reboot, so do not infer calibration, equal illumination, exposure equivalence or the cause of differences. WinRT reports exposureAuto=true, nominalValue5000ticks and whiteBalanceValue5000; no proof those are exact sensor registers. White-balance Auto was unavailable/null, not false. No fps or unique-frame claim.
Returned protected Golden boot1c4ba1bc-9728-42a0-bc81-6192d4966c98 with unchanged EFI order and saved GRUB default, empty next entry, no camera nodes/modules/processes. E004ks is consumed; the private Windows marker prevents rerun. A lit controlled scene is required for meaningful colour/detail/response calibration. Production endpoint/access/lifecycle engineering remains separate and can continue.
