# E003d preflight — IMX681 C-PHY graph, stream blocked

## Goal

Connect the already-accepted native IMX681 subdevice to X1E80100 CAMSS CSIPHY2 as one-trio CSI-2 C-PHY while keeping sensor streaming impossible.

## Host implementation

Generic C-PHY plumbing is the minimal applicable subset of the archived Qualcomm v9 series:
- preserve PHY type in parsed endpoint state;
- C-PHY lane-mask semantics;
- select C-PHY at CSID Gen2 RX;
- C-PHY-aware CAMSS link-rate fallback math;
- accept C-PHY endpoints.

X1E electrical programming does **not** use the generic SDM845 table. It uses an exact 121-record table mechanically extracted from this SP11's local `qccammipicsi8380.sys` (SHA-256 `033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407`). The binary passes the table at VA `0x140010c50` with count 121 to its register writer. 118 unique final offsets match both independent KD live snapshots exactly.

The Windows delay field conversion is proven as nanoseconds to microseconds; Linux preserves the resulting 10 ms / 1 ms / 10 ms delays.

## DT boundary

Front endpoint only:
- CSIPHY2 / port 2;
- `MEDIA_BUS_TYPE_CSI2_CPHY`;
- one trio as `data-lanes = <0>`;
- symmetric remote endpoints.

No link-frequency is asserted in E003d. Streaming remains blocked by the accepted E003c driver's `.s_stream(1) = -EOPNOTSUPP`, and the driver still contains no sensor write path.

## Runtime acceptance

1. exact Golden kernel release and one-shot boot;
2. IMX681 dual identity still passes;
3. IMX681 appears as a media sensor linked immutably to `msm_csiphy2`;
4. direct test of `s_stream(1)` remains `-EOPNOTSUPP`;
5. sensor PM suspended/usage 0 after probe;
6. MCLK4/front rails/CSIPHY2 clocks remain disabled;
7. no C-PHY electrical table execution occurs because streaming is blocked;
8. rear OV13858, Wi-Fi, FullIO audio and G6 touch remain healthy;
9. return to byte-exact Golden.
