# E011BK — original profile callback and complete reader

The original reader now returns through its real indirect callback and decimal formatter in bounded offline fixtures. The interface constructor and callback layout are qualified. The profile-node contents and file context remain owned fixtures; actual tuning-file profile selection and the loader's concrete interface instance are still open.

## Accepted evidence

| Original routine | Complete top-level returns |
| --- | ---: |
| Interface constructor 0x6F3D08 | 4 |
| Callback 0x6F3B50 | 72 |
| Recursive profile formatter 0x6F2208, independently invoked | 44 |
| Complete reader 0x6F47B8, including dispatch at 0x6F4A98 | 72 |

Four placements include unaligned locations. Eight malformed owned descriptions are rejected before execution. The complete-reader cases include 24 invocations using typed AEC records from three SHA-pinned files and 48 using owned numeric record variants. Each uses an owned interface/context and either a single-node or ancestor profile graph.

The original interface constructor installs table 0x133B740; its first slot is callback 0x6F3B50. Four original interface-table slots have that same callback. This qualifies the base interface fixture and common callback, without selecting the actual loader subclass or live interface instance.

The callback reads the node table pointer at interface+1072 and U32 count at+1080. Its index comes from reader wire+44, also retained at reader+68. Node stride is160 bytes. A valid selected node supplies its eight bytes at+4 to reader+60. Null table, negative signed index and out-of-range index zero only that eight-byte output and preserve the profile buffer.

For a valid node the callback clears one byte of the profile buffer. The formatter follows parent pointers at node+24 first. A zero U32 at node+8 includes the decimal pair from U16 fields at+4/+6; a nonzero value omits that node's pair. Included ancestor/current pairs are joined with a vertical bar. The original bounded formatter 0xCB6300 executes without a formatting shim, and sets destination byte127 to zero when it formats text. Accepted owned graphs are acyclic, at most12 nodes, with generated text at most100 bytes. Overflow/truncation policy beyond this scope is open.

Complete reader runs retain ID/name, exact32-byte original copy, wire36:44 -> reader52:60, wire44:48 -> reader68:72, wire52:56 -> reader200:204, file-relative payload pointer and56-byte cursor advancement from E011BJ. They additionally verify the exact eight-byte callback result and complete128-byte profile buffer after the original indirect dispatch and full return. The caller-supplied alignment1 and zero-filled file context remain explicit fixture scope.

Every heap byte is compared against the exact permitted writes. File-map bytes and canaries, interface records, parent pointers and source contexts are preserved. No allocation occurs. Only the inherited security-cookie shims at0x11D0/0x11F0 execute; no callback, decimal formatter, string helper, allocator or new helper shim is introduced.

## Reproduce

On this SP11:

```sh
python3 experiments/E004-front-ir-vd55g0/e011bk-rear-aec-profile-callback/source-private.py
```

Original DLL/tuning bytes, decompiled C and raw logs remain private on SP11. Tracked evidence contains owned fixture code, semantic facts, RVAs, counts and hashes only. Captured live metadata/profile values are never inputs to these tests.

## Next

Qualify how loader0x6F22C8 produces the160-byte profile records and parent links, including its node-table/count stores at0x6F3188/0x6F318C and later table-pointer update at0x6F34A4. Follow the interface argument passed into table builder0x6F4CA8 at0x6F3520, then into reader0x6F47B8 at0x6F4E84. Prove the concrete source/interface selection and filename authority before integrating original metadata helpers into the full AEC parent, accounting for their extra name allocation.

Actual source profile selection, exact opened filename, whole loader alignment, full-parent metadata integration and remaining root/grid fields stay open. Cold metadata, RS authority, deterministic bootstrap, WM16 retirement and optical parity are also open. No camera start, reboot, observer arm, production C change or kernel build occurred. Golden and all three protected payloads are unchanged; native rear runtime remains denied.
