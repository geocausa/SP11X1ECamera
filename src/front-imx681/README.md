# Front IMX681 stable source/runtime bundle

This tree is the stable, non-experiment-path form of the proven SP11 front RGB stack. HF froze the accepted source bundle; HG/HH made the IQ runtime relocatable and removed its proprietary/raw cache dependency; HI adds deterministic production userspace build, dynamic media-node discovery and a dry-run-by-default launcher.

It contains:

- `kernel/camss/`: the final R27 CAMSS authority;
- `kernel/imx681/`: the CW atomic clustered IMX681 driver and mode table;
- `userspace/runtime/`: frozen HC/native AEC/CQ/scheduler sources plus the HI production capture helper and write-policy gate;
- `userspace/iq/`: the clean R5..R27 IQ runtime, derived clean authority, and accepted template-free R4 bootstrap asset;
- `bin/front-imx681-discover.py`: dynamic sensor and `/dev` discovery while pinning the proven X1E pipeline entity route;
- `bin/front-imx681-launcher.py`: dry-run by default, with post-G3 writes defaulting to `shadow`;
- `build-userspace.sh`: deterministic production userspace build without camera access;
- `build-production.sh`: exact kernel/userspace production build. It now requires both the accepted Kbuild source frontend (`KERNEL_SOURCE`) and prepared output/header tree (`KERNEL_BUILD`), and fails closed unless CAMSS/IMX681 reproduce their accepted SHA-256 values.

The production launcher does not hard-code the IMX681 I2C bus, `/dev/videoN`, or sensor subdev number. The proven route identities remain pinned (`msm_csiphy2 -> msm_csid1 -> msm_vfe1_pix -> msm_vfe1_video3`) until a different route is separately proven.

`cap-release-one-shot` is not the default and requires explicit launcher acknowledgement. Bounded repeated-open robustness is proven through four sequential 27-frame production streams (HQ); production-native changed post-G3 feedback remains unproven. Each launcher invocation now defaults to a fresh timestamp/PID session directory, and `--execute` refuses an already-existing output directory so evidence cannot be silently overwritten or mixed between sessions.

E004dm adds the Windows-authoritative `CTrigleAdjV1` fallbacks that were deliberately missing from the earlier clean runtime: per-call visit-count/centroid resolution for oscillating triangle walks and the reachable two-vertex boundary projection path. The normal contained-triangle path remains bit-exact against EG/FA/FH/FW. Runtime producer evidence now records AWB selection mode and selector visit counts.

E004du promotes the live-tested SP11 front-IR CSIPHY0 D-PHY Windows receiver parity delta into this maintained CAMSS source. The legacy module parameter name `e004j_ir_dphy_windows_parity` is retained intentionally so the promoted source rebuild remains byte-identical to the module exercised by E004dp/E004dr/E004ds. The gate remains **false by default** and is scoped to X1E80100 + CSIPHY0 + D-PHY; rear CSIPHY1 and front RGB CSIPHY2 are unaffected. The canonical production build reproduces CAMSS SHA `862732b7...` and IMX681 SHA `ef57ed06...` exactly.

`PROVENANCE.json` remains the HF source-authority provenance record.
