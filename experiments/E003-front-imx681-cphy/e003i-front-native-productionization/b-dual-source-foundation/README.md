# E003i-B — dual-camera source foundation

Status: **accepted static build foundation; no runtime authorization**.

This checkpoint reconstructs a buildable source foundation from the protected source lineage:

1. true Golden v33 source;
2. accepted E002k rear R3 five-patch source replay, fuzz=0 and exact accepted hashes;
3. exact successful 0074 CAMSS 14-file source oracle (still intentionally contains disposable E003h control plumbing at this stage);
4. squashed dual-camera Denali source patch with rear OV13858 kept enabled and front IMX681 added;
5. exact accepted 0054 IMX681 mode2 source wired into normal media/i2c Kconfig + Makefile.

The rebuilt CAMSS and IMX681 modules have the same srcversions as the successful runtime. A full Denali DTB compiles and flattens with both camera endpoints, CAMSS port@1 + port@2, RT-CDM1, VFE 0xf000 spans, CSIPHY2 0x2000 and the five-entry X1E CAMSS IOMMU fwspec.

The five-entry IOMMU set is stronger front parity evidence than the older rear R3 eight-entry set: same-machine Windows and the current X1E Linux implementation both support it, including RT-CDM1 SID 0x18a0. It is therefore the front production candidate, but **rear regression is mandatory** before it can replace the accepted rear R3 domain contract.

Next: remove the disposable E003h control plane from CAMSS while preserving the proven VB2 ownership/requeue, runner and monotonic IQ FIFO. Fixed R4/R5/R6 firmware playback is not a production producer.
