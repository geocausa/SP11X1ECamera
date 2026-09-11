.if (qwo(@x20+0x1ff8) < 0n4) { gc }
.if (qwo(@x20+0x1ff8) > 0n27) { gc }
.if (@$t19 == qwo(@x20+0x1ff8)) { gc }
.printf "GJ_STAGE R=%I64u ptr=%p bank=%u colsminus2=%u rowsminus2=%u\n",qwo(@x20+0x1ff8),@x19+0xac,wo(@x19+0xb4),dwo(@x19+0xc0),dwo(@x19+0xc4)
.if (qwo(@x20+0x1ff8) == 0n4) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R04_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n5) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R05_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n6) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R06_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n7) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R07_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n8) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R08_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n9) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R09_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n10) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R10_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n11) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R11_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n12) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R12_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n13) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R13_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n14) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R14_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n15) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R15_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n16) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R16_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n17) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R17_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n18) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R18_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n19) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R19_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n20) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R20_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n21) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R21_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n22) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R22_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n23) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R23_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n24) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R24_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n25) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R25_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n26) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R26_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (qwo(@x20+0x1ff8) == 0n27) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GJ\\R27_LSC_STAGING.bin @x19+0xac @x19+0x194b; r @$t19=0n27; .if ((@$t18 & 0x100) != 0) { .printf "GJ_CAPTURE_COMPLETE R=27 AWB=YES LSC=YES\n"; bc *; .logclose; .detach; q }; gc }
r @$t19=qwo(@x20+0x1ff8)
gc
