# E008h — rear two-slot ten-WM prime/ownership scaffold

Parent Git: 131506568acd (E008g).

Status: BUILD-ONLY / UNREACHABLE / NO CAMERA / NO MODULE LOAD.

## Why two complete output sets are required

E008e observed a second wave of BUS address activity after ISP_START_DONE and
before the next selector-2 batch. E008g maps that next batch to startup packet2
at the first IFE Epoch0. The existing exact-driver scheduler contract also
places the complete BUS address update before the Epoch0 RT-CDM selector-2
consume.

E008d owns only one complete ten-WM output set. Rewriting that same set at
first Epoch0 would preserve DMA safety only if the payload were allowed to be
overwritten; it cannot preserve the first processed rear frame for inspection.
E008h therefore reserves two distinct complete Linux-owned sets and refuses
any cross-slot IOVA overlap.

This is a conservative Linux ownership requirement. It does not claim that
E008e's redacted trace proved the Windows IOVAs were distinct.

## Two-slot structure

Each slot contains the full E008d one-frame private allocation:

- one 0xFF6000 FULL coherent surface split into non-overlapping WM0 Y and WM1 C
  owned spans;
- independent coherent outputs for WM2/3/11/12/13/14/16/18;
- one independent E007z ten-WM exact-consumed-IOVA ledger.

The one-slot private allocation budget is 0x1369D00 bytes. Two slots reserve
0x26D3A00 bytes (40,712,704 bytes) before hardware activation.

E008h rebuilds the E007z bindings directly from the Linux DMA allocations and
validates every pair of owned spans across slot0 and slot1 as non-overlapping.
The ledgers receive the same REAR owner epoch and consecutive request
generations.

## Safe activation model

E008d preloads slot0 static configuration and valid Linux addresses while all
WMs are disabled. E008h preserves that safety improvement, then models the
live E008f resource sequence using this WM order:

WM0, WM1, WM2, WM3, WM11, WM18, WM12, WM14, WM13, WM16

That corresponds to FULL, DS4, DS16, AEC_BE, RS, BHIST, AWB_BG, TL_BG, BAF.
After enable, E008h rewrites and readbacks slot0 addresses, so the effective
post-enable phase remains Windows-observed enable -> initial addresses while
never allowing an enabled WM to contain an unowned address.

At the future first Epoch0, e008h_rear_epoch0_retarget_slot1() writes and
readbacks the second complete ten-WM address set. E008g requires that action
to occur before E007y packet2 is submitted. E008h itself never submits RT-CDM,
starts CSID/CSIPHY/sensor, or installs a caller.

## Completion ownership

e008h_rear_observe_consumed() routes each already-latched/ACKed completion to
the unique pending slot whose E007z programmed image IOVA exactly equals the
reported last-consumed IOVA. A stale duplicate from an already-cleared slot
returns EALREADY; a non-matching or ambiguous IOVA faults both ledgers. No
completion-group bit can retire a buffer by implication.

both_complete means only that both E007z ledgers have all ten exact IOVAs
accounted for. It is not permission to free DMA. E008a-c BUS stop, IRQ drain,
RT-CDM stop, source teardown and owner-safe release remain mandatory.

## Remaining boundary

This checkpoint deliberately stops before composing the complete rear runner.
The next gate is to integrate E007y packet0/1 pre-CSID, E008h slot0 activation,
CSID1/CSIPHY1/OV13858 start, first-Epoch0 slot1 retarget + packet2, packet3 on
the next Epoch0, two-slot completion dispatch, and E008c teardown into one
still-unreachable fail-closed runner.

No native rear frame is attempted here.


## Build result — PASS

Fresh isolated fix1 CAMSS build completed with `W=1 -j4`, zero warnings/errors and exact protected-Golden vermagic. The resulting private `qcom-camss.ko` is 13,797,352 bytes, SHA-256 `261920bcd5fe3c847c6f465aad6031d08101df07715f335288f7a4f759253cb1`. PiMaster verification passed and an independent Fabric verifier/hash/vermagic check passed. The module was not installed or loaded and no camera, WM-enable runtime, RT-CDM submission or reboot occurred.

The first isolated build identity is consumed: it failed at compile time because the local variable name `current` collided with the kernel `current` macro. No module was produced from that identity. The source was corrected to `cfg_now` and a fresh `-fix1` build directory was used; the failed build directory was not reused.
