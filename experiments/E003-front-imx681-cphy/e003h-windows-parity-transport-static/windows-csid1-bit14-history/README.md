# Same-SP11 Windows CSID1 IPP bit14 history

This bounded dynamic oracle follows Linux 0049, which measured a transient CSID1 `ERROR_LINE_COUNT` event with actual `3840x2640` while expected/cropped geometry was `3840x2160`.

SP7 KD armed qccamisp8380's IPP-error branch at RVA `0x1ba04`. A separate proof breakpoint at RVA `0x1b3e0` fired once and proved the tested route is CSID1 selector `5` (IPP), index `1`. Pre-enable state was Windows-exact: `CFG0=0x802b2000`, crop `0x0eff0000/0x086f0000`, expected frame `0x08700f00`.

The error breakpoint remained armed across that selector-proven start plus two timestamped/UI-confirmed Camera restarts. It never fired. At the bounded end Windows reported expected=actual `0x08700f00` (3840x2160), HBI `0x03b203ad`, VBI `0x00ffffff`, IPP status `0x00e11ff8` with bit14 clear.

This proves only the bounded normal-start sample: it does not claim Windows can never assert bit14. It does establish that Linux 0049's 480-line error is not reproduced by the tested normal Windows front-camera startup and is therefore a concrete parity fault. It does not yet prove that this error causes the missing VFE1 raw Epoch0.

Next gate: statically close CSID680 vertical-crop active/shadow/update semantics. Linux crop register readback matches Windows, yet Linux's error-time measured frame remains 2640 lines while Windows reaches 2160 lines.
