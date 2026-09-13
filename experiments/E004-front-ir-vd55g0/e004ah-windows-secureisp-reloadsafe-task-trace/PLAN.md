# E004ah — reload-safe Windows SecureISP dynamic task trace

Purpose: close the E004z dynamic parity gate using same-machine Windows and real IR frames.

Prior E004aa was aborted before trace. E004ab/ac/af/ag repo directories contain preparation records only.
SP7 retained logs show the later attempts armed absolute breakpoints against a SecureISP image base that changed after driver reload. Those logs are diagnostic only and are not accepted task evidence.

This run uses reload-safe unresolved module+RVA breakpoints:
- +0x3350 outer SecureISP operation dispatcher; record operation
- +0x4a90 Secure Companion send helper; record task ID, selector/class source, pointers and lengths
- +0x24f0 exported function-table dispatcher; record command 0x2e/0x2f and dereference 8-byte lane mask
- +0x1b08 ConfigSecureCamera; record lane mask and protect boolean

Trigger is the exact proven Surface IR Camera Front / Infrared / VideoPreview holder and requires real TryAcquireLatestFrame() frames.

Acceptance requires task/lane records plus >=3 real frames and clean StopAsync, followed by immediate return to protected Golden. Linux SecureISP runtime remains unauthorized.
