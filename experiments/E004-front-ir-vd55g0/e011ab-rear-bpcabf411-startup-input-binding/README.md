# E011AB — rear BPCABF411 startup input binding

Status: FIRST RUN HEALTHY CAMERA / INCONCLUSIVE OBSERVER; CORRECTED FRESH RUN PREPARED.

Parent: 1a0470aa3a47cc153857f2007dd8eb082f85eead.

Hypothesis: the first two BPC common calculations form cold/request-1 states followed by request-2/3 holds. Observe rather than assume the schedule. Capture the first eight common inputs (107-float region, six-word runtime reserve, bounded dependence) and packer common outputs together with 16 atomic request hooks. Validate the selected E011AA semantic terms against each live common output. Runtime reserve mapping and full packet binding are separate claims.

Pinned DeviceMFT SHA: c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35. Request/common/packer RVAs: 0x746f18/0x9c16b0/0xb41090. Packer common pointer is x1+0x10. Maximum 16 request hooks and eight hits per common/packer boundary; no writes to camera configuration or target data.

Fresh candidate identity: E011AB-20260929-2100B. holder.ps1 atomically consumes its identity at entry before camera enumeration, gates enumeration/initialization/start, requires rear Color VideoRecord NV12 3840x2160, and automatically stops acquisition after 30 seconds. A sign-in session task must be manual-only and removed after completion. The observer attaches to the existing FrameServer process before initialization.

Checkpoint these sources before one-shot Windows. Preserve Linux-first EFI BootOrder and saved FullIO v19c. Normal Windows reboot returns to Golden. No Linux camera/module/MMIO/DMI/RT-CDM execution is authorized by this stage; native rear VFE1 WM16 retirement gate remains open.

Raw captures, addresses and transcript stay private on SP11. Commit only own sources and aggregate validation. Any possibly started candidate is consumed; no same-boot retry.

First identity E011AB-20260929-2045A delivered 711 valid 4K handles and clean Start/Stop, but bare module-offset deferred breakpoints did not bind: zero captures, no semantic proof. Its task was removed and SP11 returned to Golden before preparing candidate B. Correction: attach before PREINIT, set `sxe ld:QcDeviceMFT8380.dll`, release PREINIT, stop at actual module load, then execute the observer with resolved `bp` addresses before resuming initialization. Verify `bl` has concrete addresses before START.GO. Do not infer later request labels from a hook stopped at eight: observe 16 requests for the eight producer samples.
