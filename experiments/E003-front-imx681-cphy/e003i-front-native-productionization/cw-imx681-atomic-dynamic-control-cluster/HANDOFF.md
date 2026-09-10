# CW handoff

CW converts CV's four IMX681 raw controls into a topology capable of one request-local group-held sensor transaction without reviving AL's pending-exposure clobber.

Core rule:

- one V4L2 cluster: VBLANK + exposure + analogue gain + digital gain;
- VBLANK is master;
- no `__v4l2_ctrl_modify_range()`;
- static exposure metadata max = sensor-wide hardware max;
- `try_ctrl` enforces `exposure <= even(FLL-4)` using pending cluster values;
- one successful cluster change -> one unchanged AM hardware transaction.

The AM transaction body is source-exact and was previously live-proven by AP. CW itself is offline only.

## Remaining gate

Do not call AV's two-frame delay an extra `request+2` optical offset. AW proves a sensor packet tagged request F is selected by KMD while current SOF is F-1 and explicitly warns that simply adding maxPipeline again can double-count scheduling.

Next: reconcile the AW KMD `F-1` apply selection, AV delay record, group-hold release and a concrete SOF/frame-boundary observation into one optical-effect label. Prefer static/retained evidence first. Only if that cannot close the latch edge should a single bounded live control transition be designed, with before/after frame evidence and Golden return.
