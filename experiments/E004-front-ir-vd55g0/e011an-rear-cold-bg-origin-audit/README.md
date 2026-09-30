# E011AN — cold BG origin boundary audit

Parent: a3c81299111f8c1f46c9a0f2a0531293cd7a2ea9.
Status: ORIGINAL OWNERSHIP PASS; FULL OFFLINE PARITY UNCHANGED; VALUE POLICY OPEN.

E011AM produces zero semantic register differences from independent caller input records. This audit narrows the remaining cold-weight/quad origin question without replacing those inputs with guessed defaults.

The original CAWBIOUtil descriptor helper RVA 0x845368 exposes a 92-byte BG output at IO+0xCB4 as expected-output index 5/type 5. Its GetParam descriptor helper RVA 0x845658, with selector 12, exposes the same destination as output index 10/type 10. Selector2 does not expose that BG output. Both helpers preserve every byte of the BG payload: they provide writable destinations and do not generate a quad value.

AWB initialization RVA 0x831510 invokes algorithm GetParam slot+8 at call RVA 0x831964, returning at 0x831968, after preparing selector 12 at 0x831938. This is a concrete upstream writable boundary to observe; it is NOT yet a physically trapped first writer to IO+0xD08. E011Q already brackets successful initialization from an uninitialized BG source to the normal seed, but that broader bracket cannot select the precise write inside it.

Original FillBGConfigurationData RVA 0x846020 carries the full 32-bit IO+0xD08 field into output record+0x4C. This function preserves its incoming value, including synthetic nonboolean inputs; boolean validation remains the clean caller contract. E011AL separately proves hardware packing uses bit0. The initialization prepublish path uses the same IO field for Usecase AWBStatsControl; E011R already closes the distinct normal request publication path.

Static ReadDefaultStatsConfig RVA 0x73B730 copies a 0x818-byte AEC statistics payload to the retained pointer at node+0x72A58 and a 0x80-byte AWB payload to node+0x72A68 before HardcodeSettings. The E011B cold geometry stores leave the extra weight/quad fields outside their proved geometry slice. Their numeric origin must be traced upstream of these consumer copies; this audit does not independently prove the earlier algorithm/tuning value policy.

E011AK cold and normal AEC weights are the same binary32 values near 0.299/0.587/0.114; sampled AWB quad is1 in both. The nearby HardcodeSettings weight triple near 0.3125/0.5635/0.125 is at a different record offset and does not establish the normal AEC_BE cold policy. No such constants were added to the clean implementation.

Validation:
- 48 original descriptor calls cover four owned IO base offsets, four payload sentinels and three descriptor paths.
- 136 original FillBG calls cover four owned bases and zero, all-ones and every walking bit.
- 184 original calls return normally; executable bytes are unchanged and no OS driver is invoked.
- Full E011AM provider replay repeated with GCC/Clang ASan/UBSan:509,829 assertions each; differences by phase0/0/0/0. Existing safe reports remain byte-identical.

Run on SP11: python3 experiments/E004-front-ir-vd55g0/e011an-rear-cold-bg-origin-audit/verify-private.py
Originals, decompiler text, private records, diagnostic logs and runtime pointers remain on SP11. This audit changes no production C, creates no kernel build and performs no camera, boot, suspend, MMIO or submission operation.

Next: bounded user-mode observation around AWB selector 12 before/after0x831964; identify the actual algorithm owner privately and establish the first write/policy inputs. Trace the AEC Usecase statistics producer independently. Keep normal RS/AFD count policy, whole-frame offset authority, explicit inactive cold gamma and generation-safe WM16 IRQ/DMA/IOMMU retirement open. Native rear runtime remains denied.
