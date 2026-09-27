# E008j — rear pre-BUS two-slot ordering adapter

Status: **BUILD-ONLY PASS**.

E008h proved the two-slot ten-WM DMA ownership model, but its convenience
e008h_rear_alloc_prime_pair() deliberately performs the disabled slot0 preload
before returning. E008g subsequently closes the exact rear control order and
proves E007y packet0 is consumed before BUS configuration.

Those two facts are individually safe, but the convenience helper cannot be
used verbatim in the final rear runner.

E008j splits the operation into three explicit phases:

1. allocate both complete Linux-owned DMA sets and derive/disjoint-check all
   addresses with **no VFE MMIO**;
2. bind both E007z ledgers under the same REAR owner epoch, still with
   **no VFE MMIO**;
3. only after the caller has submitted E007y packet0, perform E008d's disabled
   static/address preload for slot0.

The caller may then invoke the already accepted E008h slot0 enable helper,
which enables WMs in E008f resource order and rewrites/readbacks the same
Linux-owned slot0 addresses. Packet1 follows that activation.

Target orchestration prefix:

allocate(no MMIO) -> bind(no MMIO) -> packet0 -> BUS config/address while
disabled -> BUS enable + owned-address rewrite -> packet1.

This adapter adds no call site, RT-CDM submit, camera start, module load or
reboot. It does not supersede E008h's ownership/retirement rules; it only
provides an exact-order entry point for the final unreachable runner.

## Build result

Fresh isolated W=1 CAMSS build passed against protected Golden headers. qcom-camss.ko is 13,811,416 bytes, SHA-256 d8a3849f426ef57d4ca167c31f4029cf186e20a9f59e5f3e99114b659a15c6ef, vermagic 7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64. PiMaster and independent Fabric verification passed. No install, load, camera runtime, RT-CDM submission or reboot occurred.
