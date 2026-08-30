# Windows RT-CDM BL boundary oracle — 2026-08-30

This directory freezes the same-SP11 Windows dynamic proof that resolves the ambiguous adjacent RT-CDM arena words seen in the earlier manual dump.

## Accepted facts

- qccamisp `FUN_140028480` / commit instruction RVA `0x28884` writes BL base to RT-CDM `+0x50`, encoded `(BL byte length - 1) | 0x00100000` to `+0x54`, then triggers `+0x58 = 1`.
- The live first-start queue submits a 4-byte `CHANGE_BASE 0x0000f000`, then the VFE main list, then a separate 4-byte `CHANGE_BASE 0x00057000`, then the CSID companion list.
- The arena word `0x0803c000` sits between those two 4-byte BLs but is skipped by the submitted descriptors. It is **not** a Windows command and must not be added to Linux.
- The submitted CSID RUP/AUP block is `REG_RANDOM [common +0x18] = 0x01f501f5` followed by `GEN_IRQ`. Replay1, replay2, replay3 and steady-state captured blocks all use the same combined value.
- Adjacent `0x000001f5` and `0x01f50000` words are likewise not submitted replay masks.
- The only CSID1 path enable observed is selector `5`, IPP. No hidden RDI/PPP enable is present in the captured first start.
- The RT-CDM anchor/base arithmetic remains exact: `0x0ac62000 + 0x0000f000 = VFE1 0x0ac71000`; `0x0ac62000 + 0x00057000 = CSID1 0x0acb9000`.

## Evidence

Raw logs are committed byte-for-byte from SP7 and hash-pinned by `extract_rtcdm_bl_boundaries.py`. The extractor also pins the corrected prior CSID ordering oracle and the independent CSID1 physical-base oracle. `EXTRACT.txt` is the deterministic extractor output; `windows-rtcdm-bl-boundaries-oracle.json` is the machine-readable accepted result.

This is a negative-search closure, not a Linux runtime authorization. The next gate remains the same-machine Windows first-start lifecycle after VFE BUS start and before sensor-on. Do not create a Linux `0x0803c000` or split-RUP delta from adjacent arena bytes.
