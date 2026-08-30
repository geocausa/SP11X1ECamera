# E003h CSID1 prepare → RUP/AUP → enable parity gate

Same-machine SP11 Windows KD now proves the front IMX681 CSID1 IPP order in one camera start:

1. qccamisp configures IPP while `CTRL=0`: `CFG0=0x802b2000`, `CFG1=0x7241`, pre-RUP IPP IRQ mask `0x3c1c7004`, TOP mask `0x1`, accepted crop state.
2. The kernel-owned RT-CDM buffer submits the already-known all-path CSID update: `CHANGE_BASE 0x57000`, `REG_RANDOM [0x18]=0x01f501f5`, `GEN_IRQ`.
3. qccamisp resource selector `5` enables IPP. Completion has `CTRL=1`, final IPP IRQ mask `0x3cbc601c`, TOP mask `0x1`.

The raw KD log remains on SP7 and is not committed. Its SHA-256 is `eeb60ca85e08d8d69cbd42a7fb8847663e4031f90482c9592e1c2cd2e686da30`; the committed derived oracle is `windows-csid1-config-rup-enable-order-oracle.json`.

Linux 0042 already submitted `0x01f501f5` inside prime1, so the missing operation was not another RUP write. Patch 0043 reorders the bounded front path to `prepare -> prime1 RUP/AUP -> startup2 -> startup3 -> enable -> CSIPHY2 -> sensor`, with rollback covering a prepared-but-not-enabled CSID. Runtime is not authorized by this static record.
