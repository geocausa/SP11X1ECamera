# E003i DM — Windows internal CapExposure bounds

Base: 47f9691. Hypothesis: ordinary Windows PopulateOutput supplies finite request-local per-lane bounds to its internal CapExposure, explaining a stage absent from native CG/DJ.

Experiment: bounded normal front-camera Windows observation, logging same-request internal cap inputs, min/max records, branch inputs, and outputs. No injected exposure targets and no Windows configuration/driver changes. Use existing CDB and camera holder. SP11 Linux/Windows are the same physical device; PiMaster routes are mutually exclusive. Preserve the default Golden entry, boot Windows once, and return normally to Golden after archiving evidence.

Expected observation: seven limits with producer identity, cap call-before-publication order, and matching pre/post compact records. Keep raw logs/binaries outside Git. No Linux camera candidate or source behavior change is part of the oracle. If the needed state cannot be observed, record the precise gap and return to Golden.
