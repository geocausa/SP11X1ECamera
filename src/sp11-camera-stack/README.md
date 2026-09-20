# SP11 unified camera hardware authority

This directory is the maintained hardware-level authority for the Surface Pro 11 rear RGB + front RGB + front IR camera topology.

It deliberately separates **proven hardware authority** from the still-blocked protected IR execution path. The unified DTB exposes all three sensors simultaneously. CAMSS contains the disabled-by-default, Windows-exact CSIPHY0 D-PHY receiver gate. Rear OV13858 and front IMX681 remain their accepted production authorities. VD55G0 remains bind/configure/standby only and refuses direct Linux streaming.

`build-hardware-authority.sh` reconstructs the exact tested hardware set into a fresh output directory and fails closed on any hash drift. It requires both `KERNEL_SOURCE` and `KERNEL_BUILD` because the accepted external-module ELF bytes are reproduced only through the historical Kbuild source frontend plus the prepared Golden output/header tree.

The build emits the exact unified DTB, four kernel modules, front capture helper, front bootstrap helper, and `HARDWARE-MANIFEST.sha256`.

The source-only E004jd production staging correction requires the exact locally derived R4 bootstrap (41,088 bytes, pinned SHA-256) that Git archive otherwise omits from the front RGB runtime. The ignored input is hash/metadata-verified and copied only to disposable package staging with mode 0600; the newly generated **51-file** unified manifest and front manifest include it. `verify-package.py --require-r4` additionally fails on omitted/corrupt R4, symlinks and unlisted files. The historical non-strict verifier remains for old 50-file package inspection. E004jc demonstrated the real rear8-to-front27 QC10C capture with this R4 sidecar; package staging by itself does not install a camera, complete QC10C decoding or grant protected IR/Hello admission.

Rear OV13858 is the one intentional exception to source rebuilding inside this script: the accepted module was an in-tree kernel build. Its exact source is frozen here as `authority/ov13858.c`, and the accepted runtime module is frozen as `authority/ov13858-production.ko`. We do not pretend an external-module compile is equivalent.

The IR security boundary is unchanged. This authority does **not** enable illumination, direct VD55G0 streaming, Linux SecureISP, secure CB9, CPZ migration, protected ownership transfer, or SecurePD execution. Protected IR/Windows Hello runtime still requires legitimate production SecurePD worker trust admission.
