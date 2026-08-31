# E003h 0059 — VFE1 low-TOP read-only telemetry

Static-only diagnostic delta on top of accepted 0057 camera programming and consumed 0058 result. Adds 13 `readl_relaxed()` calls to the existing bounded X1E80100 VFE1 timeout dump so Linux powered values can be compared against the preserved successful Windows LIVE1 VFE1 oracle.

No `writel*()` line changes, no new MMIO write, no sensor/CSID/CSIPHY/RT-CDM/DT/BUS-client programming change, and no runtime authorization. The Windows oracle values are frozen in `0059-static-oracle.json`.
