# E003h same-machine Windows dynamic lifecycle oracle

Date: 2026-08-28

Behavioral policy: Windows on this exact Surface Pro 11 is the oracle. These artifacts resolve only the cross-driver ordering between the Windows ISP lifecycle and the IMX681 stream-on/off apply points.

## Exact artifacts

- `E003H_LIFECYCLE_ABS_20260828.log`
  - 51,296 bytes
  - SHA-256 `2908392a619b14f229161dec616e43052103b53b161a3fc77edda56b782d1b36`
  - raw UTF-16LE KD `.logopen /u` capture
- `e003h-abs-lifecycle.kd`
  - 559 bytes
  - SHA-256 `7413f63bc7bcc4bb46f749829ce1f26e6b7632d4004e79734b431ae1211d2c04`
  - absolute breakpoint command file; contains no KDNET credential
- `E003H-WinRT-Holder.ps1`
  - 3,809 bytes
  - SHA-256 `7eb5971788d89024ef85614774866ddf205ba39c2b9ded618890ee0eef7ddd75`
  - exact Windows-side holder bytes copied read-only from the Windows NTFS partition after return to Golden
- `extract_lifecycle_order.py`
  - deterministic parser/validator
- `lifecycle-order-summary.json`
  - generated parser result

## Capture identity

Immediately before the accepted capture, the active DriverStore files re-hashed to the already accepted static oracle values:

- `qccamisp8380.sys`: `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`
- `qccammipicsi8380.sys`: `033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407`
- `surfacecamfrontsensor8380.sys`: `80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03`

Same-machine kernel enumeration gave live bases `qccamisp8380=0xfffff802eed70000`, `qccammipicsi8380=0xfffff802eb340000`, and `surfacecamfrontsensor8380=0xfffff802ef200000`. The absolute breakpoint addresses in the KD script were derived from those bases plus the statically decoded RVAs.

The holder hard-selects the `Surface Camera Front` source group and refuses to start unless the chosen color source's own `DeviceInformation.Name` is exactly `Surface Camera Front`. Two independent runs both completed `MediaFrameReader.StartAsync=Success` and normal `StopAsync()`.

## Accepted result

`extract_lifecycle_order.py` ignores the noisy ISP start/stop *entry* sites because those addresses are internal command-path locations and fire hundreds of times. It accepts only exact runtime marker lines for the unique completion/sensor apply sites.

Cycle 1:

`ISP_START_DONE` line 22 -> `SENSOR_STREAM_ON_APPLY` line 25 -> `ISP_STOP_DONE` line 422 -> `SENSOR_STREAM_OFF_APPLY` line 423.

Cycle 2:

`ISP_START_DONE` line 435 -> `SENSOR_STREAM_ON_APPLY` line 438 -> `ISP_STOP_DONE` line 831 -> `SENSOR_STREAM_OFF_APPLY` line 832.

Therefore the same-machine Windows cross-driver order is reproducibly:

**ISP start complete -> sensor stream-on apply**

**ISP stop complete -> sensor stream-off apply**

Combined with the separately proven static ISP-internal order, Windows uses:

**start: IFE -> initial IFE/CSID config -> CSID -> sensor `0x0100=0x01`**

**stop: CSID -> IFE -> CDM/remaining core -> sensor `0x0100=0x00`**

This does not by itself place the Windows MIPI/CSIPHY power/open/close operations relative to the ISP operations.
