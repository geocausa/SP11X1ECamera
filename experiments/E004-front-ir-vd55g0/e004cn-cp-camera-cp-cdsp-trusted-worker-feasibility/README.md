# E004cn — CP_CAMERA + CP_CDSP trusted-worker feasibility

## Result

**PASS: the Qualcomm camera stack has an explicit protected `CP_CAMERA + CP_CDSP` buffer mode, and the same-machine CDSP firmware contains a real CPZ/secure-process substrate. However, Golden Linux does not expose an authoritative host binding that lets our own FastRPC worker execute against CP_CDSP/CPZ-owned camera buffers without retaining HLOS access. CP_CDSP is therefore a justified next research path, but not yet a selectable protected-frame worker backend.**

This gate remained static/passive. No camera stream, ownership transition, SCM reassignment, CPZ process creation, CDSP restart, FastRPC invocation, Windows boot or SecureISP runtime occurred.

## 1. Qualcomm camera source proves the co-owner contract

Archived Qualcomm camera source contains a dedicated protected-output flag:

`CAM_MEM_FLAG_CDSP_OUTPUT`

When it is combined with `CAM_MEM_FLAG_PROTECTED_MODE`, camera allocation selects the secure heap and constructs the owner set:

- `VMID_CP_CAMERA` — read/write;
- `VMID_CP_CDSP` — read/write.

The legacy ION path expresses the same policy as:

`ION_FLAG_SECURE | ION_FLAG_CP_CAMERA | ION_FLAG_CP_CDSP`

This independently corroborates the E004cm same-machine QHEE rule table. `CP_CAMERA + CP_CDSP` is a real Qualcomm protected-camera design, not a guessed owner combination.

## 2. The camera protected buffer is intentionally not KMD CPU-mapped

The same camera memory manager rejects protected-mode buffers with KMD access and routes protected mappings through stage-2/SMMU handling rather than ordinary kernel virtual mapping.

That matches the Windows parity requirement that protected image backing must not become an ordinary HLOS CPU buffer.

So the camera side of the architecture has the correct shape:

`IFE/CAMSS -> protected backing -> CP_CAMERA + CP_CDSP`

The missing question is which CDSP process can actually consume that backing.

## 3. Same-machine CDSP firmware has a real protected-process substrate

Golden is already running the exact X1E CDSP firmware:

`qcom/x1e80100/microsoft/Denali/qccdsp8380.mbn`

The firmware contains explicit secure-process machinery, including:

- `secure_process`;
- `SIGNED`, `UNSIGNED`, `SECURE_ROOT`;
- `qurtos_secure_proc_v2.c`;
- `only one CPZ PD allowed to run!!`;
- `fastrpc_invoke_mmap_get_cpz_phys`.

This is materially stronger than ordinary FastRPC user-PD evidence: the DSP firmware itself understands a CPZ/protected process and a CPZ physical mapping path.

But the firmware strings alone do not identify the host-side authorization contract for creating that process or exposing a CP_CAMERA+CP_CDSP camera buffer to it.

## 4. Golden FastRPC is live, but its normal CDSP path is not CP_CDSP policy

Golden currently has:

- `fastrpc` loaded;
- `/dev/fastrpc-cdsp`;
- `/dev/fastrpc-cdsp-secure`;
- CDSP remoteproc running with the exact Denali firmware.

The live CDSP FastRPC DT node is marked `qcom,non-secure-domain` and has **no `qcom,vmids` property**.

The mainline FastRPC driver creates both `fastrpc-cdsp` and `fastrpc-cdsp-secure` for CDSP. The `-secure` device controls whether the host request is allowed to enter the signed-PD path; it does not by itself assign buffers to `VMID_CP_CDSP`.

Therefore the existence of `/dev/fastrpc-cdsp-secure` must not be misread as proof of CP_CDSP memory ownership.

## 5. Mainline `FASTRPC_ATTR_SECUREMAP` is not the required no-HLOS mapping

The current Linux driver can perform an SCM assignment for `FASTRPC_ATTR_SECUREMAP`, but its destination set is explicitly:

- HLOS read/write;
- one DT-supplied FastRPC VMID read/write/execute.

On free, it expects the source set to contain both HLOS and that VMID and returns ownership to HLOS.

Two consequences follow:

1. this path deliberately **retains HLOS as an owner**;
2. X1E's live CDSP node has no `qcom,vmids`, so there is no authoritative `CP_CDSP` destination configured here anyway.

That is not Windows-equivalent protected-frame ownership.

## 6. Static-PD remote heap is a different mechanism, still without X1E CP_CDSP authority

FastRPC static-process creation can assign its remote heap exclusively to a DT-configured VMID set and later assign it back to HLOS on failure/teardown.

That mechanism proves Linux FastRPC can support non-HLOS DSP-owned memory when platform DT supplies an owner list.

However:

- X1E CDSP FastRPC supplies no `qcom,vmids` list;
- no SP11 DT/source authority was found binding FastRPC to `QCOM_SCM_VMID_CP_CDSP (0x2a)`;
- no static PD identity was found that is documented as the camera CPZ worker.

So editing DT to inject `0x2a` would be an experiment based on inference, not parity evidence, and remains forbidden.

## 7. Windows proves ordinary camera CDSP clients, not the protected-frame worker

The exact SP11 `QcDeviceMFT8380.dll` delay-loads `libcdsprpc.dll` and contains two substantial CDSP client families:

- BitML/NSP inference via `libbitml_nsp_v2_skel.so` on `_dom=cdsp`;
- IFE/HVX DSP control via `libdsp_streamer_skel.so` on `_dom=cdsp`.

The bundled `libbitml_nsp_v2_skel.so` is a large Hexagon neural-network/HTP library. The DeviceMFT contains the model name `bm3a68v08s11n52.bin` and explicit BitML register/execute/deregister flows.

This corrects the earlier ambiguity around the SecureISP package's DSP payload: the BitML skeleton is consumed by DeviceMFT as an inference workload. It is **not evidence that the SecureISP VTL1 final protected-frame transfer runs on CDSP**; E004br/E004cf already proved that final transfer is CPU work inside the VTL1 trustlet.

Likewise, the IFE/HVX `dsp_streamer` path is a normal camera CDSP control/processing client. Static evidence does not connect it to the VTL1 external secure-section transfer.

## 8. Why CP_CDSP remains interesting

Unlike pKVM, Gunyah trusted VMs, or generic QTEE services, `CP_CDSP` has all three architectural ingredients in the platform:

- a same-machine QHEE rule allowing co-ownership with `CP_CAMERA`;
- a real protected/CPZ process model in the CDSP firmware;
- a mature FastRPC execution transport already active on Linux.

The missing authority is now sharply bounded:

> how does a host request or identify the CPZ process, and how does that process map a `CP_CAMERA + CP_CDSP` buffer while HLOS has no access?

Until that is proven, CP_CDSP cannot satisfy the E004ce provider gate.

## What remains forbidden

Do not yet:

- add `qcom,vmids = <0x2a>` to the live FastRPC node;
- use `FASTRPC_ATTR_SECUREMAP` and call it protected parity;
- create a CPZ PD;
- invoke arbitrary DSP code against protected camera memory;
- call `qcom_scm_assign_mem()` for CP_CAMERA/CP_CDSP;
- restart CDSP;
- enable protected camera runtime.

## Evidence

- `evidence/QCOM-CAMERA-CP-CDSP-AUTHORITY.txt`
- `evidence/QCOM-CAMERA-CDSP-OUTPUT-FLOW.txt`
- `evidence/QCOM-PROTECTED-CAMERA-CPU-MAP-INVARIANTS.txt`
- `evidence/SP11-CDSP-SECUREISP-PAYLOAD.txt`
- `evidence/LINUX-FASTRPC-SECURE-PD-CONTRACT.txt`
- `evidence/FASTRPC-ASSIGNMENT-SEMANTICS.txt`
- `evidence/GOLDEN-FASTRPC-DEVICE-SIGNED-PD-SEMANTICS.txt`
- `evidence/LIVE-FASTRPC-DT-POLICY.txt`
- `evidence/VENDOR-FASTRPC-CP-CDSP-DT-AUTHORITY.txt`
- `evidence/WINDOWS-BITML-CDSP-CLIENT-DISCOVERY.txt`
- `evidence/DEVICE-MFT-BITML-CDSP-SURFACE.txt`
- `evidence/DEVICEMFT-IFEDSP-HVX-METHODS.txt`
- `evidence/DSP-STREAMER-PROVIDER-SEARCH.txt`

## Next gate

**E004co — CDSP CPZ protected-process authority**, static first.

Trace the DSP-side `secure_process` / `qurtos_secure_proc_v2` / `fastrpc_invoke_mmap_get_cpz_phys` path and its host protocol. Determine:

1. what FastRPC request creates or selects the CPZ PD;
2. whether CPZ identity is fixed/signed or host-selectable;
3. how a host buffer is marked or mapped as CPZ/CP_CDSP memory;
4. whether CP_CAMERA+CP_CDSP camera output can enter that process without HLOS ownership;
5. whether the installed Windows camera CDSP clients ever request this CPZ path.

Stay static/read-only unless a later dynamic oracle has one sharply defined question that static reversing cannot answer.
