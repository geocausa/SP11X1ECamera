.printf "E007N_HIT I=%I64u R=%I64u S=%I64u M=%I64x\\n",@$t5,@$t0,@$t1,@$t3
.if (@$t5 == 1) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H01_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 1) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H01_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 1) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H01_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 1) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H01_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 1) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H01_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 1) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H01_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 1) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H01_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 1) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H01_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 1) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H01_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 1) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H01_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 2) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H02_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 2) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H02_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 2) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H02_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 2) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H02_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 2) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H02_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 2) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H02_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 2) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H02_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 2) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H02_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 2) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H02_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 2) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H02_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 3) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H03_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 3) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H03_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 3) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H03_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 3) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H03_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 3) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H03_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 3) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H03_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 3) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H03_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 3) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H03_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 3) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H03_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 3) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H03_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 4) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H04_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 4) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H04_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 4) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H04_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 4) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H04_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 4) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H04_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 4) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H04_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 4) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H04_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 4) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H04_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 4) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H04_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 4) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H04_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 5) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H05_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 5) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H05_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 5) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H05_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 5) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H05_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 5) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H05_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 5) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H05_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 5) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H05_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 5) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H05_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 5) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H05_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 5) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H05_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 6) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H06_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 6) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H06_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 6) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H06_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 6) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H06_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 6) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H06_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 6) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H06_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 6) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H06_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 6) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H06_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 6) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H06_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 6) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H06_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 7) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H07_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 7) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H07_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 7) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H07_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 7) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H07_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 7) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H07_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 7) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H07_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 7) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H07_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 7) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H07_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 7) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H07_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 7) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H07_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 8) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H08_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 8) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H08_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 8) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H08_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 8) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H08_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 8) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H08_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 8) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H08_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 8) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H08_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 8) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H08_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 8) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H08_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 8) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H08_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 9) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H09_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 9) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H09_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 9) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H09_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 9) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H09_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 9) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H09_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 9) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H09_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 9) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H09_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 9) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H09_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 9) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H09_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 9) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H09_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 10) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H10_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 10) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H10_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 10) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H10_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 10) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H10_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 10) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H10_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 10) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H10_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 10) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H10_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 10) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H10_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 10) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H10_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 10) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H10_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 11) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H11_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 11) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H11_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 11) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H11_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 11) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H11_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 11) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H11_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 11) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H11_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 11) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H11_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 11) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H11_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 11) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H11_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 11) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H11_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 12) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H12_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 12) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H12_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 12) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H12_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 12) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H12_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 12) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H12_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 12) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H12_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 12) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H12_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 12) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H12_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 12) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H12_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 12) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H12_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 13) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H13_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 13) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H13_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 13) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H13_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 13) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H13_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 13) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H13_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 13) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H13_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 13) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H13_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 13) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H13_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 13) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H13_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 13) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H13_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 14) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H14_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 14) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H14_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 14) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H14_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 14) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H14_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 14) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H14_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 14) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H14_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 14) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H14_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 14) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H14_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 14) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H14_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 14) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H14_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 15) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H15_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 15) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H15_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 15) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H15_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 15) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H15_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 15) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H15_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 15) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H15_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 15) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H15_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 15) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H15_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 15) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H15_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 15) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H15_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 16) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H16_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 16) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H16_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 16) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H16_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 16) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H16_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 16) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H16_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 16) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H16_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 16) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H16_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 16) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H16_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 16) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H16_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 16) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H16_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 17) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H17_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 17) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H17_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 17) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H17_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 17) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H17_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 17) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H17_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 17) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H17_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 17) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H17_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 17) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H17_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 17) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H17_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 17) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H17_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 18) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H18_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 18) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H18_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 18) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H18_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 18) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H18_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 18) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H18_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 18) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H18_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 18) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H18_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 18) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H18_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 18) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H18_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 18) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H18_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 19) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H19_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 19) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H19_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 19) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H19_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 19) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H19_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 19) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H19_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 19) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H19_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 19) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H19_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 19) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H19_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 19) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H19_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 19) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H19_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 20) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H20_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 20) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H20_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 20) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H20_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 20) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H20_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 20) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H20_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 20) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H20_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 20) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H20_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 20) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H20_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 20) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H20_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 20) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H20_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 21) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H21_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 21) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H21_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 21) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H21_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 21) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H21_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 21) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H21_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 21) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H21_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 21) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H21_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 21) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H21_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 21) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H21_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 21) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H21_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 22) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H22_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 22) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H22_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 22) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H22_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 22) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H22_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 22) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H22_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 22) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H22_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 22) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H22_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 22) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H22_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 22) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H22_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 22) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H22_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 23) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H23_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 23) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H23_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 23) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H23_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 23) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H23_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 23) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H23_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 23) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H23_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 23) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H23_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 23) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H23_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 23) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H23_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 23) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H23_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 24) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H24_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 24) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H24_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 24) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H24_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 24) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H24_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 24) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H24_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 24) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H24_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 24) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H24_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 24) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H24_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 24) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H24_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 24) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H24_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 25) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H25_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 25) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H25_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 25) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H25_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 25) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H25_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 25) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H25_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 25) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H25_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 25) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H25_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 25) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H25_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 25) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H25_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 25) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H25_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 26) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H26_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 26) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H26_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 26) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H26_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 26) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H26_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 26) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H26_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 26) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H26_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 26) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H26_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 26) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H26_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 26) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H26_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 26) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H26_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 27) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H27_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 27) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H27_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 27) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H27_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 27) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H27_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 27) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H27_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 27) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H27_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 27) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H27_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 27) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H27_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 27) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H27_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 27) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H27_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 28) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H28_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 28) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H28_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 28) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H28_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 28) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H28_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 28) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H28_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 28) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H28_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 28) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H28_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 28) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H28_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 28) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H28_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 28) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H28_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 29) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H29_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 29) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H29_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 29) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H29_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 29) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H29_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 29) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H29_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 29) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H29_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 29) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H29_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 29) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H29_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 29) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H29_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 29) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H29_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 30) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H30_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 30) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H30_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 30) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H30_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 30) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H30_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 30) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H30_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 30) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H30_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 30) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H30_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 30) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H30_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 30) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H30_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 30) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H30_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 31) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H31_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 31) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H31_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 31) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H31_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 31) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H31_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 31) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H31_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 31) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H31_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 31) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H31_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 31) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H31_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 31) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H31_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 31) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H31_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 32) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H32_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 32) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H32_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 32) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H32_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 32) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H32_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 32) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H32_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 32) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H32_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 32) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H32_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 32) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H32_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 32) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H32_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 32) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H32_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 33) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H33_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 33) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H33_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 33) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H33_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 33) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H33_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 33) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H33_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 33) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H33_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 33) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H33_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 33) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H33_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 33) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H33_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 33) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H33_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 34) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H34_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 34) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H34_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 34) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H34_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 34) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H34_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 34) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H34_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 34) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H34_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 34) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H34_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 34) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H34_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 34) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H34_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 34) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H34_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 35) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H35_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 35) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H35_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 35) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H35_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 35) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H35_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 35) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H35_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 35) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H35_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 35) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H35_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 35) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H35_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 35) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H35_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 35) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H35_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 36) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H36_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 36) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H36_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 36) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H36_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 36) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H36_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 36) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H36_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 36) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H36_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 36) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H36_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 36) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H36_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 36) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H36_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 36) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H36_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 37) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H37_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 37) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H37_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 37) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H37_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 37) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H37_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 37) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H37_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 37) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H37_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 37) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H37_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 37) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H37_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 37) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H37_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 37) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H37_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 38) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H38_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 38) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H38_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 38) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H38_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 38) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H38_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 38) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H38_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 38) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H38_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 38) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H38_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 38) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H38_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 38) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H38_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 38) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H38_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 39) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H39_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 39) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H39_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 39) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H39_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 39) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H39_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 39) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H39_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 39) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H39_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 39) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H39_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 39) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H39_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 39) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H39_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 39) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H39_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 40) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H40_TUNE.bin @x0 @x0+0x16f }
.if (@$t5 == 40) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H40_RUNTIME.bin @x1 @x1+0x497 }
.if (@$t5 == 40) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H40_DESC.bin @x2 @x2+0x87 }
.if (@$t5 == 40) { .if (poi(@x2+0x10) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H40_HIST.bin poi(@x2+0x10) poi(@x2+0x10)+0xfff } }
.if (@$t5 == 40) { .if (poi(@x2+0x28) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H40_PRE_SRC.bin poi(@x2+0x28) poi(@x2+0x28)+0x1b } }
.if (@$t5 == 40) { .if (poi(@x2+0x30) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H40_PRE_DST.bin poi(@x2+0x30) poi(@x2+0x30)+0x1b } }
.if (@$t5 == 40) { .if (poi(@x2+0x50) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H40_PRE_COEF.bin poi(@x2+0x50) poi(@x2+0x50)+0x3b } }
.if (@$t5 == 40) { .if (poi(@x1) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H40_COMMON.bin poi(@x1) poi(@x1)+0x7f } }
.if (@$t5 == 40) { .if (poi(@x1+0x40) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H40_CTRL.bin poi(@x1+0x40)+0x8228 poi(@x1+0x40)+0x8267 } }
.if (@$t5 == 40) { .if (poi(@x1+0x450) != 0) { .writemem C:\\Users\\Geoca\\Documents\\E007N\\H40_FACE.bin poi(@x1+0x450) poi(@x1+0x450)+0x3f } }
.if (@$t5 == 40) { .printf "E007N_WINDOW_COMPLETE H=40\\n" }
gc
