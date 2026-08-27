# E002c-r1 preflight — packaging-only correction

Status: PREPARED / NOT YET BOOTED

## r0 evidence

E002c r0 proved the camera-facing design is correct when loaded after full kernel initialization:

- accepted RPMh provider binds;
- patched native `ov13858.ko` binds to `1-0010`;
- native upstream 24-bit identity succeeds;
- dmesg logs `SP11 E002c PASS: native OV13858 identity verified`;
- runtime PM becomes `suspended`, usage `0`;
- all four rails disable;
- MCLK1 returns to enable count 0 at 19.2 MHz;
- reset returns asserted;
- no CSI endpoint and no stream;
- system health remains good.

r0 automatic loading failed before any electrical action because its CPIO layer emitted `.../extra/e002c/` without first emitting the absent Golden parent directory `.../extra/`. The initrd script also lost the true `insmod` failure code while logging it.

## r1 changes — packaging only

There are **zero** changes to:

- kernel;
- DTB;
- patched OV13858 source or module;
- RPMh provider module;
- V4L2 dependency module bytes;
- power sequence;
- rails/voltages;
- GPIO97 MCLK pinctrl;
- MCLK rate;
- GPIO110 reset;
- CCI controller/master/rate/address;
- native identity transaction;
- V4L2 registration logic;
- absence of CSI endpoint;
- stream behavior.

r1 changes only the initrd builder/loader:

1. explicitly emits `usr/lib/modules/7.1.5-sp11-render-parity-v4+/extra/` before `extra/e002c/`;
2. captures the actual `insmod` return code immediately before logging it.

## Fixed hashes

Kernel SHA-256:

`bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`

DTB SHA-256 (unchanged from r0):

`721ba8473e9b1c6ea6328fe43a3397d795d81f696402ab32c1067d5502c23d83`

Patched native OV13858 module SHA-256 (unchanged):

`35c99b50106265449e18e633851b6653268382e59d7e7a3ce938cf7d0135b148`

RPMh provider SHA-256 (unchanged):

`ac9269cd4be0842cb5dd3eeef9ccc2dc95100c86b59e57d83b3d86c8f5178ace`

Golden initrd SHA-256:

`ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`

r0 candidate initrd SHA-256:

`48e092c4e038a95ef51d683fb10ee78d515341338082e46337a9d8f92047a035`

r1 candidate initrd SHA-256:

`d1e56f66b742e33f980748a66e4184e92ba1b7e0cb4f7a1844471b5fb7ffe344`

Independent r1 build A/B are byte-identical.

`INITRD-R1-DELTA.txt` records exactly ten semantic CPIO deltas: the previous nine plus the required parent `extra/` directory.

## Runtime acceptance

r1 is accepted only if the automatic initrd path, with no manual module insertion, produces:

1. provider module loaded and bound;
2. dependency modules loaded in order;
3. patched `ov13858` module loaded;
4. native driver bound to `1-0010`;
5. native identity PASS;
6. runtime PM `suspended`, usage `0` after probe;
7. rails and MCLK disabled after probe;
8. reset asserted after probe;
9. no CSI endpoint and no streaming;
10. normal Wi-Fi/audio health;
11. exact payload hashes and Golden still saved default.

Rollback remains Golden v19c via saved default.
