# Standalone PHY owned-resource port — candidate30

Reuses explicit acquired-reference flags, reverse release and safe fault retention from the retained sensor/native source. AUDIT.json records the prior-source/history decision. Four files change: PHY core/header, CAMSS typed PHY stop return, and owned-stage fatal cleanup reporting. PHY lane/register tables, graph and timing profiles are unchanged.

Supply references are enabled individually and tracked as an acquired prefix. PM, scaled-domain votes, OPP, clocks, lanes and IRQ ownership are recorded only after successful acquisition. One shared release helper unwinds the resources actually owned; a release failure preserves remaining ownership and permanently pins the provider module until reboot. A failed runtime-PM put consumed its usage count, so get_noresume restores that owned count before quarantine. Generic PHY core already preserves power_count/its own runtime reference when provider shutdown returns a negative error; CAMSS now propagates that result.

Clean failed start preserves its primary error. A cleanup failure logs both primary and cleanup codes and returns EUCLEAN: the retained CAMSS lifecycle treats that as retained failed-stage ownership and holds graph, PM, module and independent DMA-SG leases before VB2 cancels. No recovery or manual driver unbind is qualified; fault exit is machine reboot. Electrical failures hidden by void APIs, physical clock/rail measurements and real IRQ concurrency are outside hosted proof.

## Qualification

- Actual provider header/functions plus actual generic PHY core and CAMSS stop functions: GCC/Clang ASan/UBSan,94 cases each. Acquisition failure matrix, cleanup faults, PM-count restoration, reference consistency, generic core retention, fault retry/configuration barriers and C-PHY/D-PHY clean restarts.
- Reused actual CAMSS/VB2 body integration model extended with fatal failed-start cleanup:51 cases per compiler, including DMA/graph/power retention before forced cancellation.
- Five unsafe ownership/propagation mutations compile and are rejected.
- Exact four-file patch replay,102 parent pins preserved, checkpatch zero errors/warnings.
- Scoped native ARM64 PHY and CAMSS modules W=1/-Werror, kernel26 ABI, zero warnings/errors. Full kernel30 not built. Source/module proof is separate from hardware power-cycle/streaming proof.

Initial duplicate declaration from the preparation extractor, and test extractor/fixture errors, are retained in qualification01/02 logs. Corrected source/templates and module02 are pinned. Kernel register programming is unchanged by these corrections.

## Reproduction

prepare.py [FRESH_DIRECTORY] refuses an occupied identity, links immutable parent branches, detaches changed files, and applies the pinned patch with zero fuzz/offset. Default qualification identity is already occupied. Avoid changing or deleting the retained source29 parent: its pins and links are explicit dependencies. build-worker.py ATTEMPT uses fresh output/module directories and MO; all build outputs remain outside source. Tests take SOURCE and FRESH_OUTPUT. The original source29 sensor-owned TOP domain remains hardware-qualified.

The next bounded hardware gate is standalone PHY2 configuration and three power cycles with sensor off and no CAMSS streaming/buffers. Then qualify the standard RAW lifecycle separately. No camera firmware, proprietary calibration/tuning, pixels or OS sleep are involved.
