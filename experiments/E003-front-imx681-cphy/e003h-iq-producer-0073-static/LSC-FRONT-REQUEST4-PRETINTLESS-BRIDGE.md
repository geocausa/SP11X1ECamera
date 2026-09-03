# E003h 0073 — verified-front request4 pre-Tintless bridge

Status: **accepted offline/native Surface replay checkpoint**. No Linux camera runtime or Linux request6 is performed or authorized.

## Result

Verified-front request4 can now be reconstructed deterministically from its captured request-local trigger state through the exact input presented to the Tintless stage.

The chain is:

`front request4 generic triggers -> rear/default LSC41 interpolation -> rear/default golden + rear runtime calibration payload -> native Surface geometry resampler -> front pre-Tintless 4x221 mesh`.

No historical rear TINTCTX state and no request4 correction-table snapshot is used in this derivation.

## Exact request4 trigger path

Machine-code-pinned `SetupGenericTrigger` maps:

- vector[0] = `ISPInputData+0x20b8` = AEC lux index = `355.14508056640625`;
- vector[6] = `ISPInputData+0x20c8` = CCT = `4712.0`.

Request4 therefore crosses two rear/default LSC41 interpolation gaps:

1. CCT `4200 -> 4800`: region `0x29e -> 0x2a0`, float32 ratio `0.8533333539962769`;
2. lux `340 -> 430`: that lower result -> region `0x2a4`, float32 ratio `0.16827867925167084`.

The exact generated request4 pre-calibration payload is:

`x22 SHA256 = 99bf4e1dd6d500aa81cdb4f6e0f6e0b1f23bb953748be84ff451f6a71fe3d84f`.

Applying the proven rear/default golden plus the exact rear runtime calibration slot produces:

`x23 SHA256 = a24bba7c3d9cd6db545f65801006defd154f2da412bb101805cf9b45e23dfcde`.

## Active front geometry/Tintless ordering

Request4 `LSC_COMMON` is SHA `646e62de0d5192129ba03bcc285cc5928c231ab24bf1d83ed236513c59c20535` and contains:

- full: `4048x3152`;
- output: `3840x2160`;
- crop offset: `(104,496)`;
- scale: `1`;
- Tintless enable `common+0xc0 = 1`;
- branch selector `common+0x108 = 0`.

Exact DeviceMFT code around RVA `0x9b4c68` branches on `common+0x108`. For value 0 the active path at `0x9b4d54` calls geometry resampling first and then invokes Tintless. Therefore the correct verified-front ordering for request4 is:

`calibrated x23 -> geometry resample -> Tintless`.

## Native Surface resampler

The proof maps the exact SHA-pinned ARM64 `QcDeviceMFT8380.dll` under Unicorn and executes Surface resampler RVA `0x9b6048` directly. No Python reimplementation is accepted for the parity verdict.

The resulting four 221-float channel hashes are:

- channel0: `d0b36a767d3aadb35ec8b6ead29d97f67a11575d43a7d945e455fc5148b995a8`;
- channel1: `c6cdd5199db09233dce2bef205521041f4fa5e69f1b399705d26d4d7e62b2e28`;
- channel2: `c6cdd5199db09233dce2bef205521041f4fa5e69f1b399705d26d4d7e62b2e28`;
- channel3: `20f2ef9db2c811a983f1a31fdbb38c222de8a205fdba26474e6a3995bff6b9f2`.

The concatenated 0xdd0-byte pre-Tintless mesh is:

`SHA256 = 839cae7d7b1c884b77068f0cb76d6ce34fbed562ac1328a59ea4373a30ab88c9`.

The two green output planes remain byte-identical.

## Correction-table timing correction

The old `REQ4_LSC_CAL0..3.bin` snapshots must **not** be treated as request4 final Tintless ratios against `REQ4_LSC_STAGING.bin`.

The original capture plan proves the timing split:

- correction buffers were dumped at `IQInterface::LSC411CalculateSetting` **entry**, so they are pre-request adaptive state;
- staging was dumped later at caller RVA `0xa03b34`, after the request calculation completed.

That is why dividing post-request staging by those entry snapshots produced a false contradiction. The files remain useful as pre-request state evidence, but not as same-frame output/base ratios.

## Remaining front gate

The front-specific missing bridge is now narrower:

`pre-Tintless SHA 839cae7d... -> sequential verified-front Tintless config/stats/state -> captured front staging`.

A future or recovered front capsule should hook `TintlessAlgorithmWrapper::Process` at RVA `0xc95fd0`, capture the proven bounded config/stats/input/output meshes and persistent state from stream creation through the target request, and require native ARM64 replay. The historical TINTCTX state is rear OV13858 mode1 and remains invalid for satisfying this front gate.

Proof artifacts:

- `prove-lsc-front-request4-pretintless-bridge.py`
- `lsc-front-request4-pretintless-bridge-oracle.json`
