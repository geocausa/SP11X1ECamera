# E004ks Windows RGB numeric luminance reference

Fresh bounded Windows oracle to investigate nearly-black E004kr Linux front/rear samples. Uses exact existing Surface Camera Front/Rear colour VideoRecord source groups and default NV12 front1080p/rear4K. Eight in-memory luminance samples per camera after2seconds settling. No IR source, sensor/driver/3A control writes, pixel files or frame hashes. CPU bytes are cleared after aggregation. Timing and unique-frame identity are not proven; this is not a controlled scene or colour calibration.

Preflight on authorized SP7 passed PowerShell parsing, compiled numeric known-value test, and synthetic WinRT NV12 bitmap layout/copy/statistics; no camera opened. Host-bound SP11 live path creates an exclusive consumed marker before any camera operation and schedules a240second reboot first. Every reader/capture is disposed. Linux-to-Windows uses existing checked one-time EFI BootNext helper, preserving Golden GRUB default and EFI BootOrder. Results are numeric JSON only. Never rerun E004ks after its marker exists.

API sources: Microsoft SoftwareBitmap.CopyToBuffer and BitmapBuffer.GetPlaneDescription documentation. Luma stride must equal width with zero start offset; unexpected layouts fail rather than being guessed.
https://learn.microsoft.com/en-us/uwp/api/windows.graphics.imaging.softwarebitmap.copytobuffer
https://learn.microsoft.com/en-us/uwp/api/windows.graphics.imaging.bitmapbuffer.getplanedescription
