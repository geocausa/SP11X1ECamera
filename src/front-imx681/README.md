# Front IMX681 stable source/runtime bundle

This tree is the stable, non-experiment-path form of the proven SP11 front RGB stack. HF froze the accepted source bundle; HG/HH made the IQ runtime relocatable and removed its proprietary/raw cache dependency; HI adds deterministic production userspace build, dynamic media-node discovery and a dry-run-by-default launcher.

It contains:

- `kernel/camss/`: the final R27 CAMSS authority;
- `kernel/imx681/`: the CW atomic clustered IMX681 driver and mode table;
- `userspace/runtime/`: frozen HC/native AEC/CQ/scheduler sources plus the HI production capture helper and write-policy gate;
- `userspace/iq/`: the clean R5..R27 IQ runtime, derived clean authority, and accepted template-free R4 bootstrap asset;
- `bin/front-imx681-discover.py`: dynamic sensor and `/dev` discovery while pinning the proven X1E pipeline entity route;
- `bin/front-imx681-launcher.py`: dry-run by default, with post-G3 writes defaulting to `shadow`;
- `build-userspace.sh`: deterministic production userspace build without camera access.

The production launcher does not hard-code the IMX681 I2C bus, `/dev/videoN`, or sensor subdev number. The proven route identities remain pinned (`msm_csiphy2 -> msm_csid1 -> msm_vfe1_pix -> msm_vfe1_video3`) until a different route is separately proven.

`cap-release-one-shot` is not the default and requires explicit launcher acknowledgement. Repeated-stream live robustness and production-native changed post-G3 feedback are still unproven.

`PROVENANCE.json` remains the HF source-authority provenance record.
