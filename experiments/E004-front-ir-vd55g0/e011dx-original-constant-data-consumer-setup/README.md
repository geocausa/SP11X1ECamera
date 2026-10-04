# E011DX: exact constant-data and retained consumer setup

The original active outer callee now passes the exact opaque constant-data read at 0x600420 and executes the nested consumer setup in its retained caller. This proof ends before the next runtime-dependent read, without substituting a formatted buffer or consumer return result.

| Derived authority | Qualified result |
| --- | --- |
| Source 0x600420 | One exact eight-byte read from 0x10F03A0 |
| Constant-data extent | Eight file-backed bytes in a nonwritable PE section, matching retained memory |
| Actual 0x7AC38 entry | Existing 640-byte stack destination, count 640, exact image pointer coordinates and inherited X6/X7 |
| Actual 0x7ACA0 entry | Retained destination/count and original variadic spill area |
| Actual 0x6BDD0 / 0x6BD48 entries | Exact nested argument transformations and stack frames |
| Original leaf 0xEDD0 | Returns address 0x17A1150 at 0x6BD70 with SP/X19..X29/D8..D15 preserved |
| Frontier | Stop BEFORE 0x6BD8C reads eight bytes from 0x17A1150 |

The exact eight-byte opaque window has SHA256 a2fb00d4cf5a726758f3b5d24abbf631cccc4da72abd78c7e7556755fce7d726. The earlier private 64-byte exploration is superseded as authority; only the exact observed eight-byte request is accepted. No original bytes, names, format contents or pointed string bytes are exported. Passing a pointer coordinate does not qualify dereferencing its contents.

Each case executes 75 original instructions and writes 33 stack chunks under an independently authored ordered contract. The stores preserve original saved frame links, arguments and variadic spill values; the incoming X6/X7 values are retained rather than invented as semantic input. Each store rejects changed source, address, width, value and readiness before advancing. The exact constant read and each nested call have corresponding altered-request checks. Five nested entries are validated, one leaf returns, and four consumer frames remain active.

All 256 inherited seven-axis cases pass: four stack/allocation biases, two loader indices, two initial thread epochs, two bound sentinels, two diagnostic X0 values, two OS void X0 values and two poison patterns. Added totals are 19,200 original visits, 8,448 exact stack stores, 52,224 rejected requests, 256 exact constant reads, 256 original leaf ABI returns and 1,280 exact nested entries. No new allocation or OS leaf is modeled.

Every complete inherited E011DW row equals its accepted row. Inherited original visits remain separate: DW 151,552, DV 237,568, DU 45,056, DT 127,744 and DS 333,312. Combined original coverage is 914,432 visits. One original-entry-to-frontier memory and mapping-permissions snapshot spans all stages without resetting expected memory, parent registers, allocations, guards or epochs.

All nine allocations, redzones, earlier constructed nodes/header/array, two-entry/32-slot exit table and original registry ownership remain retained. The published 18,832-byte buffer stays wholly zero with reference count one; the 640-byte destination remains wholly zero. All added stores lie below that destination. Both registry locks remain held; CRT/SRW locks are released. Actual enumeration/global/TLS epoch stays 80000042, helper guard 80000041 and factory guard FFFFFFFF.

Five exact function bodies at 0x7AC38 / 0x7ACA0 / 0x6BDD0 / 0x6BD48 / 0xEDD0 add 104 / 84 / 80 / 132 / 12 bytes respectively, extending 25 inherited source pins to 30. Every executed instruction matches its original bytes. Only 0xEDD0 has returned; consumer returns 0x600440 / 0x7AC7C / 0x7ACDC / 0x6BE0C and outer return 0x5F8EA8 remain pending.

NEXT E011DY derives authority for the writable eight-byte runtime scalar at 0x17A1150. Static PE metadata puts it in virtual zero-fill; this is not proof of its native loaded or subsequently initialized runtime value. Its read is not executed in E011DX.

Loader/runtime selection, native allocator success/failure, stack commitment, exceptions/concurrency/teardown and complete consumer/outer/helper/descriptor publication remain unqualified or inherited explicit models. Selected profile/input deterministic startup, populated RS identity/generation/lifetime, normal AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain required before clean-colour front/rear/off acceptance. Native rear runtime is denied.

Run python3 experiments/E004-front-ir-vd55g0/e011dx-original-constant-data-consumer-setup/verify.py --selfcheck to review evidence, pins and scope. source-private.py reruns bounded original emulation on SP11. Originals and optical material remain private there.

Zero camera Starts, reboots, kernel builds, production camera C or PM changes. Golden boot/payloads, full EFI/GRUB and historical repositories are unchanged.
