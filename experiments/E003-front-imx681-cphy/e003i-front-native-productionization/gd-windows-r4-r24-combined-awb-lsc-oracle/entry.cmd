.if (qwo(@x1+0x1ff8) < 0n4) { gc }
.if (qwo(@x1+0x1ff8) > 0n24) { gc }
.if ((@$t18 & 0xff) == qwo(@x1+0x1ff8)) { gc }
.if (poi(@x0+0xa0) == 0) { .printf "GD_FAIL null_stats R=%I64u\n",qwo(@x1+0x1ff8); bc *; .logclose; .detach; q }
.if (dwo(poi(@x0+0xa0)+4) != 0x300) { .printf "GD_FAIL record_count R=%I64u n=%x\n",qwo(@x1+0x1ff8),dwo(poi(@x0+0xa0)+4); bc *; .logclose; .detach; q }
.if ((dwo(poi(@x0+0xa0))&2) == 0) { .printf "GD_FAIL layout_bit1 R=%I64u word0=%x\n",qwo(@x1+0x1ff8),dwo(poi(@x0+0xa0)); bc *; .logclose; .detach; q }
.printf "GD_ENTRY R=%I64u stats=%p word0=%08x n=%u lux=%08x cct=%08x\n",qwo(@x1+0x1ff8),poi(@x0+0xa0),dwo(poi(@x0+0xa0)),dwo(poi(@x0+0xa0)+4),dwo(@x1+0x2080+0x38),dwo(@x1+0x2080+0x48)
.if (qwo(@x1+0x1ff8) == 0n4) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R04_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R04_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n5) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R05_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R05_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n6) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R06_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R06_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n7) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R07_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R07_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n8) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R08_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R08_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n9) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R09_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R09_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n10) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R10_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R10_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n11) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R11_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R11_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n12) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R12_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R12_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n13) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R13_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R13_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n14) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R14_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R14_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n15) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R15_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R15_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n16) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R16_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R16_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n17) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R17_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R17_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n18) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R18_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R18_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n19) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R19_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R19_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n20) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R20_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R20_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n21) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R21_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R21_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n22) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R22_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R22_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n23) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R23_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R23_TRIGGER.bin @x1+0x2080 @x1+0x217f }
.if (qwo(@x1+0x1ff8) == 0n24) { .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R24_TINTLESS_STATS.bin poi(@x0+0xa0) poi(@x0+0xa0)+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-GD\\R24_TRIGGER.bin @x1+0x2080 @x1+0x217f }
r @$t18=(@$t18&0x100)|qwo(@x1+0x1ff8)
gc
