# E003h 0052 one-shot candidate — X1E front CSID link-derived clock rate

Distinct Golden-safe package for 0052. Relative to consumed 0051, only `qcom-camss.ko` changes. The exact proven X1E front route (CSID1 + CSIPHY2 + one-trio C-PHY) now sends `csid` and `csid_csiphy_rx` through the existing link-derived CSID rate algorithm. For the frozen 1.2GHz C-PHY link this changes the requested clocks from the generic first entry 300MHz to the existing calculated 400MHz selection.

The helper, IMX681 module, front-only DTB, oracle capsule, media setup and persistent RT-CDM observer are byte-identical to 0051. No CSID crop/RUP/AUP, VFE, RT-CDM, CSIPHY programming, sensor or DT value changes. Installation cannot arm the boot. Runtime requires a separately committed authorization and permits one helper invocation only.
