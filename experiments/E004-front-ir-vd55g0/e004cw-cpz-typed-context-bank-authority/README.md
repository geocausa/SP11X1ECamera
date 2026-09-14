# E004cw — CPZ typed context-bank authority and topology

## Result

**PASS: CPZ requires a dedicated typed secure FastRPC context bank, and the exact X1E/Hamoa Linux topology deliberately omits that bank. Golden and the live SP11 DT expose CDSP compute context banks 1–8 and 10–13, while the source explicitly states that compute-cb@9 is secure. No live node carries a `pd-type`. Therefore E004cv's CPZ session port is correctly fail-closed, and ordinary existing CDSP context banks must not be relabeled or reused as CPZ without recovering the downstream secure-CB9 definition.**

This gate was static/passive only. No DT overlay, IOMMU change, FastRPC request, CPZ process, ownership transition, camera runtime or SecureISP runtime occurred.

## 1. Exact live SP11 CDSP topology

The booted DT exposes twelve CDSP FastRPC context-bank devices:

- 1–8;
- 10–13.

Each is instantiated as its own platform/IOMMU-group device. There is no compute-cb@9.

The live FastRPC node is still marked `qcom,non-secure-domain`, and there is no `pd-type` property anywhere in the live tree.

Thus `/dev/fastrpc-cdsp-secure` does **not** imply that a CPZ-capable secure context bank exists underneath it.

## 2. Golden source explicitly identifies the missing bank

The exact Golden Hamoa/X1E DTS lists compute-cb@1 through @8 and then contains the comment:

`compute-cb@9 is secure`

The node itself is intentionally absent. Ordinary nodes resume at compute-cb@10 through @13.

The same pattern exists across multiple upstream Qualcomm SoCs: the public Linux tree omits the downstream secure CB9 while retaining ordinary FastRPC context banks around it.

This is stronger authority than inferring a missing number from the sequence: the source identifies bank 9 as a distinct secure class.

## 3. Downstream FastRPC requires a pre-typed context bank

Qualcomm's downstream PD-type work makes context-bank type a probe-time property. A bank may carry `pd-type`; session allocation then matches the requested remote process type.

For secure memory with typed banks enabled, FastRPC selects CPZ_USERPD (6).

So CPZ is not implemented by taking any existing ordinary context bank at runtime. The secure/CPZ bank must already exist and be typed appropriately.

E004cv therefore has the correct behavior: its CPZ rebind cannot succeed on Golden because every live session is DEFAULT_UNUSED.

## 4. Existing ordinary CBs are not parity-safe substitutes

Reusing an existing bank such as 1–8 or 10–13 would require assuming that its SMMU/security configuration is equivalent to the omitted secure CB9.

There is no same-machine evidence for that assumption, and the DTS distinction argues the opposite.

Therefore do **not**:

- tag an arbitrary existing bank as CPZ;
- choose CB10/11 merely because they are additional banks;
- infer CB9's IOMMU SID/flags from numeric sequence;
- expose E004cv's CPZ session control until secure CB9 is mechanically recovered.

## 5. IOMMU visibility model remains compatible in principle

E004co already proves the downstream secure import chain:

protected/non-HLOS-exclusive dma-buf
→ secure FastRPC memory classification
→ secure context-bank session
→ CPZ_USERPD selection.

E004cu/E004ct provide the corresponding HLOS-excluding ownership/backing state on Golden.

So the missing piece is not a new mapping architecture. It is the **exact secure context-bank device definition** that permits that already-proven mapping path.

## Safety boundary

Golden FullIO v19c remained active. No DT was edited or overlaid, no context bank was reprobed, no FastRPC ioctl was issued, no CPZ process was created, and no protected/camera runtime occurred.

## Next gate

**E004cx — X1E downstream secure CB9 recovery**, static first.

Recover authoritative same-family/same-platform data for the omitted secure context bank:

1. locate the downstream Hamoa/X1E compute-cb@9 definition if available;
2. recover its IOMMU SID(s), flags and any `pd-type` value;
3. determine whether CB9 is specifically CPZ_USERPD or a more general secure-memory bank;
4. cross-check against same-machine firmware/ACPI/QHEE evidence where possible;
5. reject any guessed SID or copied unrelated-SoC value.

Do not modify the live DT until the X1E secure-bank identity is mechanically proven.
