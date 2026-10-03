# E011DF: original factory cold prefix and actual startup guard caller

Sixteen cases cover four owned stack placements, loader indices 0/37 and negative epochs 0x80000000/0xffffff00. They execute 1,344 unchanged original instructions and 352 exact store chunks; 640 invalid requests reject before effects. Each case executes 84 instructions, including 26 in original CE7AD8, and stops before allocator call5BE698 -> CAE740 with X0=48. The stop instruction is not counted as executed.

Original factory5BDE08 calls the guard at5BE67C with actual guard1B302D0 and returns to5BE680. The original header changes the cold guard from0 toFFFFFFFF. Its actual caller SP/X19–X29/D8–D15 restore, with balanced logical Acquire/Release on the same SRW owner. The factory then clears DWORD18A296C and QWORD1B302A0/1B302A8. Independent whole mapped memory, actual permissions, planned field values, pre-instruction stack stores and exact source reads pass.

Invalid entry/argument, held/unready resources, actual loader/TEB/slot/TLS/epoch/IAT corruption, wrong guard caller and wrong allocation-boundary requests reject before effects. Store values are normalized to their actual width because Unicorn may expose a signed 64-bit callback value; v3 failed this verifier representation check and is excluded. Accepted v4 checks the allocator target from the pinned original call instruction.

File-image/BSS cold state, owned loader/TLS layout, negative epochs, stack placements and logical native OS dependencies remain explicit fixtures. No native OS lock bytes, concurrent wait, allocator body, factory parent ABI return, completion guard, full factory/Default or hardware readiness is established. Original files and private names remain only on SP11.

Accepted source is byte-identical to private v4; job exited0 with zero stderr. Golden, boot defaults and historical checkouts remain unchanged. Zero Starts, reboots, Linux image tests or production C/kernel changes.

NEXT E011DG qualifies the exact 48-byte allocation boundary and original factory construction, then file enumeration/context/Default, full startup/preflight/RS and independent physical retirement/optical parity.

Artifacts: [RESULT.json](RESULT.json), [source-private.py](source-private.py), [source cases](ORIGINAL-FACTORY-GUARD-PREFIX-V4-SAFE.json), [authority](FACTORY-GUARD-AUTHORITY-SAFE.json), [Golden guard](GUARD-SAFE.json), [next source plan](NEXT-SOURCE.json).
