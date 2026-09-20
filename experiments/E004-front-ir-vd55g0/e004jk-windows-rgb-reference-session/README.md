# E004jk — same-machine Windows RGB format and delivered-buffer baseline

**Date:** 2026-09-20. **Status:** Windows reference collected; Golden safely restored.
Scope: front/rear *RGB only*. No IR illumination, Hello, KD, Windows driver modification or permanent Linux camera activation.

## Reproducible route and safety

Started on protected Golden with `camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process` passing. `tools/sp11-camera-windows-oracle-oneshot.sh --check-only` verified unique `Windows Direct Oracle Temp` pointing to actual `EFI/Microsoft/Boot/bootmgfw.efi`, the persistent EFI BootOrder `0005,0004,0000,0001,0002,0006`, and Golden saved GRUB entry `sp11-audio-fullio-v19c`, with no pending GRUB next entry. Armed firmware **BootNext=0006** only, no persistent order change. Windows PiMaster agent came online, and the read-only WinRT camera inventory/CPU-buffer acquisition script in `oracle/` ran under the signed-in user (PowerShell local-process execution-policy override; system policy unchanged). Windows then rebooted; Linux returned on Golden boot ID `9adcc518-173f-4cff-bd9f-3c6087bc5a04` with no camera nodes/modules/processes, empty GRUB `next_entry`, unchanged Linux-first EFI BootOrder, clean tracked repository.

The Windows private original is retained **only on the machine's Windows filesystem**, `Documents/SP11-Camera-Windows-Reference-20260920/rgb-probe-20260920-221438.json` (SHA-256 `3bcc114bdff518481021c6979dbaef75b63cb448929df5cbc81b2d50aceb1b50`). It contains 135 nonimage frame-handle observations. It was independently read from Linux through a **read-only, immediately unmounted NTFS mount**, verified and distilled into `evidence/windows-rgb-observations.json` without the Windows machine name. No private image or video was exported or committed.

## Windows-observed camera modes

| RGB source | Actual default WinRT SoftwareBitmap | Buffer acquisitions | Additional advertised formats |
| --- | --- | ---: | --- |
| Rear `VideoPreview` | NV12 1920×1080 | 45/45 CPU-accessible | NV12 2560×1440; 1920×1440; 1440×1080; 1280×720; 640×480; 640×360 |
| Rear `VideoRecord` | **NV12 3840×2160** | 45/45 CPU-accessible | NV12 2560×1440; 1920×1440; 1440×1080; 1920×1080; 1280×720; 640×480; 640×360 |
| Front `VideoRecord` | **NV12 1920×1080** | 45/45 CPU-accessible | NV12 **2560×1440**; 1920×1440; 1440×1080; 1280×720; 640×480; 640×360 |

All listed modes advertise **30/1 fps** in WinRT `SupportedFormats`. This is **not** a measured sustained frame rate. The probe selected each source's default format, independently started one reader at a time, acquired 45 handles, and verified that each handle exposed a CPU-accessible `Nv12` `SoftwareBitmap` with the expected pixel dimensions. This proves Windows delivers frame buffers at **rear 4K** and **front 1080p**. **Front 2560×1440 remains advertised only**, not yet successfully set and sampled. One capture handle does not prove a unique new sensor frame. Every probed WinRT `SystemRelativeTime` and `Duration` was null; elapsed host polling time cannot establish hardware cadence.

## Parity gates these results define

1. On Linux, verify physical rear 3840×2160 video *buffers* and 1920×1080 preview delivery separately; prior E004jh's **1920×1080** real optical virtual camera is not yet equivalent to Windows **4K recording**.
2. Prove front real **1920×1080** NV12 RGB frames and independently test **2560×1440** delivery. Oaklee's published 720p browser demo and our 27 compressed QC10C frames do **not** satisfy the Windows-delivered front 1080p baseline.
3. Independently time frame IDs / timestamps, CPU/GPU cost, start latency, mode-switch/reopen reliability, sustained stability, video conferencing application selection, power/thermal, suspend/resume.
4. When user-authorized pixel export is feasible, store Windows reference images locally/private, select fixed scenes and matched settings, measure crops/FOV, centre and corner detail, motion, exposure/white-balance response, colour/black level, dynamic range, noise, frame drops and output latency against Linux. Do **not** infer image quality from buffer dimensions.
5. Still-photo resolution, in-app video recording and actual front 1440p streaming remain separate untested Windows gates. IR/Hello excluded by user's initial compromise.

The separately staged Windows raw-pixel export script was **not executed** because its remote execution was blocked. No `.nv12`, PNG, or raw optical reference files were created. Do not count it as a pixel-quality baseline. The Windows original metadata JSON and inventory script remain on the Windows filesystem; only the successfully run *metadata* script and redacted observations appear in this repository.

Run `python3 experiments/E004-front-ir-vd55g0/e004jk-windows-rgb-reference-session/verify-e004jk.py` to validate the supported-format/delivered-buffer distinction.
