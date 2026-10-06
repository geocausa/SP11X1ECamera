# SP11 unified camera hardware authority

This directory is the maintained hardware-level authority for the Surface Pro 11 rear RGB + front RGB + front IR camera topology.

It deliberately separates **proven hardware authority** from the still-blocked protected IR execution path. The unified DTB exposes all three sensors simultaneously. CAMSS contains the disabled-by-default, Windows-exact CSIPHY0 D-PHY receiver gate. Rear OV13858 and front IMX681 remain their accepted production authorities. VD55G0 remains bind/configure/standby only and refuses direct Linux streaming.

`build-hardware-authority.sh` reconstructs the exact tested hardware set into a fresh output directory and fails closed on any hash drift. It requires both `KERNEL_SOURCE` and `KERNEL_BUILD` for the accepted CAMSS/IMX681 rebuild. Rear OV13858 and bind-only VD55G0 are frozen accepted runtime ELFs: their historical build bytes are not falsely re-created from a differently named checkout.

The build emits the exact unified DTB, four kernel modules, front capture helper, front bootstrap helper, and `HARDWARE-MANIFEST.sha256`.

The source-only E004jd production staging correction requires the exact locally derived R4 bootstrap (41,088 bytes, pinned SHA-256) that Git archive otherwise omits from the front RGB runtime. The ignored input is hash/metadata-verified and copied only to disposable package staging with mode 0600; the newly generated **51-file** unified manifest and front manifest include it. `verify-package.py --require-r4` additionally fails on omitted/corrupt R4, symlinks and unlisted files. The historical non-strict verifier remains for old 50-file package inspection. E004jc demonstrated the real rear8-to-front27 QC10C capture with this R4 sidecar; package staging by itself does not install a camera, complete QC10C decoding or grant protected IR/Hello admission.

Rear OV13858 and bind-only VD55G0 are the two intentional runtime-module exceptions to source rebuilding inside this script. OV13858 was an accepted in-tree build; its exact source and runtime ELF are frozen here. VD55G0 was physically accepted as the exact E004dp/dr/ds module, but its ELF embeds historical absolute Kbuild/source paths, so an identical-source rebuild from `SP11X1ECamera-clean` is not byte-identical. `authority/sp11-vd55g0-production.ko` freezes the accepted runtime artifact rather than treating path metadata drift as a new driver. Source verification still pins the VD55G0 source used to establish that artifact.

The IR security boundary is unchanged. This authority does **not** enable illumination, direct VD55G0 streaming, Linux SecureISP, secure CB9, CPZ migration, protected ownership transfer, or SecurePD execution. Protected IR/Windows Hello runtime still requires legitimate production SecurePD worker trust admission.
