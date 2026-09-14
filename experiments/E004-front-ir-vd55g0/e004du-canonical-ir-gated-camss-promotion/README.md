# E004du — canonical IR-gated CAMSS promotion

Status: **PASS / SOURCE PROMOTED / BYTE-EXACT REBUILD / NO NEW RUNTIME**.

E004k introduced the SP11 front-IR CSIPHY0 D-PHY Windows receiver parity delta behind module parameter `e004j_ir_dphy_windows_parity`. E004dp then exercised that exact module in the unified three-camera topology and obtained 96/96 Windows-exact receiver readbacks. E004dr and E004ds independently streamed the accepted rear and front RGB paths with the same gate armed and proved that it is not selected on rear CSIPHY1 or front RGB CSIPHY2.

E004du promotes that exact live-tested source delta into `src/front-imx681/kernel/camss/camss-csiphy-3ph-1-0.c`. The historical parameter name is intentionally retained to preserve byte identity with the runtime-tested module. The gate remains false by default and requires all of: X1E80100 CAMSS, CSIPHY instance 0, D-PHY mode, and explicit module-parameter enablement.

The promotion also closes a production-build provenance defect found while sealing the source. The previous `build-production.sh` entered the prepared output tree directly (`make -C KERNEL_BUILD`), which produced valid but byte-different CAMSS/IMX681 ELF files. The accepted binaries are reproduced when Kbuild is entered through the historical source frontend and the prepared build/header tree is supplied as `O=`. The production build now requires both `KERNEL_SOURCE` and `KERNEL_BUILD`, uses that exact invocation shape, and fails closed if any accepted artifact hash drifts.

With:

- `KERNEL_SOURCE=/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src`
- `KERNEL_BUILD=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826`

canonical `build-production.sh` reproduces:

- CAMSS `862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7`;
- IMX681 `ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6`;
- front capture `70f407f5fd70e6657f9647a33eecde744ac9e1bd19fa9e901a4faf52508e354d`;
- bootstrap controls `4721ff6510d806ed63ffcb70d9a88441220047ef734ca760cc40bdc5719cd7ce`.

No new camera boot or stream is needed for this source promotion because the canonical CAMSS output is byte-for-byte identical to the module already exercised by E004dp/E004dr/E004ds. Linux SecureISP remains unauthorized and untouched.
