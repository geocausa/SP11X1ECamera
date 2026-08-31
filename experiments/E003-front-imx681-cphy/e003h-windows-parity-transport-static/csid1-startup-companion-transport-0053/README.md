# E003h 0053 startup CSID companion transport oracle

The same-machine Windows descriptor-1 companion bytes are now reconstructed and hash-verified exactly: packet0 is 60 bytes and packets1..3 are 16 bytes each. Windows submits them to CSID1 through RT-CDM after `CHANGE_BASE 0x00057000`; current Linux 0052 instead submits only the VFE startup base/main through RT-CDM and then applies the matching CSID companion values through CPU `writel()` calls.

This proves a **transport/ownership mismatch**, not causality. Register values and host order already match; no claim is made that RT-CDM transport is the crop fix. The only justified 0053 experiment is to preserve the exact Windows CDM transport for these already-proven bytes and remove the four startup CPU-companion calls. Runtime remains unauthorized.
