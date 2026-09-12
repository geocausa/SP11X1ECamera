# E003i-HU — production boot/module/firmware integration authority

Status: **PASS / offline + read-only Golden inspection**.

HT proved that userspace installation alone cannot activate the camera. HU closes the missing boot/module/firmware authority without changing Golden.

The accepted historical front-only DTB is **not authorized for direct production reuse**. It has the accepted front route (`port@2`, IMX681 at 0x10, C-PHY bus type 1, lane 0, five-entry CAMSS IOMMU set) and its node-path set is a structural superset of current Golden: 1,433 versus 1,402 nodes, with exactly 31 candidate-only nodes and no Golden-only paths. But its builder was based on older DTB SHA256 `333e...b14e`, not current protected Golden SHA256 `2fcf...6d00`. Structural containment is therefore not semantic identity.

The production modules remain exactly HN (`qcom-camss.ko` `7afe...97e95`, `imx681.ko` `ef57...f63d6`) with Golden vermagic. Neither module advertises firmware, has unresolved firmware-loader symbols, or embeds the e003i candidate token. The current production source has no functional firmware-loader call, so the historical candidate `firmware_class.path=` is legacy baggage for this production runtime; IQ authority is packaged with the launcher.

The proven live activation sequence is dependency modules, private qcom-camss, then private IMX681. The candidate boot token was enforced by fail-closed runtime preflight, not inside the modules. Production integration therefore still requires an equivalent activation gate.

Next: HV constructs a new camera-capable DTB from **current Golden**, imports only the proven camera authority, and proves Golden common-node semantic preservation before any fresh boot candidate exists.
