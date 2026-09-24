# E004om — conditional 0x802 manager list builder supplies generic 0x809 core dispatch

**2026-09-24. Parent Git `cae49ddf72b73f2cc6592436a90de04e0d9c6e8b`.** Exact same-SP11 original Qualcomm `qccamisp8380.sys` read-only, SHA pinned. Evidence tier **S** = static original code, NOT live Windows rear hardware proof. Linux slices: **L1** exclusive ISP ownership and **L2–L3** per-core mode/IRQ/DMA lifecycle. Target client/mode: rear OV13858 3840×2160 Windows VideoRecord, active instance and branch selection **not observed**.

## Original source connection

E004ol proves selector `0x809` takes generic manager branch RVA `0x1932C`, reads manager count `+0x24` and its index-six onward list, and forwards the original selector to enabled per-core callback records. E004om identifies an **actual writer of those very fields** earlier in the same source, inside dedicated **`0x802` configuration branch** (manager RVA `0x16714–0x16718`).

| Exact original ARM64 branch/instructions | Constrained static result | Still unverified |
| --- | --- | --- |
| RVA `0x16F3C–0x16F44` | This conditional 0x802 path only enters the checked descriptor-selection branch **when existing manager list count +0x24 is zero**. A nonzero count branches to another per-core configuration path RVA `0x18F9C`. | All record initialization or invalidation sites, actual real-world 0x802 call ordering. |
| RVA `0x16F6C–0x16FBC` | With relevant configuration-state gating, obtains a descriptor pointer from original global `+0xE3E8`, reads descriptor count/table and uses manager `+0x55C` in a hardware-availability search. | That the descriptor or its chosen indices correspond to Windows rear VideoRecord. |
| RVA `0x170D8–0x1711C` | If an original pair-selection flag is set, copies **two descriptor halfword indices** to manager indexed words starting at index six, incrementing manager count `+0x24` after **each** append. | That any particular pair (CDM/IFE/CSID) is selected; that every branch cannot exceed its record capacity. |
| RVA `0x17234–0x1724C` and `0x17410–0x17430` | Two alternative bounded-branch sites each append **one selected index** to the same manager list and increment the same count; the first is tied to a separate descriptor/availability scan and the second a separate selected-index search. | That the two sites always execute, or that these are all producers/reinitialization paths. |
| RVA `0x17464–0x17484`, `0x19350–0x19370` | Another 0x802 block iterates the populated manager list; the later generic 0x809 branch **reads that same count/entry address expression**. E004ol separately source-locks unchanged selector forwarding at `0x193B4`. | Actual live sequence, selected core ID, receiving callback semantics, IRQ/DMA stop. |

Because the original 0x802 branch may skip the checked builder when count is nonzero, **do not claim a complete manager-list lifecycle or that 0x802 always generates exactly one/two entries**. The generic 0x809 branch caps its normal nonnegative iteration count at two, but this **does not validate every writer's capacity nor establish that a signed core ID cannot be negative**.

## Verification and next test

`PYTHONDONTWRITEBYTECODE=1 python3 verify.py`: exact same-SP11 original binary SHA, **80 individual ARM64 instruction anchors** across the 0x802 branch, both descriptor paths, manager indexed list writes and 0x809 consumer; independent E004ol conservative schema; **17 fail-closed negative mutations**. Only derived scalar RVAs/fields and conservative booleans enter `RESULT.json`; no proprietary original executable/disassembly, camera image, DMA address or KD material enters Git or another host.

**Next falsifiable slice:** identify concrete installed per-core first callback bodies' **actual** 0x809 branches, arguments and return statuses, using E004og's source-verified CSID/IFE/CDM first callback entries; decide whether the generic list can reach any of them based on conditional core IDs, not by assuming it is the 0x805 stop list. Independently prove the real Windows rear VideoRecord's actual list/mode and later WM16 bus/IRQ/physical DMA retirement without retrying the blocked KD workflow.

**Safety:** nothing was installed, compiled into runtime or activated. Source-compiled experimental rear Linux ISP remains DENIED. Protected Golden, front native 27-frame PIX, rear RAW/software-4K fallback and IR privacy remain unchanged. `0x809` has not been promoted to a Linux command, physical stop or DMA-retirement acknowledgement.
