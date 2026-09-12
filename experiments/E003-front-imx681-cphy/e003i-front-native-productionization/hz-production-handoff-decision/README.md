# E003i-HZ — production handoff decision

Status: **PASS / offline decision**.

HY proves a real front-RGB production stream on the exact current-Golden-derived HV DTB. E002k-D-R3 independently proves the rear OV13858 production stream. HZ asks whether either accepted DTB can now become the durable whole-camera production image.

The answer is **not yet**. The HV front DTB intentionally disables the rear OV13858 and exposes only CAMSS `port@2`; the accepted rear DTB exposes only `port@1`. More importantly, the shared CAMSS node is not identical: front authority adds RT-CDM1 register/IRQ resources and uses the front-proven five-entry IOMMU fwspec, while rear authority uses its accepted eight-entry fwspec without RT-CDM1. Simply concatenating nodes or making the front DTB the default would silently discard accepted rear authority.

Therefore protected Golden stays the saved default. Front and rear proofs remain independently accepted. The production handoff now moves to an **offline unified rear+front shared-CAMSS authority analysis** on exact current Golden. That stage must reconcile the common CAMSS resources and both routes from evidence; it must not guess an IOMMU union and must not broaden front post-G3 writes beyond `shadow`.
