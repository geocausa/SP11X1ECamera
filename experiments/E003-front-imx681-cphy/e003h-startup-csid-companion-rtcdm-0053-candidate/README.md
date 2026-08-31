# E003h 0053 one-shot candidate — startup CSID companion RT-CDM transport

Distinct Golden-safe package for 0053. Relative to consumed 0052, only `qcom-camss.ko` changes. The four initial startup CSID1 companion command lists keep the exact same register values and host order but move from CPU MMIO replay to the captured Windows RT-CDM transport: `CHANGE_BASE(VFE1) -> IFE main -> CHANGE_BASE(CSID1) -> exact descriptor-1 companion`.

Packet0 companion bytes hash exactly to the Windows capture `1872731e...e2a2`; packets1..3 hash to `45d059ec...5c7`. No new register value, crop coordinate, RUP/AUP value, VFE, CSIPHY, sensor or DT programming is introduced. The helper, IMX681 module, front-only DTB, oracle capsule, media setup and persistent RT-CDM observer are byte-identical to 0052. Installation cannot arm the boot. Runtime requires a separately committed authorization and permits one helper invocation only.
