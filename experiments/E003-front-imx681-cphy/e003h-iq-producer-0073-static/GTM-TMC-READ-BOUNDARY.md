# E003h 0073 — exact GTM131 ← TMC v5 read boundary

Status: **accepted static/offline checkpoint**. This checkpoint performs no Windows camera run, no Linux camera runtime, no MMIO and no request6 submission.

The remaining GTM producer input is now bounded much more tightly than the previous coarse TMC-object plan. In the exact SHA-pinned Surface DeviceMFT, IFE GTM reads the published TMC/ADRC pointer from `ISPInputData+0x21d0`, selects `IFEGTM131 module+0x130` as its internal TMC buffer, installs that pointer at GTM common-input `+0x50`, and—when the published state says it is valid—calls RVA `0x898738` to convert the published layout into that internal layout. The exact IFE GTM hardware-setting dispatch slot `+0x4b8` resolves to RVA `0x9aa6e0`.

This gives a clean future Windows capture point: **RVA `0x9aa6e0`**, filtered to the IFE call by LR **`0x180a28f2c`**. At that entry `x0` is the GTM common input, `x1` is the already-interpolated 257-float/`0x404` GTM region, `x2` carries the calculation flags, `x3+4` supplies the setting halfword, and `poi(x0+0x50)` is the exact converted TMC object consumed by GTM.

For the TMC generation-5 branch (`dwo(tmc+0x08) == 5`), GTM does **not** consume the whole `0x8278`-byte published object. Its exact dynamic reads reduce to these internal-layout ranges:

- `+0x0008`, `0x0c` bytes — generation / hardware-version / valid header dwords;
- `+0x0074`, `0x04` bytes — curve interpolation mode;
- `+0x109c`, `0x08` bytes — the two curve-blend scalars;
- `+0x5104`, `0x1c` bytes — seven-float source knot array;
- `+0x5120`, `0x1c` bytes — seven-float target knot array;
- `+0x51b0`, `0x3c` bytes — 15-float cubic coefficient block used by mode 2;
- `+0x6228`, **maximum `0x1000` bytes** — dynamic tone-curve domain.

The last range is deliberately bounded at the exact worst case rather than assuming the target's hardware-version field. The helper uses 256 floats only when internal `+0x0c == 0x60400`; otherwise it uses 1024 floats. Capturing `0x1000` bytes therefore remains fail-closed without guessing the target branch.

Those sparse ranges total only **`0x108c` bytes**, versus the full published **`0x8278` bytes**. Including the GTM common input through `+0x78` yields `0x1108` bytes. Including the known `0x404` interpolation input and the tiny `x2`/`x3` auxiliary inputs still totals only `0x1512` bytes before the separate `0x800` post-calculation validation result.

The capture must fail closed if the selected TMC pointer is null, `tmc+0x10` is zero, or `tmc+0x08` is not generation 5. In that case we stop and revise the branch-specific contract instead of treating a different TMC layout as v5.

After the hardware-setting call, the IFE path copies exactly `0x800` bytes into cached staging at `IFEGTM131 module+0x138`. That staging is the correlation target for requests 4/5/6 and must reproduce the matched Windows request6 GTM0 bytes offline before Linux request6 is reconsidered.
