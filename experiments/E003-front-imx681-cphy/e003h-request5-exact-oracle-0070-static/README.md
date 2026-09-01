# E003h 0070 request5 exact Windows oracle

Fresh Windows KD captures close the second steady 0x958 request needed after successful 0069r1. Requests 4–7 in one Windows stream share one `period_cfg +0x8c` value; the value changes across streams. After zeroing the already-known IQ holes plus this per-stream period field, historical request4, fresh request4–7, and a second-stream request5 share one exact command skeleton.

`build-pix-oracle-capsule-r5.py` therefore keeps the already-proven 0069 request4 template (including its same-stream period_cfg) and substitutes only the exact request5 IQ register values/DMI payloads plus request_id 5. Raw Windows command/DMI bytes and generated capsule remain local/untracked; Git stores their identities and the builder/manifest.

This is static evidence only. It does not authorize Linux runtime.
