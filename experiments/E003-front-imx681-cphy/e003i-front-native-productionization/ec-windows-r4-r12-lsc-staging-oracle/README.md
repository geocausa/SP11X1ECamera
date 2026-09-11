# E003i-EC — Windows R4..R12 LSC staging oracle

Status: **STAGED / WINDOWS ORACLE NOT YET EXECUTED.**

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
