# SP11 unified camera hardware authority

This directory is the maintained hardware-level authority for the Surface Pro 11 rear RGB + front RGB + front IR camera topology.

It deliberately separates **proven hardware authority** from the still-blocked protected IR execution path. The unified DTB exposes all three sensors simultaneously. CAMSS contains the disabled-by-default, Windows-exact CSIPHY0 D-PHY receiver gate. Rear OV13858 and front IMX681 remain their accepted production authorities. VD55G0 remains bind/configure/standby only and refuses direct Linux streaming.

`build-hardware-authority.sh` reconstructs the exact tested hardware set into a fresh output directory and fails closed on any hash drift. It requires both `KERNEL_SOURCE` and `KERNEL_BUILD` because the accepted external-module ELF bytes are reproduced only through the historical Kbuild source frontend plus the prepared Golden output/header tree.

The build emits the exact unified DTB, four kernel modules, front capture helper, front bootstrap helper, and `HARDWARE-MANIFEST.sha256`.

Rear OV13858 is the one intentional exception to source rebuilding inside this script: the accepted module was an in-tree kernel build. Its exact source is frozen here as `authority/ov13858.c`, and the accepted runtime module is frozen as `authority/ov13858-production.ko`. We do not pretend an external-module compile is equivalent.

The IR security boundary is unchanged. This authority does **not** enable illumination, direct VD55G0 streaming, Linux SecureISP, secure CB9, CPZ migration, protected ownership transfer, or SecurePD execution. Protected IR/Windows Hello runtime still requires legitimate production SecurePD worker trust admission.
