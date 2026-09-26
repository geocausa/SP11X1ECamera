.if (@$t0 < 4) { gc }
.if (@$t0 > 18) { gc }
.if (@$t0 == @$t3) { gc }
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E007J\R04_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=4\n"; r @$t3=4; gc }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E007J\R05_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=5\n"; r @$t3=5; gc }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E007J\R06_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=6\n"; r @$t3=6; gc }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E007J\R07_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=7\n"; r @$t3=7; gc }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E007J\R08_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=8\n"; r @$t3=8; gc }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E007J\R09_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=9\n"; r @$t3=9; gc }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E007J\R10_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=10\n"; r @$t3=10; gc }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E007J\R11_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=11\n"; r @$t3=11; gc }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E007J\R12_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=12\n"; r @$t3=12; gc }
.if (@$t0 == 13) { .writemem C:\Users\Geoca\Documents\E007J\R13_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=13\n"; r @$t3=13; gc }
.if (@$t0 == 14) { .writemem C:\Users\Geoca\Documents\E007J\R14_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=14\n"; r @$t3=14; gc }
.if (@$t0 == 15) { .writemem C:\Users\Geoca\Documents\E007J\R15_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=15\n"; r @$t3=15; gc }
.if (@$t0 == 16) { .writemem C:\Users\Geoca\Documents\E007J\R16_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=16\n"; r @$t3=16; gc }
.if (@$t0 == 17) { .writemem C:\Users\Geoca\Documents\E007J\R17_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=17\n"; r @$t3=17; gc }
.if (@$t0 == 18) { .writemem C:\Users\Geoca\Documents\E007J\R18_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "E007J_OUT R=18\n"; r @$t3=18; .printf "E007J_CAPTURE_COMPLETE R=18\n"; bc *; .logclose; .detach; q }
gc
