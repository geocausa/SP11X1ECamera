.if (qwo(@x20+0x1ff8) < 0n4) { gc }
.if (qwo(@x20+0x1ff8) > 0n24) { gc }
.if (@$t19 == qwo(@x20+0x1ff8)) { gc }
.printf "GD_STAGE R=%I64u ptr=%p bank=%u colsminus2=%u rowsminus2=%u\n",qwo(@x20+0x1ff8),@x19+0xac,wo(@x19+0xb4),dwo(@x19+0xc0),dwo(@x19+0xc4)
.if (qwo(@x20+0x1ff8) == 0n4) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R04_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n5) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R05_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n6) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R06_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n7) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R07_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n8) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R08_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n9) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R09_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n10) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R10_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n11) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R11_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n12) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R12_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n13) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R13_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n14) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R14_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n15) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R15_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n16) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R16_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n17) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R17_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n18) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R18_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n19) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R19_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n20) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R20_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n21) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R21_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n22) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R22_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n23) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R23_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n24) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R24_LSC_STAGING.bin @x19+0xac @x19+0x194b; r @$t19=0n24; .if ((@$t18 & 0x100) != 0) { .printf "GD_CAPTURE_COMPLETE R=24 AWB=YES LSC=YES\n"; bc *; .logclose; .detach; q }; gc }
r @$t19=qwo(@x20+0x1ff8)
gc
