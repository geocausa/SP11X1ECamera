# E003i CJ — Windows AEC source-S1 history provenance

Status: **PASS (static/offline)**.

CJ removes an ambiguity left by CI: the `sourceExposure[S1]` used by the ordinary Frame/Safe/Short/Long analyzers is not an unrelated current-request exposure input. Windows materializes the AnalyzerManager's seven-double source vector from a retained AEC history record before analyzer execution, and lane 3 is the retained S1 exposure.

Exact path:

`mode-selected retained history S1 qword @ +0xa0 -> UCVTF d64 -> AnalyzerManager state+0x38 -> sourceType S1 lane3 -> CAnalyzer::RunAnalyzer SI publication`.

The history record is selected with the byte at `ModeInfo+0x8ec`. CJ intentionally leaves that selector's normal-preview constant value unresolved rather than conflating it with convergence's separately proven hard-coded F-1 lookup.

This checkpoint is static/offline only. It performs no camera stream, module load, sensor write, MMIO, reboot, or Windows mutation.
