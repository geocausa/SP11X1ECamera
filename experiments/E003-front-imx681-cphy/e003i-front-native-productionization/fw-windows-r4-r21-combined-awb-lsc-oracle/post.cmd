.if (qwo(@x20+0x1ff8) < 0n4) { gc }
.if (qwo(@x20+0x1ff8) > 0n21) { gc }
.if (@$t19 == qwo(@x20+0x1ff8)) { gc }
.printf "FW_STAGE R=%I64u ptr=%p bank=%u colsminus2=%u rowsminus2=%u\n",qwo(@x20+0x1ff8),@x19+0xac,wo(@x19+0xb4),dwo(@x19+0xc0),dwo(@x19+0xc4)
.if (qwo(@x20+0x1ff8) == 0n4) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R04_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n5) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R05_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n6) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R06_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n7) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R07_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n8) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R08_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n9) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R09_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n10) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R10_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n11) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R11_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n12) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R12_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n13) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R13_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n14) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R14_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n15) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R15_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n16) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R16_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n17) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R17_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n18) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R18_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n19) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R19_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n20) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R20_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n21) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FW\\R21_LSC_STAGING.bin @x19+0xac @x19+0x194b; r @$t19=0n21; .if ((@$t18 & 0x100) != 0) { .printf "FW_CAPTURE_COMPLETE R=21 AWB=YES LSC=YES\n"; bc *; .logclose; .detach; q }; gc }
r @$t19=qwo(@x20+0x1ff8)
gc
