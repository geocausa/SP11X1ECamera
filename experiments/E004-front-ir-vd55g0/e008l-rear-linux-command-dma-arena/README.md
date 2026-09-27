# E008l — rear Linux command-DMA arena

Status: **BUILD-ONLY PASS**.

## Goal

Close E008k's remaining command-memory ownership gate without submitting anything to hardware.

E007y intentionally requires the caller to provide Linux-owned 32-bit DMA backing for each packet's MAIN, wrapper and every DMI payload, plus CPU-only dynamic scratch. E008l provides that ownership mechanically for all four rear startup packets.

Each packet gets one coherent DMA slab. MAIN starts at offset zero, the 0x100-byte wrapper follows at 4-byte alignment, and every DMI payload is suballocated at a 4-byte-aligned offset. DMI payload lengths are parsed directly from the accepted E007y startup skeleton, not duplicated as a new table. The entire returned Linux DMA span is validated against the VFE/CDM 32-bit aperture before any address is exposed.

The descriptor array and e006g_rear_dynamic_payloads scratch remain ordinary kernel CPU allocations because only the MAIN/wrapper/DMI payload bytes are hardware command/data targets.

## Lifetime

Before any RT-CDM submission, the complete command set may be zeroed and freed normally. Once any packet is marked submitted, E008l refuses release until the caller supplies an independently proven rtcdm_stopped=true. This deliberately pins every command slab across the complete transaction rather than guessing when individual BL fetches are complete.

This is stricter than necessary but closes the first bounded-run lifetime safely. Hardware-fault paths can leave the set pinned until reboot.

No runtime call site, RT-CDM submit, module load, camera activation or reboot is introduced by this checkpoint.

## Build result

Fresh isolated W=1 build passed against protected Golden headers. qcom-camss.ko is 14,664,024 bytes, SHA-256 500c8dd00e64c307b9c447bfd5bea0e7284da0f28693f3db9cda4a5c6c2e9901, exact Golden vermagic. PiMaster and independent Fabric verification passed. No install, load, camera activation, RT-CDM submission or reboot occurred.
