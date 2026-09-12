# E003i-HR — production repeated-open lifecycle handoff

Status: **PASS / offline only**.

HQ proves four sequential production opens/closes in one boot after the HN generation-reset fix. HR turns that bounded live result into a safer production launcher contract without changing any kernel module or capture/bootstrap binary.

The production launcher now treats each invocation as a distinct evidence/session owner: omitting `--output-dir` produces a fresh timestamp+PID directory under `/var/tmp/sp11-front-imx681`, while `--execute` rejects any already-existing output path. Dry-run planning creates no output directory. This prevents later opens from silently overwriting or mixing an earlier session's QC10C/stats/IQ evidence.

Two independent production builds remain byte-identical to HN. Package staging is deterministic, the staged launcher reproduces unique session paths outside the source workspace, default post-G3 policy remains `shadow`, and no camera node is opened by the offline handoff verifier.

Bounded repeated-open/close robustness is proven through HQ's four streams / 108 frames. Indefinite soak and production-native changed post-G3 feedback remain unproven.
