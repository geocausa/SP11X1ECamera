# Camera IF — unified production handoff + same-boot reset analysis

Status: **PASS offline analysis / no camera runtime**.

ID and IE now prove the accepted rear OV13858 path and the HY-equivalent front IMX681 production path separately under the same IB unified DTB and module authority. IF asks whether that is enough to authorize same-boot camera switching or production-default promotion.

It is not enough yet. Front repeated-open robustness is strong: HO passed two streams, HQ passed four streams / 108 frames with generation 1 on every stream, and HR closed the production repeated-open handoff. Current source also resets TLBG/3A snapshot generations on open/close and clears front CSID software epoch/buffer counters during CSID reset.

The remaining handoff gap is route ownership, especially around cross-camera switching. The accepted rear helper explicitly enables the two rear mutable links and never disables them. The production front launcher likewise enables the two front mutable links and never disables them. Media links are persistent configuration, not stream-local state. A production switch must therefore pass through a verified neutral topology rather than assuming STREAMOFF or file close removes route ownership.

IF defines the safe same-boot transaction:

1. Finish STREAMOFF and close the source camera.
2. Require no camera process/file owner and require the source sensor runtime-suspended where observable.
3. Explicitly disable both mutable links of the source route.
4. Verify a neutral state: all four mutable rear/front route links disabled.
5. Only then enable the two mutable links of the target route and verify target-only state.
6. Start exactly one bounded target stream.
7. Any failure after candidate consumption is terminal for that boot; no retry.
8. Golden return/archive/retirement remain mandatory.

The first live direction should be rear -> neutral -> front because ID gives the accepted rear starting contract and the front repeated-open/reset path is already the stronger side. A second independent one-shot must later prove front -> neutral -> rear. Whole-stack production/default promotion remains blocked until both directions pass.
