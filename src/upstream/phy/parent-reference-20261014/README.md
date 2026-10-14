# Borrowed-parent PM reference release — source31

Generic PHY core keeps its child active while calling provider power_off.
Runtime core refuses parent suspend while children are active (-EBUSY).
Source30 attempted parent put_sync inside that callback and quarantined the
first real shutdown in07. Its error propagation and automatic recovery worked;
no same-boot retry/unload was attempted. Specific release step was not logged
in07; source inspection identifies the parent/child compatibility violation.

Use existing pm_runtime_put_noidle to release only the provider-owned count.
Generic PHY core then releases the child and requests final idle. This keeps
correct ownership without asking the parent to suspend prematurely. Real
OPP/performance/supply failures still propagate and retain resources/modules.
Added step labels make future faults attributable; register payloads, profile,
CAMSS30 and source29 DTB remain unchanged.

Actual provider, generic PHY on/off, runtime parent-admission and CAMSS stop
functions: GCC/Clang ASan/UBSan87 cases each. Includes the active-child EBUSY
reproducer, corrected complete release, acquisition/cleanup fault matrix,
reference consistency, retry barriers and restarts. Six compiled unsafe
mutations rejected. Exact one-file replay and102 parent pins preserved.
Scoped ARM64 PHY module W=1/-Werror zero warnings/errors, kernel26 ABI.
Checkpatch zero diagnostics. Source/model proof is separate from hardware.

prepare.py [FRESH_DIRECTORY] preserves immutable parent overlays and applies
only the pinned change; occupied identities refused. build-worker.py creates
fresh output and PHY module directories. Tests take source/fresh outputs.
Hardware reuses the exact07 diagnostic and repeats only the changed teardown
behavior on fresh08. Require all3 cycles, runtime suspend, baseline clock/rail
counts, clean unloading and complete final/return logs; no frames or OS sleep.
