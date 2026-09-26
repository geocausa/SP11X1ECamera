.if (@$t0 < 4) { gc }
.if (@$t0 > 18) { gc }
.if (@$t0 == @$t2) { gc }
.if (dwo(@x1+8) != 0x60800) { gc }
.if (@x0 == 0) { .printf "E007L_FAIL null_tune R=%I64u\n",@$t0; bc *; .logclose; .detach; q }
.if (@x1 == 0) { .printf "E007L_FAIL null_runtime R=%I64u\n",@$t0; bc *; .logclose; .detach; q }
.if (@x2 == 0) { .printf "E007L_FAIL null_desc R=%I64u\n",@$t0; bc *; .logclose; .detach; q }
.if (poi(@x2+0x10) == 0) { .printf "E007L_FAIL null_hist R=%I64u\n",@$t0; bc *; .logclose; .detach; q }
.printf "E007L_ENTRY R=%I64u lr=%p face=%p\n",@$t0,@lr,poi(@x1+0x450)
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E007L\R04_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E007L\R04_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E007L\R04_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E007L\R04_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E007L\R04_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E007L\R04_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E007L\R04_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 4) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R04_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 4) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R04_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 4) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R04_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E007L\R05_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E007L\R05_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E007L\R05_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E007L\R05_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E007L\R05_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E007L\R05_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E007L\R05_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 5) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R05_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 5) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R05_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 5) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R05_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E007L\R06_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E007L\R06_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E007L\R06_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E007L\R06_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E007L\R06_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E007L\R06_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E007L\R06_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 6) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R06_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 6) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R06_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 6) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R06_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E007L\R07_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E007L\R07_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E007L\R07_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E007L\R07_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E007L\R07_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E007L\R07_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E007L\R07_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 7) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R07_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 7) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R07_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 7) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R07_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E007L\R08_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E007L\R08_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E007L\R08_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E007L\R08_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E007L\R08_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E007L\R08_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E007L\R08_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 8) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R08_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 8) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R08_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 8) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R08_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E007L\R09_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E007L\R09_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E007L\R09_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E007L\R09_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E007L\R09_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E007L\R09_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E007L\R09_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 9) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R09_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 9) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R09_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 9) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R09_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E007L\R10_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E007L\R10_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E007L\R10_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E007L\R10_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E007L\R10_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E007L\R10_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E007L\R10_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 10) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R10_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 10) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R10_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 10) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R10_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E007L\R11_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E007L\R11_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E007L\R11_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E007L\R11_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E007L\R11_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E007L\R11_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E007L\R11_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 11) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R11_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 11) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R11_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 11) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R11_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E007L\R12_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E007L\R12_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E007L\R12_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E007L\R12_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E007L\R12_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E007L\R12_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E007L\R12_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 12) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R12_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 12) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R12_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 12) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R12_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 13) { .writemem C:\Users\Geoca\Documents\E007L\R13_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 13) { .writemem C:\Users\Geoca\Documents\E007L\R13_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 13) { .writemem C:\Users\Geoca\Documents\E007L\R13_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 13) { .writemem C:\Users\Geoca\Documents\E007L\R13_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 13) { .writemem C:\Users\Geoca\Documents\E007L\R13_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 13) { .writemem C:\Users\Geoca\Documents\E007L\R13_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 13) { .writemem C:\Users\Geoca\Documents\E007L\R13_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 13) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R13_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 13) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R13_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 13) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R13_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 14) { .writemem C:\Users\Geoca\Documents\E007L\R14_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 14) { .writemem C:\Users\Geoca\Documents\E007L\R14_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 14) { .writemem C:\Users\Geoca\Documents\E007L\R14_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 14) { .writemem C:\Users\Geoca\Documents\E007L\R14_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 14) { .writemem C:\Users\Geoca\Documents\E007L\R14_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 14) { .writemem C:\Users\Geoca\Documents\E007L\R14_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 14) { .writemem C:\Users\Geoca\Documents\E007L\R14_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 14) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R14_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 14) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R14_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 14) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R14_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 15) { .writemem C:\Users\Geoca\Documents\E007L\R15_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 15) { .writemem C:\Users\Geoca\Documents\E007L\R15_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 15) { .writemem C:\Users\Geoca\Documents\E007L\R15_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 15) { .writemem C:\Users\Geoca\Documents\E007L\R15_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 15) { .writemem C:\Users\Geoca\Documents\E007L\R15_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 15) { .writemem C:\Users\Geoca\Documents\E007L\R15_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 15) { .writemem C:\Users\Geoca\Documents\E007L\R15_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 15) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R15_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 15) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R15_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 15) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R15_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 16) { .writemem C:\Users\Geoca\Documents\E007L\R16_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 16) { .writemem C:\Users\Geoca\Documents\E007L\R16_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 16) { .writemem C:\Users\Geoca\Documents\E007L\R16_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 16) { .writemem C:\Users\Geoca\Documents\E007L\R16_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 16) { .writemem C:\Users\Geoca\Documents\E007L\R16_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 16) { .writemem C:\Users\Geoca\Documents\E007L\R16_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 16) { .writemem C:\Users\Geoca\Documents\E007L\R16_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 16) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R16_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 16) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R16_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 16) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R16_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 17) { .writemem C:\Users\Geoca\Documents\E007L\R17_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 17) { .writemem C:\Users\Geoca\Documents\E007L\R17_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 17) { .writemem C:\Users\Geoca\Documents\E007L\R17_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 17) { .writemem C:\Users\Geoca\Documents\E007L\R17_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 17) { .writemem C:\Users\Geoca\Documents\E007L\R17_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 17) { .writemem C:\Users\Geoca\Documents\E007L\R17_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 17) { .writemem C:\Users\Geoca\Documents\E007L\R17_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 17) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R17_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 17) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R17_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 17) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R17_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t0 == 18) { .writemem C:\Users\Geoca\Documents\E007L\R18_TUNE.bin @x0 @x0+0x16f }
.if (@$t0 == 18) { .writemem C:\Users\Geoca\Documents\E007L\R18_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t0 == 18) { .writemem C:\Users\Geoca\Documents\E007L\R18_DESC.bin @x2 @x2+0x87 }
.if (@$t0 == 18) { .writemem C:\Users\Geoca\Documents\E007L\R18_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if (@$t0 == 18) { .writemem C:\Users\Geoca\Documents\E007L\R18_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if (@$t0 == 18) { .writemem C:\Users\Geoca\Documents\E007L\R18_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if (@$t0 == 18) { .writemem C:\Users\Geoca\Documents\E007L\R18_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if (@$t0 == 18) { .if (poi(@x1) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R18_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t0 == 18) { .if (poi(@x1+0x40) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R18_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t0 == 18) { .if (poi(@x1+0x450) != 0) { .writemem C:\Users\Geoca\Documents\E007L\R18_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
r @$t2=@$t0
gc
