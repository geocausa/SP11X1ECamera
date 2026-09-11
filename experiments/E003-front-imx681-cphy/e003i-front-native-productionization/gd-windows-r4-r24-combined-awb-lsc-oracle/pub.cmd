.if (qwo(@x23+0x128) < 0n4) { gc }
.if (qwo(@x23+0x128) > 0n24) { gc }
.if (@$t17 != 1) { .printf "GD_FAIL_MISSING_GA req=%I64u\n",qwo(@x23+0x128); bc *; .logclose; .detach; q }
.printf "GD_GA req=%I64u rg=%08x bg=%08x lux=%08x cct=%08x cctr=%08x cctg=%08x cctb=%08x tri=%u v0=%u v1=%u v2=%u w0=%08x w1=%08x w2=%08x ar=%08x ag=%08x ab=%08x\n",qwo(@x23+0x128),@$t0,@$t1,@$t2,@$t3,@$t4,@$t5,@$t6,@$t7,@$t8,@$t9,@$t10,@$t11,@$t12,@$t13,@$t14,@$t15,@$t16
.printf "GD_PUB req=%I64u R=%08x G=%08x B=%08x CCT=%u\n",qwo(@x23+0x128),dwo(@x13+8),dwo(@x13+0xc),dwo(@x13+0x10),dwo(@x13+0x14)
r @$t17=0
.if (qwo(@x23+0x128) == 0n24) { r @$t18=@$t18|0x100; .if (@$t19 == 0n24) { .printf "GD_CAPTURE_COMPLETE R=24 AWB=YES LSC=YES\n"; bc *; .logclose; .detach; q } }
gc
