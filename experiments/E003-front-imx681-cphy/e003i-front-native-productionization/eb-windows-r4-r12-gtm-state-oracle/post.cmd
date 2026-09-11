.if (@$t0 < 4) { gc }
.if (@$t0 > 12) { gc }
.if (@$t0 == @$t3) { gc }
.if (@$t0 == 4) { .writemem C:\Users\Geoca\Documents\E003I-EB\R04_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "EB_OUT R=4\n"; r @$t3=4; gc }
.if (@$t0 == 5) { .writemem C:\Users\Geoca\Documents\E003I-EB\R05_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "EB_OUT R=5\n"; r @$t3=5; gc }
.if (@$t0 == 6) { .writemem C:\Users\Geoca\Documents\E003I-EB\R06_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "EB_OUT R=6\n"; r @$t3=6; gc }
.if (@$t0 == 7) { .writemem C:\Users\Geoca\Documents\E003I-EB\R07_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "EB_OUT R=7\n"; r @$t3=7; gc }
.if (@$t0 == 8) { .writemem C:\Users\Geoca\Documents\E003I-EB\R08_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "EB_OUT R=8\n"; r @$t3=8; gc }
.if (@$t0 == 9) { .writemem C:\Users\Geoca\Documents\E003I-EB\R09_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "EB_OUT R=9\n"; r @$t3=9; gc }
.if (@$t0 == 10) { .writemem C:\Users\Geoca\Documents\E003I-EB\R10_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "EB_OUT R=10\n"; r @$t3=10; gc }
.if (@$t0 == 11) { .writemem C:\Users\Geoca\Documents\E003I-EB\R11_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "EB_OUT R=11\n"; r @$t3=11; gc }
.if (@$t0 == 12) { .writemem C:\Users\Geoca\Documents\E003I-EB\R12_GTM_OUT.bin @x20+0x138 @x20+0x937; .printf "EB_OUT R=12\nEB_CAPTURE_COMPLETE R=12\n"; bc *; .logclose; .detach; q }
gc
