# E003i-EC — Windows R4..R12 LSC staging oracle

Status: **PASS_WINDOWS_ORACLE / POST-R6 LSC EVOLVING / GOLDEN RETURN PASS.**

EA proved the bounded Linux sensor + residual-ISP loop through request6. EB then proved that post-R6 GTM/TMC content is stable through request12 apart from deterministic bank parity. The next continuous producer question is LSC.

EC captures only the already-proven post-calculation IFELSC411 staging boundary. At DeviceMFT RVA `0xa03b34`, exact prior analysis establishes:

- request/frame = `qwo(x20+0x1ff8)`;
- final IFELSC411 staging = `x19+0xac`;
- staging size = exactly `0x18a0` bytes;
- exact Titan680 packer RVA `0xb3d8a0` converts that staging into authoritative LSC0/LSC1/LSC2;
- wire GIC follows from the proven LSC source alias.

The camera holder is gated before StartAsync. CDB attaches first, arms the single post-calculation breakpoint, and the stream starts only after the breakpoint list is verified. Requests R4..R12 each dump one 0x18a0 staging object. The breakpoint auto-detaches after R12.

Raw captures stay outside Git. `analyze-ec.py` uses the already-closed exact Surface packer model to derive LSC0/LSC1/LSC2 and GIC for each request, verifies the expected bank alternation and zero LSC2 branch, then classifies post-R6 wire content as stable, two-cycle or evolving.

No Linux camera runtime is performed by EC, and continuous AEC is not claimed by this checkpoint.

## Windows oracle result — 2026-09-11

The already-completed gated Windows capture was recovered read-only from the Windows NTFS partition after Golden return and preserved at:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ec/windows-r4-r12-20260911`

All nine request4..request12 IFELSC411 staging objects are exactly `0x18a0` bytes. The pinned Surface packer code verifies and maps them with bank sequence `1,0,1,0,1,0,1,0,1`; LSC2 remains the proven all-zero branch.

Unlike EB/GTM, post-R6 LSC does **not** stabilize: R6..R12 contain seven distinct staging hashes, seven distinct LSC0 hashes, seven distinct LSC1 hashes and seven distinct GIC-alias hashes. Therefore carrying R6 LSC forward would be incorrect for this steady preview regime.

The next gate is request7+ Tintless/upstream state capture/replay so the evolving LSC staging can be generated rather than frozen. Continuous AEC remains unproven.
