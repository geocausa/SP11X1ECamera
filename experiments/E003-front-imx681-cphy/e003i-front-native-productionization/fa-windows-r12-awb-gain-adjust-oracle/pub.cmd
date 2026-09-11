r @$t18=qwo(@x23+0x128)
.if (@$t18 < 4) { gc }
.if (@$t18 > 12) { gc }
.if (@$t17 != 1) { .printf "FA_FAIL_MISSING_GA req=%I64u\n",@$t18; bc *; .logclose; .detach; q }
.printf "FA_GA req=%I64u rg=%08x bg=%08x lux=%08x cct=%08x cctr=%08x cctg=%08x cctb=%08x tri=%u v0=%u v1=%u v2=%u w0=%08x w1=%08x w2=%08x ar=%08x ag=%08x ab=%08x\n",@$t18,@$t0,@$t1,@$t2,@$t3,@$t4,@$t5,@$t6,@$t7,@$t8,@$t9,@$t10,@$t11,@$t12,@$t13,@$t14,@$t15,@$t16
.printf "FA_PUB req=%I64u R=%08x G=%08x B=%08x CCT=%u\n",@$t18,dwo(@x13+8),dwo(@x13+0xc),dwo(@x13+0x10),dwo(@x13+0x14)
r @$t17=0
r @$t19=@$t19+1
.if (@$t18 == 12) { .printf "FA_CAPTURE_COMPLETE R=12 PAIRS=%u\n",@$t19; bc *; .logclose; .detach; q }
gc
