# E002k-D-R3 source-integrated runtime preflight

Date: 2026-08-27

## Purpose

First runtime of the fully maintained-source camera integration while preserving the exact FullIO v19c kernel/audio environment.

## Runtime payload

Exact Golden Image:

`bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`

Golden base initrd:

`ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`

Reconciled maintained-source DTB:

`8cb5783fed2711758763aa81dc2f28c9f348259830ad6f57ffa18a6c5fd0d553`

Production OV13858 module:

`13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309`

- vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`
- srcversion: `9366B03E91F9212A1501AEC`
- 65 imports, 0 missing from Golden, 0 CRC mismatches

R3 initrd:

`dfcc8a0d53391b80ef418ff7b3c40df2ccbc0d8aeb43ffe6a8e7abb5aabf7e15`

Independent A/B builds are byte-identical. The initrd has exactly nine semantic changes relative to Golden: init-top ORDER + one R3 loader + isolated `mc`, `videodev`, `v4l2-async`, `v4l2-fwnode`, and production `ov13858` under `extra/e002k-d-r3`.

## Source identity

After correcting the source base, the integrated camera tree differs from `.golden-v33-repro/src` in exactly three source files: OV13858, Hamoa DTS and Denali DTS. No audio source differs.

## Safety gates

- running kernel must remain `7.1.5-sp11-render-parity-v4+` before arming;
- `saved_entry=sp11-audio-fullio-v19c`;
- no pre-existing `next_entry`;
- Golden Image/initrd/DTB hashes must remain unchanged;
- new boot directory and GRUB entry only;
- R3 is armed with `grub-reboot`, never made the saved default.

## Runtime acceptance

After one-shot boot:

1. prove the R3 marker and loader log;
2. prove Golden playback/capture/touch/Wi-Fi environment survived;
3. prove native PM8010-M + CAMCC + CCI0 + CAMSS + OV13858 bind;
4. stream 16 frames at the accepted 4076x2806 ~30 fps mode;
5. require the deterministic sensor test-pattern SHA-256 `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`;
6. stop stream and require clean power/runtime-PM teardown;
7. reboot/return to saved Golden after evidence collection.
