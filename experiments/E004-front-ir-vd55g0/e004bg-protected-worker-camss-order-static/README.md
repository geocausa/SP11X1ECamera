# E004bg — protected-worker to CAMSS lifecycle order map

## Result

**PASS: Windows' protected-worker lifecycle maps naturally onto Linux X1E VFE/CSID on START, but mainline CAMSS STOP order is the opposite of Windows and therefore needs a secure-mode-specific ordering path.**

This is an integration-order checkpoint only. Windows is the parity authority; static analysis is used only to expose the internals of Windows task 2/3 after E004bf dynamically established where those tasks sit relative to lane protection.

No Linux secure-camera runtime occurred.

## Windows authority

E004bf dynamically established the outer invariant:

- protect the IR lanes first;
- then execute protected-worker START;
- on teardown, execute protected-worker STOP first;
- then unprotect the lanes.

The accepted Windows trace also proved the exact protected lane mask is 0x8.

## Windows protected-worker internals

Static fallback is necessary here because the accepted runtime trace identifies task 2/3 boundaries but does not expose every internal trustlet virtual call.

Task 2 reaches the secure ISP hardware-manager START command. Its internal order is:

1. start each active IFE;
2. replay retained initial configuration packets to IFE, optional SFE and CSID;
3. start each active CSID.

Task 3 reaches the secure ISP hardware-manager STOP command. Its internal order is:

1. stop each active CSID;
2. stop the corresponding active IFE.

Prior parity checkpoints map the Windows protected IFE-Lite and CSID-Lite blocks to Linux's X1E VFE680 and CSID680 register families.

## Linux CAMSS order

For X1E's no-ISPIF graph, CAMSS links:

sensor -> CSIPHY -> CSID -> VFE -> video

The current video streaming code begins at the video entity, walks sink links upstream, and immediately calls each subdevice's s_stream callback.

That gives the ordinary Linux start order:

VFE -> CSID -> CSIPHY -> sensor

The stop routine walks the graph in the same direction, giving:

VFE -> CSID -> CSIPHY -> sensor

## Parity comparison

START is directionally compatible for the protected processing blocks:

Windows worker: IFE -> CSID  
Linux CAMSS: VFE -> CSID -> ...

Because Windows already established lane protection before protected-worker START, placing the secure-lane call only inside Linux's CSIPHY s_stream callback would be too late: VFE and CSID would already have been started.

STOP is more important:

Windows worker: CSID -> IFE  
Linux CAMSS: VFE -> CSID -> ...

So strict Windows parity cannot use the unmodified normal CAMSS stop walk for the protected VFE/CSID pair.

## Integration consequence

A parity candidate should be designed around a pipeline-level secure bracket, not a CSIPHY-local toggle:

- establish protected ownership before the first protected VFE/CSID start;
- preserve the ordinary VFE -> CSID start direction unless later Windows evidence contradicts it;
- stop protected CSID before protected VFE;
- release lane protection only after the protected worker-equivalent has fully stopped;
- provide rollback in the same ownership order if any protected start stage fails.

This checkpoint does not select the exact production code hook yet.

## Deliberately unresolved

The exact physical CSIPHY register image at the instant Windows changes lane protection remains unobserved.

Therefore E004bg does not claim whether physical CSIPHY programming belongs before or after the protection call. That uncertainty is carried forward instead of being replaced with a Linux-derived guess.

## Evidence

- `evidence/WINDOWS-PROTECTED-WORKER.txt`
- `evidence/LINUX-CAMSS-STREAM-WALK.txt`
- `evidence/ORDER-DERIVATION.txt`
- E004bf Windows dynamic outer lifecycle authority
- E004ay/E004az protected IFE-Lite/CSID-Lite to Linux VFE680/CSID680 parity maps

## Safety boundary

No secure SCM call was made from Linux. No camera-domain memory ownership changed. No QCOMTEE driver was loaded. No kernel or CAMSS source was modified by E004bg.

## Next gate

Return to the Windows oracle for protected-buffer ownership: determine which buffers Windows makes camera-domain-owned, when that ownership is established relative to DeviceStart, and when it is released. Use static trustlet analysis only for portions that cannot be observed dynamically.
