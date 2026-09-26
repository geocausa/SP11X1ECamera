.if (@$t0 < 4) { gc }
.if (@$t0 > 18) { gc }
.if (dwo(@x1+8) != 0x60800) { gc }
r @$t4=(@$t0*4)+@$t1
.if (@$t4 == @$t2) { gc }
.if (@x0 == 0) { .printf "E007M_FAIL null_tune R=%I64u S=%I64u\\n",@$t0,@$t1; bc *; .logclose; .detach; q }
.if (@x1 == 0) { .printf "E007M_FAIL null_runtime R=%I64u S=%I64u\\n",@$t0,@$t1; bc *; .logclose; .detach; q }
.if (@x2 == 0) { .printf "E007M_FAIL null_desc R=%I64u S=%I64u\\n",@$t0,@$t1; bc *; .logclose; .detach; q }
.if (poi(@x2+0x10) == 0) { .printf "E007M_FAIL null_hist R=%I64u S=%I64u\\n",@$t0,@$t1; bc *; .logclose; .detach; q }
.printf "E007M_INPUT R=%I64u S=%I64u\\n",@$t0,@$t1
.if ((@$t0 == 4) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 4) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 4) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 4) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 4) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 4) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 4) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 4) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 4) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 4) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 4) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 4) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 4) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 4) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 4) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 4) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 4) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 4) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 4) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 4) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R04_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 5) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 5) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 5) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 5) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 5) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 5) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 5) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 5) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 5) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 5) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 5) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 5) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 5) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 5) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 5) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 5) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 5) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 5) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 5) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 5) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R05_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 6) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 6) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 6) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 6) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 6) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 6) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 6) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 6) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 6) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 6) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 6) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 6) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 6) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 6) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 6) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 6) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 6) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 6) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 6) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 6) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R06_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 7) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 7) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 7) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 7) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 7) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 7) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 7) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 7) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 7) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 7) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 7) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 7) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 7) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 7) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 7) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 7) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 7) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 7) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 7) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 7) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R07_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 8) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 8) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 8) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 8) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 8) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 8) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 8) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 8) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 8) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 8) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 8) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 8) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 8) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 8) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 8) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 8) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 8) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 8) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 8) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 8) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R08_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 9) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 9) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 9) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 9) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 9) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 9) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 9) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 9) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 9) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 9) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 9) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 9) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 9) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 9) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 9) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 9) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 9) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 9) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 9) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 9) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R09_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 10) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 10) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 10) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 10) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 10) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 10) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 10) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 10) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 10) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 10) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 10) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 10) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 10) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 10) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 10) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 10) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 10) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 10) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 10) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 10) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R10_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 11) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 11) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 11) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 11) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 11) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 11) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 11) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 11) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 11) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 11) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 11) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 11) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 11) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 11) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 11) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 11) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 11) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 11) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 11) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 11) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R11_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 12) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 12) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 12) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 12) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 12) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 12) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 12) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 12) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 12) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 12) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 12) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 12) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 12) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 12) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 12) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 12) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 12) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 12) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 12) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 12) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R12_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 13) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 13) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 13) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 13) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 13) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 13) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 13) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 13) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 13) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 13) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 13) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 13) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 13) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 13) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 13) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 13) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 13) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 13) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 13) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 13) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R13_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 14) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 14) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 14) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 14) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 14) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 14) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 14) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 14) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 14) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 14) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 14) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 14) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 14) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 14) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 14) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 14) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 14) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 14) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 14) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 14) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R14_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 15) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 15) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 15) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 15) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 15) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 15) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 15) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 15) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 15) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 15) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 15) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 15) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 15) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 15) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 15) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 15) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 15) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 15) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 15) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 15) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R15_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 16) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 16) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 16) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 16) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 16) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 16) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 16) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 16) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 16) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 16) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 16) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 16) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 16) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 16) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 16) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 16) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 16) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 16) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 16) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 16) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R16_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 17) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 17) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 17) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 17) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 17) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 17) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 17) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 17) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 17) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 17) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 17) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 17) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 17) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 17) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 17) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 17) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 17) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 17) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 17) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 17) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R17_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 18) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S1_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 18) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S1_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 18) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S1_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 18) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S1_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 18) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S1_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 18) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S1_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 18) & (@$t1 == 1)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S1_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 18) & (@$t1 == 1)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S1_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 18) & (@$t1 == 1)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S1_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 18) & (@$t1 == 1)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S1_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if ((@$t0 == 18) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S2_TUNE.bin @x0 @x0+0x16f }
.if ((@$t0 == 18) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S2_RUNTIME.bin @x1 @x1+0x497 }
.if ((@$t0 == 18) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S2_DESC.bin @x2 @x2+0x87 }
.if ((@$t0 == 18) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S2_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff }
.if ((@$t0 == 18) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S2_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b }
.if ((@$t0 == 18) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S2_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b }
.if ((@$t0 == 18) & (@$t1 == 2)) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S2_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b }
.if ((@$t0 == 18) & (@$t1 == 2)) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S2_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if ((@$t0 == 18) & (@$t1 == 2)) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S2_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if ((@$t0 == 18) & (@$t1 == 2)) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007M\\R18_S2_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
r @$t2=@$t4
.if (@$t0 == 18) { .printf "E007M_CAPTURE_COMPLETE R=18 S=%I64u\\n",@$t1; bc *; .logclose; .detach; q }
gc
