# E003h 0063 — CSID Epoch lifecycle bridge result

0063 executed exactly once, returned `RUN_RC=0`, archived a `0x76b000` / 7,778,304-byte QC10C slot0, advanced RT-CDM from the previous FIFO-25 boundary to FIFO 30 without fault, and returned immediately to FullIO Golden. No same-boot retry occurred. Golden `saved_entry=sp11-audio-fullio-v19c`, empty `next_entry`, and absent camera modules are verified.

The causal result is positive: replacing the obsolete raw VFE BUS Epoch0 poll with the already-latched CSID1 IPP Epoch0 bit21 unlocks the existing BUS slot1 retarget -> replay2 -> VIDEO lifecycle. This closes the prior missing-Epoch boundary and confirms the Windows CSID-IST interpretation.

The produced QC10C surface is not yet a complete image. Its size and four-region offsets exactly match the pinned Windows QC10C/TP10-UBWC contract. Offline integrity analysis shows only the first 70 4K pages of Y data and 35 4K pages of C data are populated: `286720 = 3584 * 80` bytes of Y and `143360 = 3584 * 40` bytes of C, exactly 1/18 of the 1440-line output height.

The new boundary is therefore premature VIDEO completion. Linux still polls VFE TOP status1 bit0 for VIDEO, but 0062r1 already observed TOP status1 `0x00030003` before Epoch progression, so bit0 is stale/pre-set by the time 0063 reaches that wait. The poll returns immediately, VIDEO slot0 is retired, and the sensor is stopped after roughly the first 80 output lines.

Do not repeat 0063 and do not substitute another raw VFE bit. Next gate: trace same-machine Windows' active type-1 dispatcher `event 3 / IFE VIDEO buf done`, especially message field2 bit0 and the producer that fills that message. Windows remains authoritative.
