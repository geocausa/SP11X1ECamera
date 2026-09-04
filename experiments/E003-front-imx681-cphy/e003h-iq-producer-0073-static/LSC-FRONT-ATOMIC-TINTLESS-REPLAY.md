# E003h 0073 — verified-front atomic Tintless replay

Status: **accepted offline/native Surface replay checkpoint**. No Linux camera runtime or Linux request6 was executed or authorized.

## Source capsule

A fresh 2026-09-04 Windows capture records one continuous IMX681 front stream at Tintless wrapper RVA `0xc95fd0` for requests 4, 5 and 6. The wrapper config geometry is invariant and uniquely front:

- output `3840x2160`;
- Tintless cells `120x90`;
- cell size `32x24`;
- packing `0`.

The tracked manifest `FRONT-ATOMIC-TINTLESS-STAGING-20260904.json` SHA-pins 44 raw local/untracked captures. Request4 wrapper state starts with a null lazy-core pointer at `+0x128`; after request4 it points to the captured `0x126e8` core. Request4 post-state equals request5 pre-state byte-for-byte, and request5 post-state equals request6 pre-state byte-for-byte for both wrapper and core.

## Native replay result

`prove-lsc-front-atomic-tintless-replay.py` loads the exact SHA-pinned ARM64 `QcDeviceMFT8380.dll` under Unicorn and executes the real `TintlessAlgorithmWrapper::Process` at RVA `0xc95fd0` sequentially for request4 -> request5 -> request6 in one emulator instance.

The only Windows-runtime service needed by request4 initialization is the lazy `0x126e8` allocation reached through the DeviceMFT heap-allocation IAT slot. The proof redirects that IAT data slot to an emulator allocator shim; **no DeviceMFT instruction is patched**. The shim must receive exactly one allocation of `0x126e8` bytes and returns the exact captured Windows core address.

To avoid assuming fresh heap contents, the complete sequence is replayed twice: once with the new core filled with `0x00`, and once with hostile `0xA5`. Both runs produce the same exact Windows state.

For each request the replay requires:

- callback return `0`;
- complete `0x1090` wrapper post-state byte-equal to Windows;
- complete `0x126e8` core post-state byte-equal to Windows;
- all four output mesh arrays byte-equal to Windows;
- generated request4 state to equal request5 captured pre-state without reseeding;
- generated request5 state to equal request6 captured pre-state without reseeding.

Request5 and request6 retain the already-proven bounded core footprint: read high-water `0x12694`, write high-water `0x126e8`.

Exact full output-capture hashes are:

- request4: `afbe1edb7193b9ee8f653e4079f5d65f4a21211f6f38cf9ae099a7fba295f9fe`;
- request5: `1758e20ec2c91348a2688297557a13db152e3fd0151825575c3d0500145199b1`;
- request6: `3d3423b717c9dcf7a5e336355dde73e35b8f60862a0d29d2b23d6034fe7619c1`.

The descriptor-addressed payload is four `0x374` float arrays = `0xdd0` bytes. The raw `0xdf0` captures include an adjacent unreferenced `0x20` tail; that tail remains unchanged across every callback and is not treated as Tintless output ABI.

## Output -> staging -> wire

The captured post-LSC `0x18a0` staging objects are valid. Exact Surface Q10 conversion of the replayed Tintless output meshes matches the channel values that the captured staging packs into LSC0/LSC1 for requests4/5/6. The two green channels are equal, so their swap is byte-invisible.

Derived authoritative wire hashes are:

- req4 LSC0 `eb41b13a2049ecfe835266fefedd2d41c3e15564a8826ee06437f48a533234e5`, LSC1 `c140edeb7b40eaefa5f904116cc4ce25478494bc9508160742cdc18881bfc676`;
- req5 LSC0 `1033e0732a1f2edf2263351be7ad213a98864ba0b9feb0a1d2eb27fbcf31953c`, LSC1 `eab65d435c04a768bc53009c0cfdf05055168213b50c83385459679dfc790590`;
- req6 LSC0 `94dda0dd0c221da88a1087b13305c1cbe440cd314b3f0f6e324504494aab758e`, LSC1 `5322633904bc97e2d647cf27c9f4f21a92b532272d063a4175028b3a8ad90076`.

LSC2 remains legitimately all-zero.

The separately dumped raw `req4/5/6_lsc0.bin` and `lsc1.bin` files in this capsule are all `0x374` zero placeholders and are **rejected as wire authority**. The authoritative route is captured staging -> exact Titan680 packer. This defect is recorded in the manifest and oracle rather than silently accepted.

## What this closes

The old sequential TINTCTX proof remains valid for OV13858 rear/shared algorithm behavior, but it is no longer needed to claim front Tintless parity. This fresh atomic capsule is mechanically IMX681 front and closes:

`front request4 lazy Tintless initialization -> request5 persistent state -> request6 persistent state -> Tintless output mesh -> captured LSC staging -> nonzero LSC0/LSC1 wire target`.

## Remaining gate

This new atomic stream does **not** have the same request4 pre-Tintless mesh as the older verified-front request4 bridge. The new atomic inputs are:

- req4 input mesh SHA `71fdf640e68b5e63cbbf84464a54de3b66f8f2df51cd273c2a9468c868d51879`;
- req5 input mesh SHA `6499164c635e70f58a950c0024ea0f35ba9f9d5be1821790fc42b9735700af2a`;
- req6 input mesh SHA `6499164c635e70f58a950c0024ea0f35ba9f9d5be1821790fc42b9735700af2a`.

Therefore do not splice the older `839cae7d...` request4 target into this independent stream. Before Linux request6, reproduce these atomic pre-Tintless inputs from the **same stream's** upstream LSC tuning/calibration/geometry, or capture the exact upstream request/x22/x23 capsule that generated them. Then perform a separate runtime-authorization review.

Proof artifacts:

- `FRONT-ATOMIC-TINTLESS-STAGING-20260904.json`
- `prove-lsc-front-atomic-tintless-replay.py`
- `lsc-front-atomic-tintless-replay-oracle.json`
- `LSC-LIVE-CURRENT-DATAMANAGER-SOURCE.md`
- `lsc-live-current-datamanager-source-oracle.json`
