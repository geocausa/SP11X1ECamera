.if (@$t0 < 0n4) { gc }
.if (@$t0 > 0n12) { gc }
.if (@$t0 == @$t3) { gc }
.printf "ED_STAGE R=%I64u ptr=%p bank=%u colsminus2=%u rowsminus2=%u\n",@$t0,@x19+0xac,wo(@x19+0xb4),dwo(@x19+0xc0),dwo(@x19+0xc4)
.if (@$t0 == 0n4) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R04_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n5) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R05_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n6) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R06_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n7) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R07_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n8) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R08_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n9) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R09_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n10) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R10_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n11) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R11_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n12) { .writemem C:\\Users\\Geoca\\Documents\\E003I-ED\\R12_LSC_STAGING.bin @x19+0xac @x19+0x194b; .printf "ED_CAPTURE_COMPLETE R=12\n"; bc *; .logclose; .detach; q }
r @$t3=@$t0
gc
