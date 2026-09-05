# E003i-Z — paired live TL_BG + 3A bounded runtime

Status: **PASS; Golden return verified**.

Z validated the public Stage-Y generation-tagged 3A transport using exactly one Golden-safe bounded boot and one helper invocation. The accepted U six-frame front path, R4-before-STREAMON timing, same-fd live R5/R6 submission, IMX681/front-only DT, hardened boot flags, no same-boot retry and mandatory Golden return were preserved.

For every completed DQBUF, the helper read both read-only controls on the same fd and required exact `(generation, source_seq, slot)` identity. All six frames passed with generations/source sequences `1..6` and slots `0,1,0,1,0,1`. TL_BG was exactly `0xF020` bytes and 3A exactly `0x51040` bytes on every read.

Offline analysis of the exact 64-byte 3A ABI proves each frame contains the expected active payloads: AEC_BE `0x14000`, BHist `0x1000`, and AWB_BG `0x3c000`. Every payload is nonzero and all three component hashes are generation-unique across all six captures, so the data is live rather than stale or padded-only. TL_BG raw hashes are also generation-unique.

The candidate completed six QC10C frames in indices `[0,1,2,3,0,1]` / sequences `[0..5]`, returned `STREAMOFF_OK`, and the critical kernel-fault scan found no SMMU/IOMMU fault, Oops, soft lockup or vblank/TLB-sync timeout. SP11 then returned to persistent FullIO Golden with `next_entry` empty and camera modules absent.

This closes Linux statistics transport. Source generation remains explicitly distinct from request ID. No Lux/CCT algorithm and no dynamic R5/R6 LSC substitution ran in Z.

**Next:** reconstruct the semantic AEC/AWB path that turns the now-live Linux AEC/BHist/AWB buffers into the request-local `AECLuxIndex` and CCT required by the repaired front IMX681 LSC tree. Use the Windows oracle when it closes parser/algorithm boundaries faster than static inference; return to Golden after any oracle boot. Dynamic LSC substitution remains blocked until Lux/CCT and request association are proven.

Primary artifacts: `RESULT.json`, `RUN.txt`, `PAIRED-STATS-ANALYSIS.json`, `analyze-paired-stats.py`, `RUNTIME-BINARY-HASHES.txt`, `DMESG.txt`, and `GOLDEN-RETURN.txt`.
