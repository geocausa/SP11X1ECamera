# E011DY: original cold runtime context and nested receiver setup

Original source now passes the runtime dependency at 0x6BD8C under declared loader initial-value models, constructs the runtime stack context and then initializes the next consumer's receiver fields. No preconstructed context, receiver, formatted output or return result fixture substitutes for source execution.

| Derived authority | Qualified scope |
| --- | --- |
| 0x17A1150 / 8 bytes | Writable virtual zero-fill scalar; owned cold value zero |
| 0x16A2A84 / 4 bytes | Writable virtual zero-fill flag; owned cold value zero |
| 0x16072D8 / 16 bytes | Writable file-initial pointer pair; targets 0x1607180 / 0x1607650 |
| Original 0xCAD868 | Exact 352-byte body; runtime context setup in retained stack |
| Original 0xCA6280 | Exact 384-byte body; nested receiver field setup |
| Original 0x11D0 | Cookie-frame convention; deliberate SP decrement 16, actual return 0xCA6298 |
| Frontier | Stop BEFORE 0xCA6348 -> 0xCA94E8, actual return 0xCA634C |

Both zero-fill scalars lie beyond their sections' file-backed data, inside writable virtual extents. They have no file-byte hash authority. The accepted values are explicit loader/model assumptions, not measured native runtime values. Changed scalar values and changed pointer cells reject the entry contract; alternate branches and native initialization remain unqualified.

The file-initial pair has SHA256 507987659945beb7bcd11ae53dece55517a2979fc4e3ea4c9683bdceb5fd0f3f. Both cells match their exact initial file bytes and retained memory. Their section is writable, so this does not prove native pointer immutability or runtime selection. Their pointed table contents are not dereferenced or qualified here.

All 256 inherited seven-axis cases pass. Per case, original execution adds 82 visits, 44 exact setup chunks, four exact runtime reads, two exact nested entries and 268 rejected requests. Totals are 20,992 visits, 11,264 stores, 1,024 reads, 512 entries and 68,608 rejects. No new allocation or OS leaf is modeled.

Each of the 44 store chunks has an independently authored source/address/width/value/order contract, including saved incoming nonvolatile registers, typed context flags and pointer fields, the original cookie slot, destination/count pointers and nested receiver fields. Changed source, address, width, value and readiness reject before advancement. Each runtime read and nested call has exact contracts; entry checks reject changed live initial-value cells.

The small inherited 0x11D0 body is cookie-frame setup. It returns at 0xCA6298 after deliberately lowering SP by 16, preserving all other nonvolatile registers and constructing its exact saved slot. It must not be called an SP-preserving leaf or an OS stack-commitment proof. All 256 cookie-frame convention checks pass; committed stack bounds remain inherited owned models.

The runtime context pointer passed onward is outer-entry SP minus 1888. Its typed flag/pointer initialization is qualified, including the two initial image pointers and the flag transition zero to one. The next receiver begins at outer-entry SP minus 3104; associated destination/count fields begin at minus 3136. Only the exact initialized fields and cumulative unchanged bytes are qualified; complete structure semantics and later lifetimes remain open.

Every complete E011DX row equals its accepted JSON evidence. Inherited visits remain separate: DX 19,200, DW 151,552, DV 237,568, DU 45,056, DT 127,744 and DS 333,312. Combined original coverage is 935,424 visits. One original-entry-to-frontier memory and mapping-permissions snapshot spans all stages, without resetting expected memory, parent registers, allocations, callback table, guards or epochs.

The original 640-byte output destination and published 18,832-byte buffer remain entirely zero; reference count stays one. All nine live allocations, redzones, constructed object/header/array, previous nodes/clears and two-entry/32-slot exit table remain retained. Both registry locks stay held and CRT/SRW locks released. Enumeration/global/TLS epoch stays 80000042; helper guard is 80000041 and factory guard FFFFFFFF.

The two new exact bodies extend the 30 inherited source pins to 32. Every executed original instruction matches its original bytes. Six consumer frames remain active: 0x7AC38, 0x7ACA0, 0x6BDD0, 0x6BD48, 0xCAD868 and 0xCA6280. Their returns 0x600440 / 0x7AC7C / 0x7ACDC / 0x6BE0C / 0x6BD94 / 0xCAD940 and outer return 0x5F8EA8 remain pending.

NEXT E011DZ integrates original 0xCA94E8 into this retained caller. Its exact 1028-byte body at [0xCA94E8,0xCA98EB], SHA256 8e1aa3dcf0d019df157030034475dc1fe87defc61d765e4f5deecac6b56b150a, is metadata only; its instructions are not included in accepted execution pins or executed here.

Native runtime values, nonzero scalar/flag alternatives, changed pointer pairs, pointed locale/format/string data, complete formatted output, consumer/outer/helper/descriptor publication, failure/concurrency/teardown and OS stack growth remain open. Selected profile/input deterministic startup, populated RS identity/generation/lifetime, normal AFD authority and independent IRQ/exact-buffer/generation/DMA/IOMMU retirement remain required before guarded clean-colour front/rear/off acceptance. Native rear runtime remains denied.

Run python3 experiments/E004-front-ir-vd55g0/e011dy-original-cold-runtime-context-receiver/verify.py --selfcheck for evidence and scope review. source-private.py reruns bounded original emulation on SP11. Original source bytes/text, proprietary names and optical material stay private SP11.

Zero camera Starts, reboots, kernel builds, production camera C or PM changes. Golden boot/payloads, full EFI/GRUB and historical repositories are unchanged.
