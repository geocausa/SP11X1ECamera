.printf "E011AQ_POPULATE tid=%x tidMatch=%u actorMatch=%u payloadMatch=%u count=%u\n",@$tid,(@$tid==@$t1),(@x0==@$t6),(@x1==poi(@$t0+0x2238+0x18)),dwo(@x1+8)
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\POP_SOURCE_BG.bin @x0+0xfb744 @x0+0xfb744+0x5b
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\POP_BEFORE_BG.bin @$t0+0xcb4 @$t0+0xcb4+0x5b
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\POP_PAYLOAD.bin @x1 @x1+0xf
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\POP_DESCS.bin poi(@x1) poi(@x1)+0x167
g
