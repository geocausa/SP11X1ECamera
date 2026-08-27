# E002k-D full isolated build / camera ABI gate

Date: 2026-08-27

## Full build

The exact-runtime-config isolated build completed successfully:

- kernelrelease: `7.1.5-sp11-render-parity-v4+`
- `Image`: 51,341,824 bytes
- `Image` SHA-256: `f47abe74f619e899cc4c34e65c37521954f732cfd13c9a01731d34a2fd1d4b49`
- no `error:` diagnostics in the complete build log
- OV13858, Qualcomm CAMSS and Qualcomm CCI all compiled and linked successfully

Target module hashes:

- `ov13858.ko`: `13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309`
- `qcom-camss.ko`: `7df7e08ddf6f8985bb4469346e64f61bc17ecab5cff7a7da9c967de7a950db66`
- `i2c-qcom-cci.ko`: `ea90f4136d64492d58d9df121fed1ba54e02729d631067d8551776a104f4d145`

All three have exact Golden vermagic:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

## Module.symvers classification

Fresh `Module.symvers` contains 31,801 symbols; the installed Golden table contains 31,794.

Comparison:

- Golden symbols missing from fresh: **0**
- extra fresh symbols: **7**
- common-symbol CRC differences: **29**
- provider/module-name differences: **0**

All 7 extra exports are audio-only:

- `lpass_macro_dmic_clk_request`
- `lpass_macro_register_dmic_clk_provider`
- `lpass_macro_unregister_dmic_clk_provider`
- `lpass_tx_macro_sp11_ep16_endpoint`
- `q6apm_get_push_hw_pointer`
- `q6apm_graph_configure_push`
- `q6apm_graph_is_push_mode`

All 29 changed CRCs are likewise exports from `sound/soc/qcom/qdsp6/snd-q6apm`. No camera, CCI, CAMSS, clock, regulator, media-core or V4L2 provider CRC differs.

## Camera import CRC gate

Each fresh target module's embedded modversion requirements were mechanically checked against the installed Golden `Module.symvers`:

- OV13858: 65 imports, 0 missing, 0 CRC mismatches
- CAMSS: 140 imports, 0 missing, 0 CRC mismatches
- CCI: 46 imports, 0 missing, 0 CRC mismatches

`CAMERA_IMPORT_CRC_GATE=PASS`

Neither CAMSS, CCI nor OV13858 imports any of the changed/new audio symbols.

The unchanged CAMSS and CCI modules also reproduce the installed Golden modules' complete import/modversion maps exactly. Their source versions match Golden exactly:

- CAMSS: `7FA30D4F4B8441472FBD74C`
- CCI: `C8F30C93DFF513D2E8C9E42`

OV13858 intentionally has a new source version (`9366B03E91F9212A1501AEC`) because E002k-D changes that driver; Golden OV13858 is `37BA92DF5373E083134987D`.

## Acceptance

The full build and camera ABI gate are **PASS**.

The audio-only `Module.symvers` differences are historical source/runtime-kitchen differences and are not consumed by the camera path. They do not justify replacing Golden audio modules in the integrated camera candidate.

Next: apply the already-accepted v19c source Kitchen reconciliation to the isolated source, then package the production-integration candidate under a separate kernel release/module tree and a one-shot GRUB entry. Golden remains the saved default and must not be overwritten.
