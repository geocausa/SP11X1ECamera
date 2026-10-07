## 2026-10-07 exposure response/readback hardware proven; gains still ambiguous

Fresh response02 source9c648fd8/kernel audit31/libcamera build09 passes320 standard
cam2560x1440 NV12 frames at30.00003fps,324 actual isolated IPA results,1625 owner
checks/325 retirements,18 grouped sensor ioctls and328 typed defaults. All19 reads
of known FLL/exposure/analogue/digital registers match commanded values,error0.
CCI write completion alone is no longer the only actuation evidence. Readback
confirms retained register values,not their optical pixel effect.

Exposure1000/2000 changes show six sharp,repeatable statistics and processed-Y
responses at command SOF+2,with stable restored baselines and unchanged receiver/
video source observations. Same offset seen in response01 retrospectively after
removing unsupported15%-of-absolute-luma threshold. Metering units/zero point are
unqualified; use response above measured noise,8 analyzer tests pass. Fresh02
qualifies exposure's empirical response delay2. First-row exposure timestamp is
still unproven. Analogue0/512 and digital256/512 writes/readbacks succeed but
responses remain ambiguous; no gain delay accepted,no copied delay2.

Both01/02 captured640 app frames/648 IPA results overall. All STOPs clean,error0,
sensors standby,graph neutral,no SOF after final STOP,critical0,Golden unchanged.
02 UTC capture17:29:35.803..17:29:47.897 on2026-10-07; current Golden
8dffb0ec-59fd-4ca5-8103-34b098d5cd21. Both response IDs consumed/retired; all26
candidate IDs retired,30 completed sensor streams,52 candidate/Golden boots.
Failure counters5 prestream/3 poststart qualification failures unchanged; response
capture PASS and unqualified gain timing are intentionally separate. No candidate
boot/unit/writer/FW remains. dc9ca301 GitHub sync issue is resolved.

NEXT isolate analogue/digital gain response in the already-proven native front
RAW path,using bounded baseline/raised/restored plateaus and known-register reads,
then compare hardware statistics/processed output and matched Windows same scene/
lighting/timestamps. Do not repeat the same ambiguous ISP experiment or infer a
brightness defect from low Y. Metering interpretation and physical illumination
remain unresolved. RAW work is a diagnostic,not a CPU image ISP or release path.
Automatic AE/AWB/DelayedControls still disabled/unqualified; SensorTimestamp absent.
Rear ISP/focus,dynamic tables,production ABI/clock policy,independent tuning,
soak/switch/fault and Windows optical acceptance remain. Earlier NEXT is history.
Evidence: docs/NATIVE-RGB-FRONT-CONTROL-RESPONSE-01/02-20261007.json,analysis
correction,readback audit31 and libcamera build09. Originals/pixels/logs private SP11.

# Native front exposure and gain response

Fresh response01 captures320 frames through standard cam/isolated real IPA.
Build09 explicitly enables exposure-gain-v1; audit30 observes CCI group release.
At SOF16..288,18 four-member clustered writes test exposure1000/2000,analogue
0/512,digital256/512 one field at a time,three up/down cycles per field. FLL3554
stays fixed; every second change restores baseline. Capture includes a final
baseline tail. No automatic controls or exposure timestamp publication.

Capture/queue/STOP acceptance is separate from per-field timing qualification.
Analyzer requires sharp consistent statistics transitions,processed-output
corroboration,repeated restored baseline and unchanged receiver/video association.
Lighting screening is statistical,not an instrumented light reference. Ambiguous
response remains unqualified. No absolute metering units or Windows optical parity
is inferred. Private pixels/logs/tuning remain SP11; derived facts may be Git.
One-use assets/identity are consumed once and retired; automatic Golden return.
