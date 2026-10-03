# E011DH: original factory initialization and1040-byte clear

Thirty-two cases cover four stack/node placements, loader indices0/37, two negative cold epochs and either unchanged file/BSS fields or explicit D7 canaries. Each executes418 original instructions /369 exact store chunks /61 rejected requests; totals13,376 /11,808 /1,952.

Original factory source clears190 image field chunks (including scalar, floating halfword and SIMD writes) while retaining both source-built48-byte records and typed allocation owners. The expected scalar-zero field plan is derived from the private discovery footprint, pinned separately and checked per source site/address/width. Sixteen canary cases prove active zeroing of those fields rather than accepting their initial zero contents.

Original5BE9F8 calls F5E600 with destination incomingSP-1144, fill0, count1040 and actual return5BE9FC. Its original428-byte metadata range is pinned and decoded per aligned instruction, so embedded table data does not truncate the valid code map. Each execution runs117 original instructions and130 exact8-byte store chunks. Independent expected zero1040 bytes, bounded destination writes, actual source reads and caller SP/X19–X29/D8–D15 plus X0=destination return all pass; no clear-result fixture is used.

Whole mapped memory and actual permissions match the independent pre-instruction stack/per-site field model. Logical SRW/allocation readiness, owner/order and both records remain checked. Wrong helper caller/entry/destination/fill/count, invalid loader/resource/allocator requests and corrupt final fields/clear data reject before effects.

The accepted stop is BEFORE original call5BE9FC ->5F8DC0. No file enumeration, factory completion or full parent ABI return is established. Native loader/OS/allocator bodies, concurrency, allocation failure/cleanup, full Default/startup/preflight/RS and hardware retirement remain open. Cold file/BSS, owned loader/TLS/negative epochs/stack/typed allocation models and canary robustness cases remain explicit.

Accepted v4 is byte-identical to private exit0/no-stderr job. Earlier v3 exposed verifier scalar-halfword/vector store handling and is excluded. Original code/filenames/path bytes remain on SP11. Golden and historical clones unchanged; zero Starts/reboots/images/production C/kernel changes.

NEXT E011DI follows actual5F8DC0 caller and standard file-enumeration contracts under those preserved models.

Artifacts: [RESULT](RESULT.json), [source](source-private.py), [cases](ORIGINAL-FACTORY-INITIALIZATION-CLEAR-V4-SAFE.json), [authority](INITIALIZATION-CLEAR-AUTHORITY-SAFE.json), [zero field plan](FACTORY-INITIALIZATION-ZERO-FIELDS-SAFE.json), [Golden guard](GUARD-SAFE.json), [next plan](NEXT-SOURCE.json).
