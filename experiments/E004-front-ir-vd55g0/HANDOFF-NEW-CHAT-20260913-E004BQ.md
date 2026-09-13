# Camera project handoff — new chat — 2026-09-13

## Resume point

Repository:

`/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`

Branch:

`experiment/e004-front-ir-vd55g0`

Current pushed HEAD:

`42a5a12 camera: define two-buffer protected contract`

Origin is in sync at `42a5a12`.

Do **not** start from older handoff text or redo the E004bm scaffold. The project has advanced well beyond that.

## Machine scope

For this camera project use only:

- **SP11** — primary Linux/Windows oracle target; one-shot Windows boots are authorized as often as needed.
- **SP7** — KDNET / light analysis helper; avoid sustained heavy work because of the known fan issue.
- **PiMaster** — orchestration/access only.

Do not use GeoServer, HostFabric machines, or the Mac hosts for camera work.

## Governing parity rule

The project goal is **Windows camera parity on Linux**.

Use this order:

1. Windows runtime/oracle whenever it can answer the question cleanly.
2. Static Windows analysis when dynamic tracing cannot expose the answer.
3. Linux/Qualcomm sources only after Windows behavior/ownership has been established.
4. Do not guess Linux architecture from generic Qualcomm conventions if Windows can answer it.

Windows experiments are one-shot and must return immediately to Golden Linux.

Do not weaken Windows code integrity, Secure Boot policy, testsigning, or other security controls.

## Current Golden Linux state

Verified immediately before this handoff:

- kernel: `7.1.5-sp11-render-parity-v4+`
- cmdline uses protected v19c Golden entry
- `saved_entry=sp11-audio-fullio-v19c`
- `next_entry=` empty
- `BootCurrent: 0005`
- BootOrder: `0005,0004,0000,0001,0002,0006`
- `Boot0006 = Windows Direct Oracle Temp` -> Microsoft bootmgfw.efi
- no `/dev/media*`
- no `/dev/video*`
- no CAMSS / VD55 / QCOMTEE camera runtime modules loaded

Keep Golden intact unless deliberately arming a one-shot experiment.

## Important pushed checkpoints

Newest sequence:

- `42a5a12` — **E004bq**: define two-buffer protected contract
- `18bc392` — **E004bp**: prove two-buffer protected pipeline
- `d4f9206` — **E004bo**: inventory protected memory primitives
- `f16372c` — **E004bn**: separate protected lifecycle contracts
- `4a05b86` — **E004bm**: scaffold protected sample contract
- `86fceea` — **E004bl**: map Linux protected sample boundaries
- `dc13cac` — **E004bk**: close FsIso secure section server path
- `7a62c19` — **E004bj**: map MFPlat secure buffers to FsIso
- `a7d2c43` — **E004bi**: pin MFCore secure capture allocator owner
- `66c5213` — **E004bh**: map Windows secure buffer ownership contract
- `e3aba09` — Windows protected-worker / CAMSS ordering checkpoint

Run the verifier in any checkpoint before relying on it.

## E004bq — current durable frontier

Directory:

`experiments/E004-front-ir-vd55g0/e004bq-linux-two-buffer-compile-contract/`

Verifier:

`python3 experiments/E004-front-ir-vd55g0/e004bq-linux-two-buffer-compile-contract/verify_e004bq.py`

Current result:

`PASS_COMPILE_ONLY_TWO_BUFFER_PROTECTED_PIPELINE_ZERO_TEXT_DIFF`

It proves, at compile-contract level, that the future Linux parity shape has **five separate domains**:

1. protected queue policy;
2. internal secure capture target;
3. external protected consumer sample;
4. protected transfer/processing boundary;
5. secure lane ownership.

The internal target alone carries:

- physical ownership range;
- separate CAMSS-visible IOVA;
- protected backing handle/state.

The external protected sample deliberately has **no CAMSS IOVA**.

There is no backend instance, runtime selector, ioctl, V4L2 control, VMID choice, SCM call, QCOMTEE call, or callback call site.

Baseline and scaffold executable `.text` are byte-identical:

`fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e`

Production CAMSS source remains untouched.

## Crucial Windows correction from E004bp

Directory:

`experiments/E004-front-ir-vd55g0/e004bp-windows-two-buffer-protected-pipeline-static/`

Windows does **not** make the external VTL1 sample the direct camera-hardware target.

Proven pipeline:

`camera / IFE hardware`
→ **internal SecureISP buffer assigned to CP_CAMERA**
→ **trusted protected-worker transfer / processing**
→ **external GUID-addressed VTL1 secure sample**

Important details:

- internal allocation is assigned to Windows domain `0x0d`, cross-checked against Linux `QCOM_SCM_VMID_CP_CAMERA`;
- hardware `hMems[]` / protected IFE request addresses come from the internal allocation;
- external VTL1 sample is opened separately by GUID;
- trusted worker transfer direction is:
  **internal secure mapping -> external VTL1 mapping**;
- Windows transfer occurs inside the trusted worker where **both protected mappings are visible**;
- ordinary HLOS `memcpy()` is therefore **not parity**;
- secure-lane ownership is a third independent lifetime.

Do not regress to the earlier single-buffer model.

## Windows protected sample lifetime chain

The fully mapped Windows external protected-sample chain is:

`MFCore SecureMode`
→ current capture surface `0x10`
→ `MFCreateSecureBufferAllocator`
→ MFPlat `SecureMediaBuffer` + per-buffer GUID
→ CameraTrustlet local `ncalrpc`
→ `FsIso.exe`
→ `RpcCreateSecureSection`
→ IUM `CreateSecureSection`
under secure-camera scenario
`AE53FC6E-8D89-4488-9D2E-4D008731C5FD`.

Destroy path uses the same GUID and ends with FsIso closing the secure-section handle.

This external sample lifetime is separate from:

- SecureISP internal CP_CAMERA allocation;
- secure CSI/worker lane ownership.

## Linux primitive inventory already proven

E004bo established:

- `qcom_scm_assign_mem()` exists;
- `QCOM_SCM_VMID_CP_CAMERA = 0x0d`;
- ownership assignment must be treated transactionally with explicit reclaim/rollback;
- CAMSS is SMMU-attached;
- `sg_dma_address()` is a CAMSS DMA/IOVA and must **not** be treated as the physical address used by `qcom_scm_assign_mem()`;
- physical ownership range and CAMSS IOVA must be tracked separately;
- ordinary system/CMA heaps are CPU-visible and are not themselves protected-camera backends.

No SCM ownership change has been executed.

## Fresh static findings immediately before handoff — NOT YET A DURABLE CHECKPOINT

These were discovered after `42a5a12` and should be the starting point for the next experiment, probably **E004br**.

### QSEECOM

Golden kernel config has:

- `CONFIG_QCOM_SCM=y`
- `CONFIG_QCOM_QSEECOM=y`
- `CONFIG_QCOM_QSEECOM_UEFISECAPP=y`
- `CONFIG_QCOM_TZMEM=y`
- TZMEM shmem-bridge mode enabled.

The current upstream-ish QSEECOM driver only auto-registers one known secure app:

`qcom.tz.uefisecapp`

The underlying SCM layer provides generic:

- `qcom_scm_qseecom_app_get_id()`
- `qcom_scm_qseecom_app_send()`

The SP11 Microsoft Denali machine is already present in the kernel's QSEECOM machine allowlist.

Do **not** call these yet. This is static inventory only.

### QCOMTEE

The source tree contains a newer Qualcomm TEE object transport under:

`drivers/tee/qcomtee/`

including generic object invocation APIs.

But Golden currently has:

`# CONFIG_QCOMTEE is not set`

and no QCOMTEE runtime is loaded.

Do not enable/load it merely because the source exists.

### TEE DMA-BUF heaps

Golden has:

`CONFIG_TEE_DMABUF_HEAPS=y`

The generic TEE heap framework supports protected-memory pool IDs including:

- secure video play;
- trusted UI;
- secure video record.

The implementation deliberately maps protected backing to devices with DMA APIs and avoids ordinary CPU synchronization assumptions.

However, **no active TEE protected heap provider is present on Golden**.

Runtime `/dev/dma_heap` currently contains only ordinary:

- `system`
- `default_cma_region`
- `reserved`

So `CONFIG_TEE_DMABUF_HEAPS=y` does not mean SP11 currently has a usable protected camera heap.

### Installed Linux firmware / secure app first pass

A filename/content first pass did **not** reveal an obvious installed Linux camera SecureISP/QSEE trustlet equivalent.

Installed Qualcomm firmware includes the expected X1E ADSP/CDSP/display firmware, but no obvious camera secure-app file was identified by this first pass.

Treat this as **not yet exhaustive**. Do not conclude the secure service does not exist until the Windows/firmware side has been searched more deeply.

### Transfer-backend conclusion so far

There is no generic in-tree Linux “protected memcpy” service identified yet.

Because Windows performs the internal -> external transfer inside a trusted worker with both mappings visible, the final Linux parity backend likely needs a **trusted-world service** or equivalent protected execution boundary, not an HLOS CPU memcpy.

The exact service/ABI remains unresolved.

## Exact next gate

Start **E004br — protected transfer backend authority map**.

Goal:

Determine, statically first, what trusted component on SP11 Linux/firmware could legally see both:

- the internal CP_CAMERA capture target;
- the external protected consumer sample;

and perform the Windows-equivalent transfer/processing.

Preferred order:

1. Re-read E004bp transfer evidence and keep internal-source/external-destination fixed.
2. Inspect the Windows SecureISP/trustlet task protocol for the operation that performs that transfer. If needed, return to the Windows oracle because Windows remains authority.
3. Search the SP11 firmware / Windows driver packages for the corresponding Qualcomm secure-app identity or ABI.
4. Compare that against Linux QSEECOM and QCOMTEE transports.
5. Determine whether an existing loaded secure app can service the operation, or whether Linux currently lacks the trusted counterpart.
6. Separately assess whether the generic TEE DMA-BUF heap framework is useful for the **external protected sample**. Do not assume its “secure video record” heap equals the Windows secure-camera scenario.
7. Produce a static RESULT + verifier before any runtime secure call.

Do **not** yet:

- execute `qcom_scm_assign_mem`;
- probe CP_CAMERA ownership dynamically;
- load/enable QCOMTEE;
- issue QSEECOM app-send calls;
- use HLOS memcpy as the protected transfer;
- touch protected MMIO;
- expose protected samples through mmap/read;
- modify VD55G0 sensor security policy.

If static analysis genuinely bottoms out, a one-shot Windows oracle boot is authorized.

## Windows one-shot boot

Persistent Golden boot policy must stay unchanged.

Current dedicated temporary Windows entry:

`Boot0006* Windows Direct Oracle Temp`

Use BootNext/one-shot behavior only, then reboot back to Golden and verify:

- BootCurrent `0005`;
- saved v19c;
- next_entry empty;
- no camera nodes/modules unless deliberately part of an authorized Linux candidate.

## SP7 KD note

Loss of PiMaster connectivity while Windows is paused at a KD breakpoint is expected. Do not misdiagnose that as SP11 needing wake/recovery.

SP7 can be used for KDNET tracing; avoid heavy sustained analysis on it.

## Repo hygiene

There are many pre-existing unrelated modified/untracked files in the repo.

Do not bulk-stage.

Stage only the current experiment directory/files you intentionally created.

In particular, the following tracked docs are already modified and should not be swept into a camera checkpoint unless explicitly updating them:

- `CONTINUE.md`
- `HANDOFF.md`
- `PROJECT_STATE.md`
- `README.md`
- `state/project.yaml`

## Suggested first command sequence in the new chat

On SP11:

```bash
cd /home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
git rev-parse --short HEAD
git log -8 --oneline --decorate
python3 experiments/E004-front-ir-vd55g0/e004bq-linux-two-buffer-compile-contract/verify_e004bq.py
uname -r
grub-editenv /boot/grub/grubenv list
efibootmgr
```

Expected HEAD: `42a5a12`.

Then create E004br only after confirming the exact state.

## Paste-this prompt for the new ChatGPT chat

> Continue the SP11 camera Windows-parity project from `experiments/E004-front-ir-vd55g0/HANDOFF-NEW-CHAT-20260913-E004BQ.md` on branch `experiment/e004-front-ir-vd55g0`. First verify exact HEAD and Golden state from the handoff. Current pushed HEAD should be `42a5a12`; E004bq verifier must pass. Do not redo earlier work. Windows remains the oracle, with static Windows fallback when dynamic evidence is weaker. The current frontier is the protected internal-CP_CAMERA -> external-VTL1 transfer backend: Windows proves it happens inside a trusted worker with both protected mappings visible, so ordinary Linux HLOS memcpy is not parity. Continue with the E004br static authority map described in the handoff. You may one-shot boot SP11 to Windows as often as necessary and use SP7 for KDNET/light analysis, then always return to Golden. Do not enable Linux SecureISP/QCOMTEE, issue QSEECOM app-send, execute SCM memory assignment, touch protected MMIO, or weaken Windows security until a verifier-backed static checkpoint explicitly justifies the next runtime gate. Commit/push meaningful checkpoints at your discretion and stage only intentional experiment files.
