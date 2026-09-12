# E003i-HV — current-Golden camera DTB merge

Status: **PASS / offline only**.

HU blocked direct reuse of the historical camera DTB because that artifact was built from an older platform base. HV instead copies the exact protected Golden DTB and imports only the 31 proven camera-only nodes plus the camera symbol aliases. All candidate phandle references are remapped by provider **path**, with new collision-free phandles assigned only to camera-added nodes.

The resulting DTB preserves every pre-existing Golden property byte-for-byte. It removes zero Golden nodes, adds exactly 31 camera nodes, and changes no common-node property other than adding camera-only entries under `/__symbols__`. The accepted front-only route remains CAMSS `port@2`, Sony IMX681 at `0x10`, C-PHY bus type 1 / lane 0, rear sensor disabled, and the five-entry X1E CAMSS IOMMU set.

A second rebuild is byte-identical. DTC emits exactly the same pre-existing warnings as the protected Golden DTB and adds no graph warning or new warning. No boot bundle is created or armed by HV; no camera runtime occurs and Golden is untouched.

Next: HW packages this merged DTB with the exact HN modules and an explicit fail-closed activation gate, still offline, before deciding whether a fresh disposable live candidate is warranted.
