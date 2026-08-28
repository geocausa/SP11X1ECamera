# E003h Windows DMI execution diagnostic

Same-machine Windows remains the behavioral oracle. This follow-up answers one narrow question: whether the older public Qualcomm VFE17x direct LUT-dump sequence can be treated as the execution mechanism for the VFE680 DMI blocks seen in the exact Windows IFE command stream.

## Capture

- raw: `raw/E003H_DMI_EXEC_20260828.log`
- bytes: 12,432
- SHA-256: `8ccb149a22dddf21edb3b7115493a9000368a29c132f9dcfddc4867070c1e9cc`
- native source: `Surface Camera Front`
- WinRT reader: `StartAsync=Success`, normal `StopAsync` and dispose
- Golden restored afterward; kernel/initrd/DTB protected hashes matched, saved GRUB default was unchanged, and `next_entry` was empty

`extract_dmi_exec_oracle.py` is fail-closed against the exact raw hash and address/value pattern and regenerates `dmi-exec-summary.json`.

## Read-only phase result

For all ten observed VFE1 DMI access quartets (`+0x3d08`, `+0x4308`, `+0x4708`, `+0x4908`, `+0x5408`, `+0x5a08`, `+0x5f08`, `+0xa008`, `+0xa208`, `+0xb208`):

- IDLE: all four dwords read `0x80000000`;
- native LIVE: all four dwords read `0x00000000`;
- POST: all four dwords returned to `0x80000000`.

Therefore the selector/address/data-port state is transient; the live MMIO residue does not retain the selector encoded in the Windows CDM command.

## Bounded direct-DMI diagnostic

While the native Windows front reader remained live, one already-known nonzero table was tested at physical `0x0ac75708` (VFE1 `+0x4708`, Windows DMI selector 1). The diagnostic wrote only:

1. DMI config `0x101`;
2. DMI address `0`;
3. read the candidate data ports at `+0x10` and `+0x14` with address reads interleaved;
4. restore DMI config/address to zero.

The config read back as `0x00000001`, both candidate data ports remained zero, and the quartet was verified zero again before Windows completed a normal StopAsync.

This **rejects** importing the older Qualcomm VFE17x LUT-dump recipe as the VFE680 execution/read mechanism. The known nonzero `+0x4708` selector-1 payload was not exposed by that sequence.

## Exact Windows static consequence

The installed `qccamisp8380.sys` contains both a hardware-CDM path and a software-CDM command parser. Its software parser recognizes DMI opcodes but explicitly reports that DMI/LUT programming is unsupported and skips them. Separately, its resource parser recognizes literal `RT_CDM_0` and `RT_CDM_1` resources, maps each resource, and stores two RT-CDM bases.

That is not yet sufficient to claim the native front path uses hardware CDM. The next oracle must mechanically prove the native `SW CDM` field is zero / the hardware branch executes, and pin the two RT-CDM mapped/physical bases and hardware version. Until then, Linux DMI execution remains unauthorized.
