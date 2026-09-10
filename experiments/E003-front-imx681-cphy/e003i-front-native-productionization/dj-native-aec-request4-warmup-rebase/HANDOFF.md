# DJ handoff

DJ corrects the DB startup recurrence by rebasing local G1 to Windows request-4 state without changing the external generation-local frame ID. Use `dj-native-aec-request4-warmup-rebase/native-aec-request-loop.{c,h}` in a runtime whose first statistics input is generation1/request4. Do not relax CH's policy-0 out-of-range rejection.

Before a live DB retry: run `verify-dj.py`, switch DB's integrated build from CP to DJ, rerun DB verification and full root prearm from a clean committed tree. Preserve the one-shot and no-same-boot-retry rules.
