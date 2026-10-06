# E011LB — 169-descriptor republish closure

PASS. Starting from the accepted E011LA 164-entry runtime descriptor table, E011LB executes the original replacement-table growth path at `0x5B84B8`: it allocates/clears 0x1520 bytes, source-exactly copies all 164 inherited descriptors and five original static descriptors at RVA `0x16235D0`, destroys the superseded 164-entry ownership tree through `0x5B9BA8`, and republishes the new table with count 169. Across the exact helper path this requires 169 descriptor copies, 790 owned allocations/clears, 620 bounded string copies, and 768 frees from the superseded table. Execution stops before `0x5B8738`.

NEXT E011LC qualifies the indirect factory-object call reached at `0x5B8738` and stops before the status branch at `0x5B875C`. No new camera Start, reboot, rear runtime, or kernel build is used.
