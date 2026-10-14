# Fresh07 standalone PHY2 owned power cycles

Reuses retained loop/recovery/ownership semantics; no prior generic-PHY API
diagnostic was found. New helper uses the same phy_get_by_of_node API as
CAMSS, balances init/get references, fixes C-PHY2/trio0/2.406 profile and runs
three20ms power cycles. Sensor remains off/reset low; no CAMSS stream, buffers,
pixels, firmware changes or OS sleep. This qualifies changed provider API
ownership, not RAW transport, electrical voltages or injected hardware faults.

Helper defaults to execute=false. On a teardown/unclean-start/exit fault it
pins itself and borrowed references until reboot. Observer stops and automatic
return handles recovery; no same-boot retry or manual unload on fault. On clean
success all its references are released before module removal. Compare supply,
clock and runtime-PM baseline and final post-unload/return logs.

Fresh private module tree hardlinks immutable04 KO files; non-KO metadata is
copied independently. Two changed KO targets are unlinked before replacement;
metadata generation checks the parent tree hashes before/after. Existing
kernel/initrd and qualified source29 DTB reused; fresh07 recovery identity.
