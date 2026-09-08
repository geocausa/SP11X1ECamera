# CN static proof

## History lookup

`CAECXHistory::GetInternalFrameHistory @ 0x1803ae6f8`:

- `0x1803ae74c`: load start-config-valid `history+0x0c`; zero takes the no-start-config path.
- `0x1803ae754`: load current-frame-valid `history+0x1c0`.
- current frame invalid: `0x1803ae7c4` selects `history+0x10` (synthetic start record).
- current frame valid: `0x1803ae7d4` loads the ordinary active-list owner from `history+0x1d0`; `x10` is initially the synthetic start record.
- each real node: `0x1803ae7f4..0x1803ae804` sets `x10=node+0x10`, loads saved frame ID from that payload, and accepts when `saved_frame + offset <= current_frame`.
- if no node is old enough, traversal ends with `x10` still pointing at the oldest inspected real record. If the list is empty, `x10` remains the synthetic start record.

For ordinary records the `payload+0x188` special flag is zero, so the first selected lookup result exits at `0x1803ae84c`.

## Convergence startup carrier

`CAECXConvergence::RunConvProcesss`:

- `0x1803b4700..0x1803b470c`: request history offset 1.
- NULL history: `0x1803b4718..0x1803b4720` writes `PredGain=1.0f` at convergence `+0xd8` and `previous_delta=0` at `+0xdc`.
- history present: `0x1803b479c..0x1803b47a8` copies record `+0x178 -> +0xd8` and record `+0x17c -> +0xdc`.

The ordinary control state backing record `+0x178` is zero-initialized at `0x180371150` (`owner+0x970`) and copied to the outgoing record at `0x180376ed4..0x180376edc`. The captured synthetic record independently proves `+0x17c == 0`.

The native CG reduction uses history DRC gain only under `drc_gain > 1.0f`, matching the Windows ordinary Short-history adjustment. Therefore startup zero is the exact identity case for this scoped consumer.

## Live oracle

`ORACLE-EVIDENCE.txt` freezes two independent read-only Windows FrameServer runs. Both see:

- `history+0x0c == 1`;
- active ordinary list via `history+0x1d0`, count 10 at discovery;
- synthetic start SHA-256 `7d703a37b02a99fe7e2915d14e9a63ddc805d1985681a1f89831556f0d2a1d5f`;
- frame 0, marker 1;
- all seven exposure lanes `33,333,332`;
- real node marker 0 and `eq_start=False`.

The earlier `history+0xc28` container is not the ordinary live frame list; it was observed with count zero and is excluded from the warm-up model.
