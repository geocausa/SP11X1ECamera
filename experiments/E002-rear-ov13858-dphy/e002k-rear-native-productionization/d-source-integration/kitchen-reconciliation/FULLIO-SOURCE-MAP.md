# FullIO v19c source reconstruction map

The exact deployed v19c DTB adds three sound-node semantics beyond the maintained Denali source:

1. model: `X1E80100-Microsoft-Surface-Pro-11-FullIO-v19c0`;
2. routes: add `TX DMIC0 -> vdd-micb` and `TX DMIC1 -> vdd-micb`;
3. `TX DMIC Capture` DAI link:
   - codec: `&lpass_txmacro 0` (deployed phandle 0xe3);
   - cpu: `&q6apmbedai TX_CODEC_DMA_TX_3` (deployed phandle 0x1c7 + ID 120/0x78);
   - platform: `&q6apm` (deployed phandle 0x1c8).

`TX_CODEC_DMA_TX_3` is defined as 120 in `include/dt-bindings/sound/qcom,q6dsp-lpass-ports.h`.

This map reconstructs the deployed numeric DTB semantics using maintained source labels; no decompiled phandle numbers are carried into source.
