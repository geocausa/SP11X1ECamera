# E011DR: original cleanup registration and guard publication

The unchanged cold caller now executes cleanup registration and first-helper guard publication. Original source registers callback 0xF7B120 and updates the encoded exit table, then publishes one epoch to the global counter, helper guard and TLS thread cell. No registration or guard result fixture is used.

| Authority | Qualified result |
| --- | --- |
| Registration wrapper 0xCA34A0 | Actual return 0x5B90A0 |
| Registration 0xCA3450 | Actual return 0xCA34B0, callback 0xF7B120 |
| Exit table 0x16A2760 | Three encoded words; one used pointer, 32-slot capacity |
| Fresh exit storage | Owned allocator leaf 0xCC2A50, arguments NULL / 256 bytes |
| Guard publication 0xCE7A48 | Actual return 0x5B90AC; global/guard/thread epoch agree |
| Boundary | Stop BEFORE 0x5B8104; next pointer read 0x1731880 at 0x5B8108 |

512 cases vary four stack/allocation placements, two loader indices, two signed-negative thread epochs, two bound sentinels, two diagnostic X0 values, two OS void X0 values, two allocation poison patterns and two initial global epochs. All 321,536 original visits pass. CRT registration contributes 173,056 visits and publication 17,920; these are subsets of the total. Original constructor coverage remains 52,736 visits.

All 43,520 stack-store chunks and 62,464 nonstack chunks match independently declared effects. The whole mapped memory and permissions snapshot allows only those effects. Source and unmodified loader regions remain immutable; the exact TLS thread epoch update is permitted and checked. Allocation redzones, constructed container relations and 5,632 added original-callee ABI returns pass. All 62,976 invalid owned dependency requests reject before effects.

The allocator adapter supplies fresh poisoned storage only. Original recalloc/memset code zeros the 256 bytes; original table code initializes encoded-null slots, writes the encoded callback and publishes begin/used/capacity. Encoding is independently checked as rotate-left(pointer, cookie modulo 64) XOR cookie. An empty encoded-null word equals the cookie, not zero. The original NULL-free branch executes; non-null free, failure paths and existing-table growth remain unqualified. The memset body authority is 308 bytes across four exact disjoint ranges.

Explicit owned models supply loader/TLS/OS resource readiness, the separate CRT lock and a ready empty encoded exit table. Native CRT initialization is not qualified: zero-filled file-image table words do not constitute that ready table. Native allocation, callback execution, teardown and concurrency remain open. Original source increments the global epoch and stores the same published value in the helper guard and TLS cell. The CRT and SRW locks are released and one owned wake occurs; the parent registry lock stays held.

Parent and first helper have not returned. Full descriptor registry initialization/publication, selected input/profile, populated RS identity/generation/lifetime, normal AFD authority and deterministic startup remain open. E011DI retains separate factory/enumeration acceptance and E011DM retains the empty RS-query proof. The next helper dependency is its factory pointer; derived references identify a write at 0x5B8138, but that write is outside this acceptance.

Run python3 experiments/E004-front-ir-vd55g0/e011dr-original-cleanup-registration-publication/verify.py --selfcheck to review matrix, source locks, counts and scope. source-private.py reruns bounded Unicorn emulation only on SP11. Original binaries/instruction text/decompilation/raw records and optical material stay private on SP11.

Zero camera Starts, reboots, kernel builds, production camera C changes or power-policy changes occurred. Golden boot/payloads, permanent EFI/GRUB and historical repositories remain unchanged. E011DS follows actual factory construction in this parent caller. Selected deterministic startup and independent exact-buffer/generation IRQ/DMA/IOMMU retirement precede the clean-colour front/rear/off app gate. Native rear runtime remains denied.
