# E004cy — compile-only X1E secure CB9 topology candidate

## Result

**PASS: the recovered X1E protected FastRPC context can be represented as a disabled Linux FastRPC context-bank node with logical index 9, SMMU stream `0x0c09/0x20`, and CPZ process type 6. The canonical fragment compiles warning-free, and an offline overlay merges cleanly into the exact currently booted SP11 device-tree topology. The node remains absent from the live kernel and is explicitly `status = "disabled"`.**

No live DT/overlay was installed. No context bank was probed, no FastRPC request was issued, no CPZ process was created, and no protected ownership or camera/SecureISP runtime occurred.

## 1. Candidate node

The compile-only source fragment is:

```dts
compute-cb@9 {
    compatible = "qcom,fastrpc-compute-cb";
    reg = <9>;
    iommus = <&apps_smmu 0x0c09 0x20>;
    dma-coherent;
    pd-type = <6>;
    status = "disabled";
};
```

Authority is split deliberately:

- `reg = <9>` comes from the exact Golden Hamoa/X1E missing secure-bank position;
- `0x0c09 0x20` comes from exact same-machine Windows SMMU policy recovered in E004cx;
- `pd-type = <6>` comes from Qualcomm downstream FastRPC's `CPZ_USERPD` contract;
- `status = "disabled"` is an E004cy safety choice, not vendor behavior.

## 2. Warning-free canonical compile

A small standalone DTS harness recreates only the structural requirements needed by the node:

- an `apps_smmu` provider with two IOMMU cells;
- an X1E CDSP remoteproc/FastRPC hierarchy;
- one included candidate CB9 fragment.

`dtc` compiles that harness with **zero warnings**. Decoding the resulting DTB gives:

- `reg = 9`;
- `iommus = <apps_smmu 0x0c09 0x20>`;
- `pd-type = 6`;
- `status = "disabled"`.

This proves the source fragment is structurally valid without touching the production tree.

## 3. Offline merge against the exact live SP11 topology

For a second proof, a temporary overlay targeted the current live path:

`/soc@0/remoteproc@32300000/glink-edge/fastrpc`

The overlay was applied only to a **file copy** reconstructed from the read-only `/proc/device-tree` dump. It merged with no overlay error.

The resulting offline node decodes as:

- `reg = 9`;
- IOMMU tuple `0x3d 0x0c09 0x20`, where `0x3d` is the current live `apps_smmu` phandle;
- `pd-type = 6`;
- `status = disabled`;
- `dma-coherent` present.

The real live path `/proc/device-tree/.../compute-cb@9` remained absent afterward.

## 4. Why the node remains disabled

E004cx solved the hardware stream identity and E004cv solved the privilege-gated FastRPC control/import logic, but those pieces have not yet been linked into one Golden kernel build.

Enabling CB9 now would be premature because the booted FastRPC driver:

- does not parse `pd-type`;
- does not expose E004cv's CPZ session control;
- does not carry E004cu's protected dma-buf query;
- does not carry E004ct's SG ownership backend.

An enabled DT node without those host pieces would at best be unused and at worst create a misleading partially-live security path.

## 5. Evidence boundary

This gate does **not** claim that an exact proprietary Hamoa downstream DTS was recovered.

The candidate topology is a mechanically derived Linux representation composed from:

1. exact Golden Hamoa source (`compute-cb@9 is secure`);
2. exact same-machine Windows SMMU stream policy (`S1_COMPUTE_CP_P -> 0x0c09/0x20`);
3. Qualcomm downstream FastRPC ABI (`CPZ_USERPD = 6`).

That is enough for a compile-only topology candidate, not enough by itself for runtime activation.

## Safety boundary

Golden FullIO v19c stayed active, the saved boot entry was untouched and no one-shot was armed. No DT was installed or applied to the live kernel, no IOMMU/context-bank state changed, no FastRPC/CPZ operation ran and no camera/SecureISP runtime was invoked.

## Next gate

**E004cz — integrated Golden protected-provider build closure**, compile-only first.

Combine the already-proven disabled pieces in a temporary build tree:

1. E004ct multi-region SG ownership API;
2. E004cu protected dma-buf state wrapper;
3. E004cv privilege-gated CPZ FastRPC session/import path;
4. E004cy secure CB9 node, still disabled;
5. the CAMSS provider capability contracts from E004cp/E004cr.

The gate must prove link/build compatibility and fail-closed default behavior. Do not install the kernel/modules/DTB and do not enable CB9 or protected runtime.
