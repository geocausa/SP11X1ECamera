.if (@$t0 < 0n4) { gc }
.if (@$t0 > 0n15) { gc }
.if (@$t0 == @$t2) { gc }
.if (@$t1 == 0) { .printf "FI_FAIL null_stats R=%I64u\n",@$t0; bc *; .logclose; .detach; q }
.if (dwo(@$t1+4) != 0x300) { .printf "FI_FAIL record_count R=%I64u n=%x\n",@$t0,dwo(@$t1+4); bc *; .logclose; .detach; q }
.if ((dwo(@$t1)&2) == 0) { .printf "FI_FAIL layout_bit1 R=%I64u word0=%x\n",@$t0,dwo(@$t1); bc *; .logclose; .detach; q }
.printf "FI_ENTRY R=%I64u stats=%p word0=%08x n=%u lux=%08x cct=%08x\n",@$t0,@$t1,dwo(@$t1),dwo(@$t1+4),dwo(@$t4+0x38),dwo(@$t4+0x48)
.if (@$t0 == 0n4) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R04_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R04_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n5) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R05_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R05_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n6) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R06_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R06_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n7) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R07_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R07_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n8) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R08_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R08_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n9) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R09_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R09_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n10) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R10_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R10_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n11) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R11_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R11_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n12) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R12_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R12_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n13) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R13_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R13_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n14) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R14_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R14_TRIGGER.bin @$t4 @$t4+0xff }
.if (@$t0 == 0n15) { .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R15_TINTLESS_STATS.bin @$t1 @$t1+0x12beb; .writemem C:\\Users\\Geoca\\Documents\\E003I-FI\\R15_TRIGGER.bin @$t4 @$t4+0xff }
r @$t2=@$t0
gc
