r @$t0=qwo(@x19+0x1ff8)
.if (@$t0 < 4) { gc }
.if (@$t0 > 18) { gc }
.if (@$t0 == @$t3) { gc }
.if (poi(@x19+0x40) == 0) { .printf "E007L_FAIL null_state R=%I64u\n",@$t0; bc *; .logclose; .detach; q }
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E007L\R04_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R04_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E007L\R04_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E007L\R05_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R05_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E007L\R05_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E007L\R06_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R06_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E007L\R06_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E007L\R07_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R07_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E007L\R07_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E007L\R08_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R08_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E007L\R08_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E007L\R09_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R09_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E007L\R09_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E007L\R10_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R10_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E007L\R10_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E007L\R11_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R11_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E007L\R11_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E007L\R12_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R12_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E007L\R12_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 13) { .writemem C:\Users\Geoca\Documents\E007L\R13_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R13_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 13) { .writemem C:\Users\Geoca\Documents\E007L\R13_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 14) { .writemem C:\Users\Geoca\Documents\E007L\R14_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R14_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 14) { .writemem C:\Users\Geoca\Documents\E007L\R14_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 15) { .writemem C:\Users\Geoca\Documents\E007L\R15_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R15_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 15) { .writemem C:\Users\Geoca\Documents\E007L\R15_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 16) { .writemem C:\Users\Geoca\Documents\E007L\R16_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R16_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 16) { .writemem C:\Users\Geoca\Documents\E007L\R16_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 17) { .writemem C:\Users\Geoca\Documents\E007L\R17_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R17_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 17) { .writemem C:\Users\Geoca\Documents\E007L\R17_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.if (@$t0 == 18) { .writemem C:\Users\Geoca\Documents\E007L\R18_POST_SRC.bin poi(@x19+0x40)+0x5104 poi(@x19+0x40)+0x511f; .writemem C:\Users\Geoca\Documents\E007L\R18_POST_DST.bin poi(@x19+0x40)+0x5120 poi(@x19+0x40)+0x513b }
.if (@$t0 == 18) { .writemem C:\Users\Geoca\Documents\E007L\R18_POST_COEF.bin poi(@x19+0x40)+0x51b0 poi(@x19+0x40)+0x51eb }
.printf "E007L_POST R=%I64u\n",@$t0
r @$t3=@$t0
.if (@$t0 == 18) { .printf "E007L_CAPTURE_COMPLETE R=18\n"; bc *; .logclose; .detach; q }
gc
