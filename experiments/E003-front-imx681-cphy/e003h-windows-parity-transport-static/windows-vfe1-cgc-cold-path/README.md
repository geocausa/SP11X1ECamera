# E003h SP11 Windows VFE1 CGC cold-path oracle

Installed qccamisp8380.sys SHA-256: `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`.

Cold same-machine sequence:

1. All user camera holders were stopped and Windows FrameServer was stopped.
2. The Qualcomm camera device was restarted under KD with `sxe ld:qccamisp8380`.
3. KD stopped on a fresh qccamisp load at `fffff802`48490000`.
4. Before device initialization resumed, breakpoint `qccamisp+0x1be80` was armed. This is the selector-zero SP11 IFE1 callback which statically contains the BUS CGC override write `+0xc08 = 0x1ff`.
5. The exact retained WinRT front holder then initialized Surface Camera Front and reached `E003H_START_STATUS=Success`.
6. The `qccamisp+0x1be80` breakpoint did not execute in this successful cold-reload/front-stream path.
7. After successful streaming, the newly allocated IFE1 context was resolved dynamically:
   - qccamisp global at `+0x4ae88` -> `ffffb588`6f7c6000`
   - record array `[global+0x30]` -> `ffffb588`6bb97880`
   - IFE1 context `[record_array+0x58]` -> `ffffb588`72202000`
   - BUS mapping `[context+0x150]` -> `ffffc880`f5d97c00`
   - live BUS `+0x08` / VFE aperture `+0xc08` -> `0x00000000`

Raw KD log: `E003H_VFE1_CGC_COLD_ENTRY_20260831.log`
SHA-256: `1103a45dd26584f32337a338fb7db0c5a51baa37fbe35ca21e166b557603d20f`
Length: 4417 bytes.

Holder success is preserved separately in `HOLDER-SUCCESS.txt` because it originated from the SP11 Windows connector job, not from KD.

## Consequence

This does **not** prove Windows never writes `0x1ff`; static reversal proves callback `0x1be80` contains that write in another lifecycle. It proves a successful same-machine qccamisp unload/reload + front-stream path exists where that callback is not executed and live `c08` remains zero.

Therefore the next bounded Linux differential is justified as a diagnostic: remove only the private X1E80100 VFE1 `BUS +0xc08 = 0x1ff` write. Do not add a compensating zero write, do not alter IRQ event selection, and do not alter sensor/CSID/clocks/RT-CDM/BUS client or UBWC programming.
