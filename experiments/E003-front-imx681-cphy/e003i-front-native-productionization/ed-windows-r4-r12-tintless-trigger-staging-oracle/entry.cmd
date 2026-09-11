.if (@$t0 < 0n4) { gc }
.if (@$t0 > 0n12) { gc }
.if (@$t0 == @$t2) { gc }
.if (@$t1 == 0) { .printf "ED_FAIL null_stats R=%I64u\n",@$t0; bc *; .logclose; .detach; q }
.if (dwo(@$t1+4) != 0x300) { .printf "ED_FAIL record_count R=%I64u n=%x\n",@$t0,dwo(@$t1+4); bc *; .logclose; .detach; q }
.if ((dwo(@$t1)&2) == 0) { .printf "ED_FAIL layout_bit1 R=%I64u word0=%x\n",@$t0,dwo(@$t1); bc *; .logclose; .detach; q }
.printf "ED_ENTRY R=%I64u stats=%p word0=%08x n=%u lux=%08x cct=%08x\n",@$t0,@$t1,dwo(@$t1),dwo(@$t1+4),dwo(@$t4+0x38),dwo(@$t4+0x48)
.if (@$t0 == 0n4) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R04_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R04_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n5) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R05_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R05_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n6) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R06_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R06_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n7) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R07_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R07_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n8) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R08_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R08_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n9) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R09_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R09_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n10) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R10_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R10_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n11) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R11_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R11_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n12) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R12_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R12_TRIGGER.bin @$t4 @$t4+0xff }
r @$t2=@$t0
gc
