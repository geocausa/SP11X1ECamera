.printf "E011AQ_BEFORE tid=%x owner=%p io=%p wrapper=%p target=%p actor=%p vtable=%p callback=%p\n",@$tid,@x19,@$t0,@x0,@x15,@$t6,@$t7,@$t8
lm a @$t8
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\BEFORE_BG.bin @$t0+0xcb4 @$t0+0xcb4+0x5b
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\BEFORE_PARAM.bin @x1 @x1+0x27
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\WRAPPER.bin @x0 @x0+0x3f
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\ACTOR.bin @$t6 @$t6+0x3f
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\VTABLE.bin @$t7 @$t7+0x2f
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\CALLBACK_CODE.bin @$t8 @$t8+0x7f
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\RETAINED_BG.bin @$t6+0xfb744 @$t6+0xfb744+0x5b
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\INPUT_LIST.bin poi(@x1+8) poi(@x1+8)+0x4f
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\OUTPUT_LIST.bin poi(@x1+0x18) poi(@x1+0x18)+0x107
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\NESTED_OUTPUT_PAYLOAD.bin poi(poi(@x1+0x18)+0x18) poi(poi(@x1+0x18)+0x18)+0xf
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\NESTED_DESCS.bin poi(poi(poi(@x1+0x18)+0x18)) poi(poi(poi(@x1+0x18)+0x18))+0x167
.writemem C:\Users\Geoca\Documents\SP11CameraPrivate\E011AQ-20260930-1740A\capture\INPUT2_PAYLOAD.bin poi(poi(@x1+8)+0x20) poi(poi(@x1+8)+0x20)+0xb
.printf "E011AQ_BEFORE_CAPTURED\n"
