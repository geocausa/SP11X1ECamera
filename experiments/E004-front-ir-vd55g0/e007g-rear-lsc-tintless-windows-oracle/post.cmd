.if (@$t0 < 0n4) { gc }
.if (@$t0 > 0n18) { gc }
.if (@$t0 == @$t3) { gc }
.printf "E007G_STAGE R=%I64u ptr=%p bank=%u colsminus2=%u rowsminus2=%u\n",@$t0,@x19+0xac,wo(@x19+0xb4),dwo(@x19+0xc0),dwo(@x19+0xc4)
.if (@$t0 == 0n4) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R04_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n5) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R05_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n6) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R06_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n7) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R07_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n8) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R08_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n9) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R09_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n10) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R10_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n11) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R11_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n12) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R12_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n13) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R13_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n14) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R14_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n15) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R15_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n16) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R16_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n17) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R17_LSC_STAGING.bin @x19+0xac @x19+0x194b }
.if (@$t0 == 0n18) { .writemem C:\\Users\\Geoca\\Documents\\E007G\\R18_LSC_STAGING.bin @x19+0xac @x19+0x194b; .printf "E007G_CAPTURE_COMPLETE R=18\n"; bc *; .logclose; .detach; q }
r @$t3=@$t0
gc
