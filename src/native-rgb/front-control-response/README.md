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
