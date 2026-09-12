# Camera IA — unified rear+front shared-CAMSS authority

Status: **PASS / offline only**.

HZ established that front HY and rear E002k-D-R3 are separately production-proven but cannot be promoted by simply choosing one DTB. IA closes the next shared-device question.

The durable module candidate must use the front production `qcom-camss.ko`, because front PIX/RT-CDM1 requires it, together with the exact accepted IMX681 and OV13858 sensor modules. All three match Golden vermagic. Relative to the exact Golden CAMSS source, the private front CAMSS keeps the X1E CSIPHY, CSID, ICC and CSID-wrapper static resource tables byte-identical. In the X1E VFE static table the only change is the VFE1 PIX format pointer; both VFE0/VFE1 RDI format pointers remain unchanged. This is strong offline evidence that rear VFE0 RDI static routing is preserved, but it does not replace a live rear regression because generic CAMSS runtime code also evolved for front PIX.

For IOMMU authority, IA does **not** discard either accepted set. It mechanically forms the conservative union of the rear eight-entry and front five-entry fwspecs, preserving every accepted SID/mask. The exact Golden ARM-SMMU stream-match allocator accepts the 11-specifier union without partial-overlap conflict; masks collapse it to six hardware mapping groups, all attached to the same CAMSS domain. This makes the union a defensible offline candidate rather than a guessed reduced list.

The next combined DTB should therefore start from exact current Golden/HV front resources, enable rear OV13858, add rear `port@1` alongside front `port@2`, retain RT-CDM1/front apertures, and replace the five-entry fwspec with the conservative 11-specifier union. **No runtime is authorized yet.** Rear must be regressed first under this private CAMSS + unified fwspec before front is rechecked.
