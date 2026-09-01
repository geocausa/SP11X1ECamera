# E003h 0069r1 — byte-identical pre-capture retry

0069 never invoked the V4L2 helper: standard `ac16000.cci` probe failed before IMX681 registration. This r1 candidate changes no camera asset or hardware recipe. It uses a new one-shot boot identity and authorization chain only. If CCI fails again, no sysfs bind/reset workaround is allowed and the helper must remain unused.
