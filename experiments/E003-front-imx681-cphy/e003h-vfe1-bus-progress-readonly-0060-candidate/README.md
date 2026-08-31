# E003h 0060 candidate — VFE1 BUS progression read-only telemetry

Distinct bounded one-shot package using the static 0060 CAMSS module. Camera programming remains byte-equivalent to the consumed 0059 path; 0060 adds only timeout-path MMIO reads for BUS common state and all nine Windows-active clients. Frozen mode2 IMX681, front-only DT, helper and RT-CDM observer are unchanged. Package must remain unarmed until a separate public authorization checkpoint.
