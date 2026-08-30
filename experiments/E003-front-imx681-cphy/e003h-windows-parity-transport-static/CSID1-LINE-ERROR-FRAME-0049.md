# E003h 0049 — CSID1 line-error frame read-only telemetry

0048 proved CSID1 reaches CAMIF SOF/EOF, Epoch0/1 and RUP_DONE, but transient IPP bit14 is present only in Linux history. Exact Windows/qccamisp and Qualcomm CSID680 evidence classify bit14 as a real line-count/frame-size error and show Windows expected/actual frame size is 2160×3840.

0049 is diagnostic-only. When the existing front-mode0 CSID ISR sees IPP bit14, before the existing IPP clear it reads and software-latches:

- `+0x38c` format-measure actual frame size;
- `+0x390` HBI;
- `+0x394` VBI.

It adds no MMIO writes and changes no mask, clear, CSID/VFE configuration, RT-CDM command, CSIPHY or sensor behavior. The three reads are conditional on the already-observed error bit.

Static facts:

- patch SHA-256 `58f9080b7ae1e9addbfb035930374d073a1694c0a666132dcd1604e13b14f4e3`;
- checkpatch: 0 errors / 0 warnings;
- exact source round-trip: PASS;
- source `camss-csid-680.c` SHA-256 `e207f5d8f522829c4bd45058ede1387fc064b16f7f1d2b649b62465601e5c261`;
- source `camss-csid.h` SHA-256 `3088e0013292d6765b8d76cdde8407bd298b4941a67a67c9d28a7a3be2f13f47`;
- Golden-ABI `qcom-camss.ko` SHA-256 `610c0def762e6449c342452ffc436b195cd1330a41055076d25cca95f077a1f5`;
- inspection SHA-256 `e5d53e72e90406023616c2658f413ca80d6c49e9ff1f4622929012299eb17afe`;
- inspector SHA-256 `980fa12059c9f535a683145614e1e42cf13534cd5f6edff70a8f281622e14f66`.

No runtime is authorized by this checkpoint. Package and authorize separately.
