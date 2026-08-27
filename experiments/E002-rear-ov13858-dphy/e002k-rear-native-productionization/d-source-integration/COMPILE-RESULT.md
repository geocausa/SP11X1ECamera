# E002k-D maintained-source compile result

Date: 2026-08-27

## Isolated source

`/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src`

The tree is an independent copy of the exact Golden replay source; the clone audit proved zero shared regular-file inodes with Golden. The accepted E002k-C OV13858 driver is integrated there.

## Clean source split

1. `0001-media-ov13858-surface-profile.patch` — native OV13858 power/runtime-PM and firmware-selected 592.8 MHz Surface profile.
2. `0002-arm64-dts-qcom-hamoa-add-x1e-camera-infrastructure.patch` — generic X1E CAMCC/CCI0/CAMSS nodes. CSIPHY1 is 8 KiB, as physically proven by E002h-r1.
3. `0003-arm64-dts-qcom-denali-add-rear-ov13858.patch` — Surface-specific native PM8010-M regulator provider, GPIO97 MCLK1, CCI0/master1 400 kHz, OV13858 at 0x10, and four-lane 592.8 MHz CSIPHY1 graph.

No `microsoft,e002*`, stream gate, custom camera regulator compatible, or experiment marker exists in these maintained-source changes.

## Compile

Using the running Golden `/proc/config.gz` and an empty out-of-tree build directory:

`make -C sp11-camera-e002k-d-src O=e002k-d-build ARCH=arm64 olddefconfig`

`make -C sp11-camera-e002k-d-src O=e002k-d-build ARCH=arm64 -j$(nproc) qcom/x1e80100-microsoft-denali-oled.dtb`

Result: **PASS**, zero DTC warnings/errors from the make invocation.

Built DTB SHA-256:

`a8efe69044a8860ac4dc50d4a01b612f2925dc7648ec2e699b1412fa74f3c2f2`

## Runtime-kitchen warning

The generic maintained-source OLED target is **not** byte/semantic equivalent to deployed FullIO v19c. A mechanical decompile comparison found 44 semantic changed lines, including FullIO TX capture and touch/QSPI differences. Therefore this clean DTB is compile/review evidence only and MUST NOT replace the deployed v19c kitchen.

Runtime camera integration continues from the exact packaged/live v19c DTB SHA-256 `2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`, applying only the accepted camera/native-PM8010 delta until the maintained board source is reconciled with all v19c changes.
