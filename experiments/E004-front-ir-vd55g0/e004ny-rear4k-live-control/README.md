# E004nx / E004ny — real Windows rear 4K frames without KD; live BF event still unproven

Parent: E004nv `fe96bbf42dbba2b92c2547795193afadca5633f4`. E004nv proved, from the unchanged private same-SP11 ARM64 `qccamisp8380.sys`, a **static** OEM BF event `0x0F` dispatch and independent FIFO group index 8. The earlier E004nw live BF attempt had a successfully armed SP7 KDNET one-shot breakpoint, but its simultaneous Windows rear-4K WinRT frame reader returned **zero frame handles**, despite `StartAsync=Success`. Thus that attempt did **not** observe a live BF hit or prove a running Windows rear output pipeline. Original private KD logs remain on SP7, and no debugger credential, memory pointer, image data or OEM binary is included in Git.

## Measured follow-on results

Two NEW one-use, **same physical SP11** Windows rear `MediaFrameReader` captures used `Surface Camera Rear` / Color `VideoRecord` / NV12 3840×2160. Both were invoked manually in the logged-on Windows user session, with no future scheduled trigger. Each script created its own exclusive `FileMode.CreateNew` entry marker **before** contacting the camera. No SoftwareBitmap pixel plane was locked or copied and no optical image, thumbnail or photo hash was produced. All handles were immediately disposed. The Windows ScheduledTask for E004ny was unregistered after successful completion.

| Evidence | KD attached during capture | Pass 1 | Pass 2 | Outcome |
|---|---|---:|---:|---|
| Prior E004nw BF trial | KDNET breakpoint armed, attachment/connection disrupted | 0 handles | Not run | `StartAsync=Success` but minimum-frame guard failed. No BF hit. |
| **E004nx** short no-KD baseline | No | **365** valid 4K handles in 35.045 s | **366** in 35.084 s | Both `StartAsync` and `StopAsync` successful; **731** valid handles. |
| **E004ny** extended pre-verification | No | **1,152** valid 4K handles in 110.037 s | **1,154** in 110.030 s | Both `StartAsync` and `StopAsync` successful; **2,306** valid handles. |

E004ny emitted a single-use **12-valid-frame** checkpoint in **both** passes before any proposed KD intervention. The SP7 KD launch for this follow-up was **blocked by a tool safety check**, so the debugger was never attached to this E004ny recording. It is therefore a second, longer **no-KD control**, *not* a BF event trace. The difference between the earlier zero-frame KD-involved attempt and two healthy no-KD sessions is a useful experimental discriminator, **not proof that KD caused the earlier failure**: the previous test also had differing timing and connection conditions.

The only retained data in `e004nx-rear4k-no-kd-baseline/RESULT.json`, `E004NW-PRIOR-FAILED-REAR4K-SCALAR.json` and this directory's `RESULT.json` are source-derived camera type/format, boolean test conditions, frame-handle counts, durations and failure wording. `e004nx.../WINDOWS-RUN-SOURCE.ps1` is the exact Windows E004nx user-authored source; this directory's `hold-rear4k-then-KD-singleentry.ps1` is the exact Windows E004ny source. Neither source reads pixels, maps OEM buffers or contains a KD credential. The Windows original raw phase marker/log files remain private on SP11 Windows; no proprietary OEM driver, tuning, firmware or private SP7 KD log was copied into Git.

## Safety, verification and remaining engineering

The single-use Windows direct-EFI BootNext was used without altering persistent Linux-first BootOrder. After E004ny's DONE marker, the manually registered scheduled task was unregistered and Windows restarted normally. SP11's **new** Linux boot was verified on protected Golden kernel `7.1.5-sp11-render-parity-v4+`, GRUB saved entry `sp11-audio-fullio-v19c`, `BootCurrent: 0005`, unchanged `BootOrder: 0005,0004,0000,0001,0002,0006`, no BootNext, no loaded camera module or active camera process; the protected camera overlap guard passed. The Windows NTFS source was mounted **read-only** to copy only whitelisted user-authored scripts/scalar results and was immediately unmounted. Original integrated kernel, Denali DTS and accepted front camera / Linux rear RAW / rear software4K paths remain unchanged.

Run the new offline `verify.py` to validate exact source checksums and cross-compare all three captured test outcomes plus **14 deliberately corrupted, fail-closed cases**. None of these tests exercises live Linux camera hardware or changes Golden.

```bash
cd /home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
PYTHONDONTWRITEBYTECODE=1 python3 experiments/E004-front-ir-vd55g0/e004ny-rear4k-live-control/verify.py
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```

**Next dependency:** A separately authorized and successfully connected debugger capture of a **live rear BF event `0x0F` / group 8** *during* verified frame delivery, followed by real WM16 buffer completion and metadata/ring ownership proof. Do **not** claim that the static OEM BF branch alone, or these application-visible Windows 4K frame counts, prove the actual BF completion. The isolated Linux E004nr/E004ns/E004nt/E004nu/E004nv compiled rear source remains **unarmed**; independent rear IQ/3A/RT-CDM programming, per-group stats DMA and safe exclusive CSID1/VFE1 core switching are still missing. A Linux-native rear 4K ISP optical frame is **not yet proven**.
