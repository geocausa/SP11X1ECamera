# CW static/offline proof

## Problem inherited from AM

AM correctly fixed AL's exposure-clobber bug by making VBLANK standalone and clustering only exposure/analogue/digital gain. That is safe for pre-stream caching and was live-proven by AN/AP. It is not a one-callback live tuple when VBLANK and exposure both change: the two masters can each invoke `imx681_apply_request_controls()` while powered.

## Atomic topology

CW uses one contiguous four-control cluster rooted at `vblank` and removes `__v4l2_ctrl_modify_range()` from the driver. `imx681_try_ctrl()` computes:

`FLL = 2160 + pending_vblank`

`maxExposure = even(FLL - 4)`

and returns `-ERANGE` when `pending_exposure > maxExposure`.

The standalone exposure metadata maximum is `even(0x00ffffff - 4)`, so ordinary V4L2 scalar validation cannot reject a valid simultaneous FLL increase before cross-control validation runs.

## Linux 7.1.5 control-core ordering

The exact Golden source establishes:

1. `try_set_ext_ctrls_common()` links controls by master and performs `user_to_new()` for all supplied controls of the cluster before `try_or_set_cluster()`.
2. `try_or_set_cluster()` fills only omitted peers with `cur_to_new()`.
3. It calls `try_ctrl` before checking/issuing `s_ctrl`.
4. On change, exactly one master `s_ctrl` is issued for the cluster.
5. `new_to_cur()` occurs only after successful `s_ctrl`.

The constructor path initializes `p_cur`, copies current to new and registers the control; it does not call `try_ctrl`. CW therefore cannot dereference the exposure peer until after all four controls exist and have been clustered.

## AL regression exclusion

The exact Linux `__v4l2_ctrl_modify_range()` still contains `cur_to_new(ctrl)`, proving the historical mechanism remains real. CW contains no call to that helper, so there is no callback-time path that can replace the pending exposure with its old current value.

## AM write-body preservation

`imx681_apply_request_controls()` is compared as exact source text between AM and CW. Its sequence is unchanged:

1. group hold on;
2. FLL;
3. even coarse exposure;
4. analogue gain;
5. global digital gain;
6. unconditional group-hold release.

AP's retained live result proves the AM instance of this exact function reached `ret=0` on SP11. CW transfers only its unchanged body; it does not claim a new live execution.

## CV / Windows differential

All four CV deterministic control tuples satisfy the new containment rule. Their FLL/coarse/AG/DG values are expanded with the retained Windows IMX681 `FillExposureSettings` oracle and reproduce its exact 10 dynamic byte writes. A deterministic 50,000-case model exercises both accepted and rejected FLL/exposure combinations, with explicit boundary checks around `FLL-4`.

## Build / safety

The copied candidate builds with `W=1` against `/02-kernel/build-runtime-v4-headers-20260826`, with Golden vermagic and zero warnings. No module load or camera runtime is part of CW.
