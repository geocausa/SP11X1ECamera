# E011DN: Windows registry boundary

The accepted result is a 116-byte metadata-only snapshot on this SP11, taken after the rear OEM NV12 3840x2160 reader became ready and before Start. The pinned OEM image matches the existing same-SP11 image hash. The metadata bound and descriptor pointer are populated, all seven runtime-tag cells are zero, and the live platform callback table matches the default file-image targets.

| Authority | Derived finding |
| --- | --- |
| Source references | Registry writer 0x5DE700 stores bound 0x17350E0 at 0x5DE9D8 |
| Windows ready snapshot | Metadata bound nonzero; descriptor pointer 0x1735118 nonnull |
| Windows ready snapshot | Seven tag cells at 0x17A30E0 all zero, including RS cell 0x17A30F4 |
| Windows / file comparison | Platform cell 0x1626898 selects callbacks 0x1DE30, 0x1DF30, 0x1DF90 |
| PE load configuration | 0xF7E7B8 is the CFG check pointer cell; cold target 0x1A8C0 is not a resource constructor |

The five exact source-body hashes are checked independently against the private image. Static references identify the writer; they do not qualify the full original initializer execution. Raw binary memory, debugger console output, decompilation and the original OEM image remain private on SP11.

## Attempts and limits

A and B use distinct persisted atomic entry identities and manual-only interactive tasks. Both ran in the same Windows boot. There was one Windows boot and two reboots, with Golden preserved as the normal return. The tasks were removed, the holders stopped/disposed, and no CDB or target service process remained at cleanup.

- E011DN-20261003-1926A: excluded from RS qualification. Initial idle service attachment failed because the service stopped. The observer attached successfully after initialization and resolved three pinned breakpoints, but its original MASM condition used unsupported logical AND syntax. Corrections resumed the same pending Start, and no query/RS record was captured. It completed with 69 valid 4K handle acquisitions.
- E011DN-20261003-1926B: fresh identity, same Windows boot, two resolved copy-site breakpoints and a clean before-Start registry snapshot. No copy-site hit occurred. It completed with 449 valid 4K handle acquisitions. This is snapshot evidence only, not an isolated-boot camera runtime qualification.

Handle acquisitions are not claimed as unique frames or image-quality evidence. No optical material was saved. Neither attempt establishes live original reader/query execution, RS presence/absence across other processes or profiles, populated record identity, generation, copy correctness, or lifetime.

The two copy sites were 0x7414B0 before the original 132-byte copy and 0x7414CC after it. Zero hits is a bounded observation, not a null-query proof. All initializers, selected request/profile authority, normal AFD input producers and independent IRQ/DMA/IOMMU retirement remain open.

## Validation and next step

Run `python3 experiments/E004-front-ir-vd55g0/e011dn-windows-registry-boundary/verify.py --selfcheck` for the derived evidence, source locks and scope checks. `source-private.py` reads the preserved evidence on SP11 and checks the private source hashes and Golden guard; it does not start a camera or execute OEM native code.

Golden return checks passed: all three payload hashes, permanent EFI state, saved GRUB state and both historical repositories match the pre-boot snapshot. The read-only Windows partition was unmounted after local recovery. No kernel build, production C change, kernel debugger halt or Linux power-policy change occurred.

Next E011DO qualifies the original registry initializer with explicit allocation/descriptor ownership and default callback contracts, then resolves the selected normal reader request/profile path. Use a fresh boot and fresh identity for another oracle. E011DM remains the latest original empty-slot query proof and E011DI the separate factory/enumeration proof. Native rear runtime remains denied.
