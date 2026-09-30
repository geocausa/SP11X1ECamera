# E011AU — bgStatsConfigV1 retained-BG initialization writer

Status: LIVE NAMED-CONFIGURATION LINEAGE PASS; INDEPENDENT PROFILE MATERIALIZATION OPEN.

Fresh Run B completed one original Windows rear Color VideoRecord NV12 3840x2160 Start/Stop, 713 valid4K frame handles and a clean Stop. CDB attached to a newly started FrameServer host immediately before enumeration/initialization; the two holder gates were released in the same operation, 0.130029 seconds after debugger readiness. A module-load event held the actual original DeviceMFT before the create-call probe was armed. Three code ranges match the pinned original image exactly.

The earlier timing assumption was corrected: CreateAWBAlgorithm/configuration ran during StartAsync after InitializeAsync completed. Three one-shot events at create-call682224, lookup-return687E48 and post-population688434 have matching thread and actor identity. All92 retained BG bytes remain identical from create-call to lookup return, with quad0. The selected named bgStatsConfigV1 record remains identical across96 bytes before/after population, has quad1 at source+20, and the retained actor has1 at+FB798 afterwards. Static original code identifies store688290 within parser686A50..688848. This is a bracketed, source-identified write, not a data-watchpoint trap on the exact store.

Nine private records/716 bytes and original code hashes pass validate-private.py. Only derived evidence enters Git. Captured records must not become producer inputs, and quad1 must not be hardcoded. Independent reproducible profile selection/materialization is still required.

Run A never released START.GO and is inconclusive: both manually started idle hosts terminated/replaced before the real DeviceMFT initialized. Both A debuggers detached/exited0; task stopped/removed; Golden returned before fresh B. The prepared original generator and A identity are historical; do not reuse them.

B CDB detached/exited0; manual-only task removed. Normal reboot returned Golden7.1.5-sp11-render-parity-v4+, boot25999320-3114-4f2c-bbce-a6335b0e2046, saved FullIOv19c, empty next_entry, NTFS unmounted and camera idle. Kernel, DTB and initrd hashes are unchanged. No kernel debugging, BCD changes, Linux camera activation, production provider changes or native rear runtime occurred.

Next: independently derive the selected named configuration profile, independent AEC cold-weight policy and RS count/offset authority, then final full deterministic startup/preflight and independent WM16 generation/IRQ/IOVA/DMA/IOMMU retirement proof. Native rear Linux ISP stays denied.

See RESULT.json, VALIDATION-SAFE.json, RUN-A-SAFE.json, PREPARE-B-SAFE.json and PRE-RUNTIME-SAFE.json.
