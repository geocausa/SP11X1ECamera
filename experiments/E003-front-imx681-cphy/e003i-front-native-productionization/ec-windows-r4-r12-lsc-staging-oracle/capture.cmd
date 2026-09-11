.if (@$t0 < 4) { gc }
.if (@$t0 > 12) { gc }
.if (@$t0 == @$t2) { gc }
.printf "EC_STAGE R=%I64u ptr=%p bank=%u colsminus2=%u rowsminus2=%u\n",@$t0,@x19+0xac,wo(@x19+0xb4),dwo(@x19+0xc0),dwo(@x19+0xc4)
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E003I-EC\R04_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E003I-EC\R05_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E003I-EC\R06_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E003I-EC\R07_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E003I-EC\R08_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E003I-EC\R09_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E003I-EC\R10_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E003I-EC\R11_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E003I-EC\R12_LSC_STAGING.bin @x19+0xac @x19+0x194b; .printf "EC_CAPTURE_COMPLETE R=12\n"; bc *; .logclose; .detach; q }
r @$t2=@$t0
gc
