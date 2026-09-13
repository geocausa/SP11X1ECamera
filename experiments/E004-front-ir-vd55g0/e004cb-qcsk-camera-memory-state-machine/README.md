# E004cb — Qualcomm Secure Kernel camera memory state machine

## Result

**PASS: the camera-specific memory state machine in `QcSkExt8380.exe` is a PIL firmware-image ownership/handoff path, not a protected frame-buffer provider. It moves camera firmware segments through HYP -> HLOS_FREE/intermediate -> camera-subsystem VMID 0x39, and reverses them through camera-subsystem -> HLOS_FREE/intermediate -> HLOS.**

This is static-only. No Windows boot, camera state switch, SMC, IUM syscall, QTEE/QSEE call or Linux protected-camera runtime occurred.

## Exact authority

The same-machine Secure Kernel extension remains:

- `QcSkExt8380.exe`
- SHA-256 `618910808afafda01533f6f0decc21209521d23db950209cebe1668520dff5e3`
- embedded PDB path `Z:\b\WP\QcSkExt\rel\10.9\ARM64\Release\QcSkExt8380.pdb`

E004ca found two camera-specific functions:

- `camera_set_state` -> Ghidra `FUN_1400138b0`;
- `pil_camera_mem_assign` -> Ghidra `FUN_140013990`.

The vendor strings embedded next to `pil_camera_mem_assign` are unusually explicit:

- `firmware segment prescan failed`;
- `unmappable segment...`;
- `failed to get ELF segment info...`;
- `map to intermediate VM from HYP failed`;
- `map to subsys from intermediate VM failed`;
- `map to intermediate VM from subsys failed`;
- `map to HLOS from intermediate VM failed`.

Those strings anchor the transition interpretation below.

## 1. This is a firmware/PIL path, not frame memory

`pil_camera_mem_assign` first walks up to 32 image entries and extracts ELF segment information.

For each mappable segment it tracks:

- physical address;
- memory size;
- ELF segment flags;
- whether neighboring segments can be merged;
- page alignment;
- segment count.

It explicitly rejects or logs:

- non-mappable segments;
- unaligned segment physical addresses;
- excessive segment counts;
- failed ELF-segment extraction.

The destination protection bits for the camera subsystem are rebuilt from the segment's ELF R/W/X flags:

- bit 0 -> execute;
- bit 1 -> write;
- bit 2 -> read.

Golden Linux independently uses the same Qualcomm permission encoding:

- `QCOM_SCM_PERM_EXEC = 0x1`;
- `QCOM_SCM_PERM_WRITE = 0x2`;
- `QCOM_SCM_PERM_READ = 0x4`.

The temporary transfer stages use permission `7` (RWX), while the final subsystem mapping preserves the individual segment's R/W/X requirements.

That is firmware image handoff behavior. It has none of the external protected-frame concepts proven in E004bv/E004bw:

- no secure buffer GUID;
- no request ID;
- no `cbBufferSize` / `cbCaptured` split;
- no serialized frame metadata extent;
- no pixel payload offset;
- no per-frame trusted worker transfer object.

Therefore this state machine must not be reused as evidence that VMID `0x39` is a protected camera-frame domain.

## 2. Vendor-anchored VMID identities

The function initializes the first local VMID slot to `0x0e`.

Golden Linux publicly names:

`QCOM_SCM_VMID_HLOS_FREE = 0x0e`.

The forward branch then writes:

- local slot 0 = `0x0e`;
- local slot 1 = `0x39`;
- local slot 2 = `4`.

The reverse branch writes:

- local slot 0 = `0x0e`;
- local slot 1 = `3`;
- local slot 2 = `0x39`.

The exact failure strings identify the roles:

- value `4` is the source called **HYP**;
- value `0x0e` is the **intermediate VM**;
- value `0x39` is the camera **subsystem** VM;
- value `3` is **HLOS**.

Linux independently names VMID `3` as `QCOM_SCM_VMID_HLOS`.

No public `QCOM_SCM_VMID_*` name for `0x39` exists in the Golden source tree, so E004cb deliberately calls it:

**camera PIL subsystem VMID 0x39**

rather than inventing an undocumented Qualcomm constant name.

## 3. Exact forward ownership choreography

Only one forward selector combination is accepted in the recovered function:

- internal object state field at `+0x14c` equals `1`;
- request selector equals `2`.

The first assignment call is immediately followed by the failure message:

`map to intermediate VM from HYP failed`

At that call:

- destination descriptor VMID = `0x0e`;
- source VMID list = `4`.

Therefore the first transition is:

**HYP (4) -> intermediate / HLOS_FREE (0x0e)**

The per-segment loop then makes a second assignment whose failure message is:

`map to subsys from intermediate VM failed`

At that call:

- destination descriptor VMID = `0x39`;
- source VMID list = `0x0e`;
- destination permissions = each ELF segment's derived R/W/X bits.

Therefore the second transition is:

**intermediate / HLOS_FREE (0x0e) -> camera PIL subsystem (0x39)**

So the complete forward handoff is:

`HYP(4) -> HLOS_FREE/intermediate(0x0e) -> camera PIL subsystem(0x39)`.

## 4. Exact reverse ownership choreography

The recovered reverse combination is:

- internal state field `+0x14c` equals `2`;
- request selector equals `0`.

Each mappable firmware segment is first reassigned with the failure anchor:

`map to intermediate VM from subsys failed`

The call has:

- destination VMID = `0x0e`;
- source VMID = `0x39`.

So:

**camera PIL subsystem (0x39) -> intermediate / HLOS_FREE (0x0e)**

After all segments are returned to the intermediate domain, one final whole-range assignment is anchored by:

`map to HLOS from intermediate VM failed`

with:

- destination VMID = `3`;
- source VMID = `0x0e`;
- destination permission = `7`.

So:

**intermediate / HLOS_FREE (0x0e) -> HLOS (3)**

The full reverse path is therefore:

`camera PIL subsystem(0x39) -> HLOS_FREE/intermediate(0x0e) -> HLOS(3)`.

## 5. `camera_set_state` brackets firmware handoff, not frame capture

The separate `camera_set_state` function accepts only state selectors `0` and `1`.

For selector `0`, it waits for a hardware idle indication before halting the core.

For selector `1`, it refuses to resume an already-running core, then invokes a helper that programs several hardware registers including a firmware/base address derived from the same camera PIL context.

Its vendor errors are:

- `core must be idle before halt`;
- `cannot resume core`;
- `setting invalid state`.

This is another strong indication that E004cb concerns camera subsystem firmware loading and core lifecycle, not per-frame secure capture.

## 6. Relationship to the earlier CP_CAMERA result

E004ca proved the SecureISP internal capture target uses:

- IUM domain `0x0d`;
- Qualcomm VMID `0x0d`;
- Linux name `CP_CAMERA`;
- write permission `0x2`.

E004cb's camera PIL subsystem VMID `0x39` is a **different domain with a different purpose**.

The distinction is now:

- `0x0d CP_CAMERA` — IFE/internal protected capture-target writer domain;
- `0x39 camera PIL subsystem` — executable camera firmware image ownership during subsystem boot/handoff;
- `0x0e HLOS_FREE` — intermediate ownership staging domain in the PIL choreography.

These must not be conflated.

## 7. Does E004cb reveal the missing external-sample provider?

No.

It proves Qualcomm ships a signed Secure Kernel policy for camera **firmware ownership**, but that policy is image/segment-oriented and core-state-oriented.

Nothing in the recovered camera PIL path provides the E004bw external-sample requirements:

1. per-sample opaque identity;
2. protected consumer lifetime;
3. captured versus allocation extent;
4. trusted serialization/payload offset;
5. protected frame-worker visibility;
6. consumer sample release semantics.

VMID `0x39` therefore must not be adopted as a frame-buffer owner simply because it is camera-specific.

## Windows oracle decision

A Windows one-shot is **not required for E004cb**.

The signed Windows Secure Kernel extension itself supplies explicit transition-direction log strings at the exact assignment callsites, plus ELF firmware-segment processing and core-state operations. Dynamic tracing would only reconfirm a state machine whose static semantics are already unambiguous, while adding avoidable boot/runtime disturbance.

Windows remains available as the next-line oracle whenever the static evidence stops being decisive.

## What remains forbidden

Do not yet:

- assign frame buffers to VMID `0x39`;
- treat HLOS_FREE `0x0e` as a protected-frame provider;
- reproduce the PIL HYP/intermediate/subsystem choreography for camera samples;
- run camera-state or PIL assignment SMCs experimentally;
- enable QCOMTEE or probe guessed service UIDs;
- activate Linux SecureISP protected runtime.

## Next gate

The provider question is now better isolated. The next useful gate is **E004cc — IUM secure-section backing/provider path below `CreateSecureSection`**, static first.

Use the exact mounted `securekernel.exe`, the IUM syscall numbers already recovered, and the Qualcomm Secure Kernel extension to determine whether the external flag-0 GUID/scenario secure section eventually uses:

- Secure Kernel private page allocation only;
- a Qualcomm VMID assignment;
- a Secure Kernel extension callback;
- a hypervisor/VTL ownership primitive;
- or a separate protected-memory service.

The key target is specifically `IumCreateSecureSection` / syscall `#0x8003`, not the already-solved `AssignMemoryToSocDomain` syscall `#0x8000`.

If static Secure Kernel reversing cannot resolve the backing/protection transition cleanly, **that is the point to use the SP11 Windows one-shot oracle** rather than infer a Linux design from incomplete evidence.
