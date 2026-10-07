## 2026-10-07 native grouped frame-length response hardware PASS

Fresh control-timing02 source74fef62f/kernel audit30/libcamera build08 physically
passes128 standard cam2560x1440 NV12 frames and132 actual isolated IPA results.
Six complete sensor V4L2 control-cluster writes at SOF16/32/48/64/80/96 alternate
FLL7108/3554, exposure1000/analogue0/digital256 unchanged. Initial setup plus six
successful CCI transactions are uniquely bracketed by userspace ioctls.
All six measured receiver interval responses start at command SOF+2; plateaus
15.00266/30.00534/15.00279/30.00533/15.00276/30.00541fps. CCI duration2.336-3.186ms.
Restored baseline at96 and held30fps through STOP. No brightness input is used.

128 app/statistics/IPA pairs,133 retirements,665 owner checks,136 typed defaults,
clean STOP,error0,all sensors standby,neutral graph,no SOF after final STOP,
critical kernel faults0,Golden hashes unchanged. Returned Golden
 a2506d21-9074-4cf6-87c9-b3a0f13828e1. timing01/02 consumed and retired; all24
candidate IDs retired,28 completed sensor streams,48 candidate/Golden boots.
5 prestream/3 poststart qualification failures; latest failure was01 analysis
precision, with successful capture/control writes. Its FAILED evidence remains.
No test boot/unit/writer/firmware remains. Private pixels/tuning/logs stay SP11.

01 used an incorrect individual5% period criterion on IRQ arrival observations.
Corrected acceptance uses plateau mean3%,median5% and disjoint30/15fps onset bands;
real-trace checks plus CCI-error/missing-commit/no-response negative checks pass,
and fresh02 independently confirms all six SOF+2 responses. IRQ times include
arrival jitter and are not first-row sensor exposure timestamps.

NEXT: separately measure exposure,analogue and digital control response under
stable-light screening and repeated up/down changes,with CCI completion/frame/
statistics identity. Do not copy the observed FLL offset2 to other controls or
publish applied-frame metadata. Standard DelayedControls parameters remain
unqualified,automatic AE/AWB disabled,SensorTimestamp absent. Metering units and
AE targets,dynamic tables,rear processed ISP/focus,production ABI/clock policy,
independent tuning,soak/switch/fault and matched Windows quality acceptance remain.
No diagnosed brightness defect; match physical camera/scene/position/lighting/time
and record weather/light changes. User rainy/cloudy report persists; no matched
Windows reference. Earlier NEXT statements are history.
Evidence: docs/NATIVE-RGB-FRONT-CONTROL-TIMING-02-20261007.json; failed01 and analysis
qualification are retained alongside kernel audit30/libcamera build08 reports.

# Native front grouped frame-length timing

Fresh one-use control-timing02 uses audit30/libcamera build08 and standard cam.
The explicit frame-length-v1 development mode changes the normal four-member
sensor V4L2 cluster at receiver sequences16,32,48,64,80,96: FLL7108/3554 repeated
three times, with exposure1000/analogue0/digital256 fixed. It captures128 NV12
frames and paired actual isolated IPA statistics, recording CCI transaction
completion and actual receiver interval transitions. Baseline is restored at96.

Kernel tracing is opt-in/read-only; no new register addresses or DMA commands.
No automatic feedback or public applied-frame metadata is enabled. Derived timing
JSON may be committed; optical pixels/original tuning/private logs remain SP11.
Do not infer exposure/gain delays or quality from frame-length response. Standard
DelayedControls parameters still need measured per-field/frame associations.
The service returns Golden automatically; spent identity must be retired.

control-timing01 completed capture/control writes but failed an overly precise
per-interrupt timestamp criterion. Its FAILED evidence remains preserved and
identity retired. Fresh02 uses multi-interval rate acceptance and disjoint
30/15fps onset bands, with real-trace and negative-admission verification.
