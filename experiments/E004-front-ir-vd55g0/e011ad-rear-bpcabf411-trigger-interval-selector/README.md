# E011AD — rear BPC exposure interval selector and startup scalar bridge

Status: **OFFLINE INTERVAL + LIVE SCALAR-TO-SOURCE REGION/COMMON/STARTUP-PACKET BRIDGE PASS.** Upstream exposure scalar production, complete E008o composition and the independent WM16 hardware retirement gate remain OPEN.

Parents: E011AC bb8bcb9492752bc400526f41c491f0f4b4135754; prepared selector/observer 07d9e26820d3a2555643679373e6a8941df7b2ce; inconclusive RunA recovery 91e14f8cabccfff91cb844f5c8f8a55e51089c1f.

## Independent source selector

selector.py decodes the installed SHA-pinned rear authority through E011AC's symbol decoder. All four installed BPC roots have one outer trigger, one next-level trigger and six terminal trigger records. It follows serialized child references and validates counts, types, empty terminal child blocks, region ownership and ordering. It does not guess leaves by comparing live outputs. Each serialized terminal record contains the start/end pair and child/region references; the native search reads those interval fields at +8/+0xC in the expanded 48-byte runtime entry.

The supported interval domain is deliberately one through six finite, ordered, nonoverlapping sibling intervals. Invalid shape, empty/oversized lists, reversed/overlapping ranges and nonfinite input fail closed. Linked/aliased mode paths retain E011AC's rejection; source interval inventories for all four roots do not add broader mode-resolution support.

The rule is a plateau/strict-gap selector: hold a leaf through its end; blend only after that end and before the next start; hold the first/last leaf outside the covered range. At a shared boundary the preceding plateau wins. The original helpers promote binary32 input/endpoints to binary64, subtract and divide there, then round the ratio once to binary32. The 107-field blend reuses the independently verified E011AC binary64 arithmetic and E011AA common/packer producer.

verify-private.py runs original callbacks RVA0x8F67E0 (outer) and0x8F6A90 (nested/terminal) only in local Unicorn memory. PAC instruction accommodations are limited to emulation; normal native stack checks remain active. All593 input cases match exact lower/upper indices and binary32 ratio in each of three modes: **1779 comparisons**, comprising209 blend and384 plateau inputs. Cases include every installed endpoint with adjacent binary32 values, gap probes, deterministic synthetic lists, touching/zero-width plateaus and narrow gaps. Six domain rejects pass. The two supported source mode paths produce1284 region fields through the scalar API. Numeric tuning values remain private.

## Fresh Windows binding

RunB E011AD-20260929-2245B completed original rear Color/VideoRecord/NV12 3840x2160 Start/Stop with **714 valid handles**. The holder used atomic CreateNew at entry, a manual-only task and bounded automatic Stop.

After initialization/CreateFrameReader reached the held READY gate, actual module ownership was discovered. Exactly one svchost/FrameServer process owned QcDeviceMFT8380. CDB attached to that process; all six breakpoints were concrete, enabled and resolved before START.GO. The observer had no syntax errors or bound rejections.

The26 private files comprise three root/region/reserve triplets, two mode-selector arrays, three outer vectors, nine nested numeric vectors and three completed common outputs. Each outer vector is72bytes; each actual nested vector is8bytes. The three trigger type IDs are **[2,5,1]** at cold/request1/request2. These are ordinary selectors, not the special type100 branch. The first two source layers each have one choice; the terminal type1 scalar chooses among the six source exposure intervals.

Source mode resolution agrees with live root IDs0x1a/0x100/0x100: Default, then Sensor1 Video. Nine original native decisions replayed on the actual typed scalar inputs agree with the independent selector. The producer takes only source tuning, semantic mode selectors and the scalar; it does not take live regions, common outputs or packet/register words.

Same-SP11 private validation passes:

- all three complete source-produced regions: **321/321 fields**;
- completed common output: **90/90 selected scalars**;
- serialized/runtime reserve anchors: **15/15**;
- retained E006a startup packet phases0/1/2: **21/21 register words**;
- two distinct startup seven-word states.

The common/interpolation/packer tags are0,1,2, and the bounded request hooks are1..8. Preserve E011AB's independently observed request3 hold; this three-hit observer is not a new proof of the hold schedule.

Actual runtime leaf ordinals were not directly observed. Several source leaves are identical, so byte equality alone cannot establish a unique runtime ordinal. This checkpoint instead source-reconstructs selection from the directly captured input scalar and proves the resulting full region/common/packet bridge. It does not create a general runtime tree/alias decoder or a new hardware witness.

## Inconclusive RunA and recovery

RunA E011AD-20260929-2215A completed711 valid4K handles with clean Start/Stop, but the attached idle service process never loaded DeviceMFT and wrote zero capture files. Semantic result INCONCLUSIVE. The run did not verify actual module ownership; do not assert an unproven reason for the missing driver. Its task was removed, and normal reboot returned to Golden boot15e9fcc5-eef0-48f6-b374-6f05e62af5af before fresh RunB. There was no same-boot camera retry.

After RunB Stop, its task was removed and normal Windows reboot cleaned up the debugger. SP11 is back on FullIO v19c Golden, boota6a56cbc-7618-43e0-b77c-297ece7ff69d, camera idle with no modules/nodes/processes. Windows NTFS was mounted read-only for private same-SP11 validation and unmounted. No successful normal debugger detach is claimed. No Linux camera/module/MMIO/DMI/RT-CDM invocation, IR activation, suspend or protected Golden replacement occurred.

## Remaining boundary and reproduction

The scalar API is explicit: upstream exposure value is caller-owned. Captured scalars are verification inputs only. Do not freeze a captured request2 value into Linux policy or promote output-equivalent leaf candidates as exposure policy. Next source-pin the shared request trigger1 scalar producer/provenance and compose the remaining independent E008o base objects. The E011X AEC/AWB producer boundary and module schedules remain authoritative. The complete first-frame composer and VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle gate are separate; native rear Linux hardware ISP remains denied.

On SP11, run python3 verify-private.py for the offline interval differential and python3 verify-live-private.py for the private RunB input-to-region/common/E006a comparison. Required original tuning/DeviceMFT, RunB26 captures and E006A-PRIVATE-RECORDS-v2.json remain private on SP11. VALIDATION-SAFE.json, LIVE-VALIDATION-SAFE.json, RESULT.json and RUN-A-SAFE.json contain derived facts only.
