# E004cl — Qualcomm HypX / protected-hypervisor extension authority

## Result

**PASS: same-machine Qualcomm HypX is an authenticated boot-time platform-hypervisor extension path tied to the Microsoft Hyper-V secure-launch stack. It is not exposed as a reusable post-boot extension/service mechanism for an arbitrary camera worker.**

No Windows boot was needed. Static evidence resolved the ambiguity more cleanly than a post-boot probe could: the HypX authenticate/launch operations live inside QHEE's early hypervisor manager and are not present in the runtime QcTrEE `MssecService` surface.

## 1. Same-machine QHEE has a singular HypX manager

The exact QHEE image remains:

`cc33b7c0d902f0aafd64d3d866899401af7d4e0ad1c9ffc1cc97555d9a6bd78a`

Its HypX source-bearing diagnostics identify:

`hyp/platform/qhee_hypx/src/qhee_hypx.c`

and a singular platform configuration consisting of:

- `HypXBaseAddr`;
- `HypXSize`;
- `HypXCodeAddr`;
- `HypXDataAddr`;
- `HypXStackSize`;
- `HypXVersion`;
- `HypXBTIEnabled`.

The launch path is gated by `hyp_secure_launch_enabled` in devcfg and reports one-time states such as:

- `HYPX NOT ENABLED`;
- `HYPX relocated`;
- `HYPX REGISTRATION SUCCESS`.

This is a boot/platform image model, not a general module registry.

## 2. HypX authentication is delegated to signed secure-world authority

Before launch QHEE:

1. looks up `qcom.tz.mssecapp`;
2. checks root-of-trust information for the supporting apps;
3. sends `HYP_IMG_AUTHENTICATE`;
4. only then sends `HYP_IMG_LAUNCH`.

The same code rejects supporting services whose root-of-trust is not Qualcomm signed:

- `MsSecApp is not QC signed`;
- `TPMApp is not QC signed`.

So HypX loading is not a host-controlled arbitrary-ELF facility.

## 3. The authenticating app is explicitly Microsoft/Hyper-V aware

The exact same-firmware `qcom.tz.mssecapp` image is:

`68821c12a1932cafa2328a8753780c1b0ef8d71e11d0eb37924a1d049892f8aa`

It contains:

- `MSSECAPP_IMAGEAUTH_ID`;
- Microsoft Authenticode/code-verification/root certificate material;
- `Printing hyperV stage logs below`;
- `HyperVStageEnded`.

This is direct platform evidence that the HypX authentication path participates in the Microsoft Hyper-V secure-launch stage.

## 4. Windows boot loader is Qualcomm-secure-launch aware

Installed Windows contains:

- `hvaa64.exe` — SHA-256 `e8822fd521685bdd6996bb42dd3755af4420147e4a4cee85852d887a013c4b44`;
- `hvloader.dll` — SHA-256 `6e5df7a8ea95ebd12feaecd230176b78d5d24ea1271d3db123c169df62abc531`.

`hvaa64.exe` identifies itself as Microsoft Hypervisor and contains the VTL0/VTL1 SMC arbitration machinery already relevant to the Windows oracle.

`hvloader.dll`:

- loads `hvaa64.exe`;
- exports `HvlLoadHypervisor`, `HvlPreloadHypervisor`, `HvlLaunchHypervisor`;
- imports Qualcomm/platform-specific boot helpers:
  - `BlArchQcSlSupported`;
  - `BlArchStartedInEL2`;
  - `BlArchGetEl2Regions`;
  - `BlSetVirtualizationLaunched`.

This tightly links the Windows Hyper-V boot path with the platform's secure-launch/EL2 handoff.

The exact HypX ELF shim itself is not separately installed as an ordinary Windows driver package. That distinction matters: `hvaa64.exe` is PE, while QHEE's HypX manager parses an ELF. HypX is therefore best described as the authenticated Qualcomm EL2 support/extension layer underneath or alongside the Microsoft hypervisor launch, not as `hvaa64.exe` itself.

## 5. HypX executes in the platform HYP context

QHEE's HypX path explicitly:

- creates `AC_VM_HYP`;
- maps HypX code/data;
- maps the HLOS partition for HypX;
- manages an `HLOS Permission Reduced Memory` list;
- handles HypX guest/sysreg/page-fault traps.

Thus HypX belongs to the platform HYP security context whose ownership rules were established in E004ck.

It is not a separate camera-capable owner identity that can simply be added beside CP_CAMERA.

## 6. Runtime Windows QcTrEE does not expose HypX launch

The exact QcTrEE `MssecService` implementation connects to `qcom.tz.mssecapp`, but its runtime service surface is limited to normal post-boot operations including:

- `MssecServiceInvoke`;
- `MssecServicePpi`;
- `MssecServiceShutdown`.

A decompilation/xref sweep contains no:

- `HYP_IMG_AUTHENTICATE`;
- `HYP_IMG_LAUNCH`;
- HypX loader;
- Hyper-V launch request.

So there is no installed Windows runtime API that could be mirrored on Linux to load our own HypX worker.

## 7. No separately installable HypX package exists on this Windows image

A same-machine scan of DriverStore/System32 found no textual HypX INF/manifest and no separately named:

- HypX ELF;
- HypX MBN;
- QHEE/HypX driver package;
- hypervisor-extension binary package.

That is consistent with HypX being firmware/boot-chain infrastructure rather than an OS-installable service.

## 8. Why a Windows one-shot was not used

E004cl initially reached an identity ambiguity and the existing one-shot procedure was verified:

- EFI `Boot0006` still exists as `Windows Direct Oracle Temp`;
- SP7 is available as the independent watcher;
- Golden remains the saved/default Linux path.

However, the static evidence then resolved the question that mattered: HypX authentication/launch exists only in the boot-time QHEE path, while post-boot QcTrEE does not expose it.

A normal Windows boot could confirm Hyper-V is running, but it would not turn the early authenticated HypX launch into a reusable runtime interface. Rebooting would therefore add risk without changing the architectural decision.

## Architectural consequence

HypX closes another tempting shortcut:

**we cannot put the Linux camera worker into HypX as if it were a loadable EL2 plugin.**

The mechanisms now divide cleanly:

- Microsoft Hyper-V/VTL1 — actual Windows trusted CPU habitat;
- Qualcomm HypX/QHEE — authenticated platform EL2 support/secure-launch layer;
- QcTrEE/QTEE — runtime secure-service transport;
- CP_CAMERA — camera device-domain write authority.

None provides an installable Linux camera worker on the current stack.

## Next gate

**E004cm — Gunyah/QHEE worker-VM ownership feasibility**, static first.

This is now the most promising source-available architecture because the same-machine QHEE image contains a full Gunyah resource manager and VM/memparcel machinery. Unlike pKVM, a Gunyah worker VM can potentially receive a real QHEE VMID and QHEE-managed SMMU/DMA isolation.

Determine whether a protected worker VM could satisfy the Windows contract without HLOS ownership:

1. inspect same-machine QHEE/Gunyah memory-parcel ACL semantics;
2. determine whether a guest VM can be a memory owner/share peer alongside CP_CAMERA;
3. establish whether CP_CAMERA may appear in a Gunyah/RM memory ACL or only in SCM assignment policy;
4. identify upstream Linux Gunyah host-driver support that could be ported into the SP11 kernel;
5. determine whether the worker VM can receive only CPU access while camera IFE retains CP_CAMERA write access;
6. reject the route if QHEE policy cannot express `{trusted guest, CP_CAMERA}` without HLOS.

No guest creation, memory parcel, HYP assignment or camera runtime is authorized by E004cm.
