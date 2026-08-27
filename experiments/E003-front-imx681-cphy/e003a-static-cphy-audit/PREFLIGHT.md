# E003a — static C-PHY / IMX681 integration audit

## Hypothesis

The exact Golden source already contains much of the X1E/modern CSID hardware support needed for C-PHY, but its endpoint parser remains D-PHY-only. A current upstream/reviewed Qualcomm CAMSS C-PHY series can likely provide the generic plumbing; the audit must determine whether its PHY init sequence is correct for X1E80100 or whether X1E-specific evidence is still required.

## Hard runtime boundary

**Compile/static only.** Do not:

- enable LDO3_M or LDO7_B;
- toggle GPIO237;
- enable MCLK4;
- issue any CCI1 transaction;
- instantiate a live front sensor endpoint;
- stream CSIPHY2.

SP11 remains booted in `sp11-audio-fullio-v19c`.

## Exact source anchor

`/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-repro/src`

Do not use `.golden-v33-delta-replay/src` as a production source base.

## Static acceptance

1. archive the exact public C-PHY patch series text/metadata or reproducible retrieval reference;
2. compare every CAMSS hunk against true Golden and classify clean/offset/already-present/conflicting;
3. prove how `V4L2_MBUS_CSI2_CPHY` flows from endpoint parse through CSIPHY and CSID;
4. identify the X1E80100 CSIPHY generation/version and whether the series has a matching C-PHY init path;
5. inventory existing Linux Sony sensor drivers / any IMX681 work without copying proprietary source;
6. decode/summarize the local Windows IMX681 mode/register/power data needed for a clean-room driver;
7. map LDO3_M and LDO7_B to native Linux RPMh providers and prove their input parents before runtime;
8. prove the physical MCLK4 TLMM pad before E003b;
9. compile any generic C-PHY backport and DT/binding changes offline only.

## First runtime gate after E003a

E003b should prove only electrical identity (`0x0004 -> 0x0aff`) over CCI1/master1 with the Windows-derived power lifecycle. It must not depend on C-PHY or streaming.
