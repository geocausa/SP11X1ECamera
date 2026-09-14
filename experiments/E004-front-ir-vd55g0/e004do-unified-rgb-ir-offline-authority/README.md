# E004do — unified rear RGB + front RGB + IR offline authority

Status: **PASS OFFLINE / COMPILE ONLY / NO CAMERA RUNTIME**.

E004dn closed repeated rear/front RGB handoff on the accepted unified IB DTB. The next whole-stack integration problem is that the proven VD55G0 IR bind/receiver work lived in an IR-isolated graph and used the E004k CSIPHY0 D-PHY parity delta, while accepted RGB runtime uses its own CAMSS authority. E004do answers whether those authorities can coexist structurally without touching Linux SecureISP runtime.

## Three-camera DT authority

Base RGB authority:

- IB unified rear/front DTB SHA256 `5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321`.

IR graph authority:

- E004l native-bind DTB SHA256 `dd54d71226b354e68164db7ad0d0985fb2d63fe584c4d0e1f647eb69ee3fe96b`.

E004l is a strict structural superset of IB for the relevant tree: it contributes exactly 13 IR-specific nodes and removes no IB node. E004do mechanically adds those 13 nodes to IB, remaps their phandles collision-free, imports only the seven IR symbol aliases, changes the otherwise-empty CCI0 bus0 clock from 1 MHz to the proven IR 400 kHz value, and widens only the CSIPHY0 resource from 0x1000 to 0x2000 as proven by E004v.

Output DTB:

- SHA256 `3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb`.

The result exposes all three external CAMSS ports simultaneously:

- port@0 — VD55G0 IR -> CSIPHY0 D-PHY;
- port@1 — OV13858 rear RGB;
- port@2 — IMX681 front RGB.

All accepted rear/front RGB sensor and endpoint nodes are property-byte-identical to IB. The IB CAMSS IOMMU union is unchanged. Across common nodes, the only deltas are the seven IR symbol aliases, CCI0 bus0 clock, and the single CAMSS `reg` resource-size change for CSIPHY0.

CCI0 bus0 is empty in IB; both accepted RGB sensors live on bus1, so the 400 kHz IR bus authority does not retime either RGB sensor bus.

## CAMSS coexistence compile proof

E004k's exact IR receiver patch SHA256 is:

`1fc0f918a2f00e79918cf8bf7164f49cb8df395b8b05c949dc424a7b3824a869`

It still applies cleanly to the current stable RGB CAMSS source. The delta is narrowly gated by all of:

- X1E80100;
- CSIPHY id 0;
- D-PHY;
- disabled-by-default module parameter `e004j_ir_dphy_windows_parity`.

It therefore does not select on rear CSIPHY1 or front RGB CSIPHY2/C-PHY.

Deterministic compile hashes from identical current-source snapshots:

- baseline CAMSS: `9cd7e472ed9e5f0f071ec533e86c89ca88c9acef84194c7cf992f0196a2752f5`;
- IR-gated CAMSS: `4c3c6e9c8dbd34ecf1346a66670bf5568b7af23d1bba7131f7c493d6268611a4`.

These are **compile artifacts only**. They do not replace the accepted RGB runtime CAMSS module `7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95` at this stage.

## VD55G0 source proof

The merged graph points at the already-accepted native bind-only VD55G0 source SHA256:

`20bca88eb4333f386e76e17d800268511dcf30fbc0b642d39e425e00703d6745`

A disposable deterministic build against Golden headers passes with module SHA256:

`e935d8a78d76d7cdc63b30d5a98708d8dfd62f0c0fec24a7158b53a0418afd81`.

The source remains bind-only: fixed Y10 644x604 D-PHY1 @ 420 MHz, Windows patch/safe42 initialization, SW_STBY final state, stream-on `-EOPNOTSUPP`, and no illumination API.

## Safety boundary

E004do performs no camera runtime. Golden FullIO v19c remains active; no camera module is loaded; no GRUB one-shot is armed. No sensor stream, IR illumination, CSID/VFE stream, Linux SecureISP action, secure CB9 enable, CPZ migration, protected ownership transition, FastRPC protected invoke, or secure-lane call occurs.

## Next gate

Prepare a **fresh bind/receiver-only three-camera coexistence one-shot** using this DTB and the E004k-gated CAMSS build. Acceptance should require:

1. all rear/front/IR sensor graph entities bind simultaneously;
2. rear/front RGB route links remain present but no RGB stream is started;
3. VD55G0 reaches the proven Windows-state SW_STBY contract and direct stream remains refused;
4. CSIPHY0 receiver-only programming/readback remains 96/96 Windows-exact, then powers off;
5. VD55G0 remains runtime-suspended before and after receiver proof;
6. no illumination, CSID stream, VFE stream, capture, SecureISP, or protected-memory action;
7. one attempt only, mandatory Golden return and candidate retirement.

Only after coexistence passes should separate fresh candidates regress rear and front RGB streaming under the three-camera DT. Linux SecureISP runtime remains unauthorized.
