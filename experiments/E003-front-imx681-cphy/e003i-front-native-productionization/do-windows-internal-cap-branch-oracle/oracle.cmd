.logopen C:\Users\Geoca\Documents\E003I-DO-oracle.log
r @$t0=0
bp QcDeviceMFT8380+0x3d33e0 ".printf \"DO_PRE n=%u conv=%p out=%p pred=%08x compact98=%08x\\n\", @$t0, @x0, @x1, dwo(@x0+0xd8), dwo(@x1+0x98); .printf \"DO_PRE_LANES\\n\"; dq @x1 L7; gc"
bp QcDeviceMFT8380+0x3d35e4 ".printf \"DO_BRANCH n=%u rc=%u valid=%u w12=%u valueptr=%p minstep=%08x compact98=%08x\\n\", @$t0, @w0, dwo(@sp+0x90), @w12, poi(@sp+0xa0), dwo(poi(@x20+0x138)+0x2c), dwo(@x19+0x98); .if (dwo(@sp+0x90)==1) { .printf \"DO_BANK9_DATA10 n=%u bits=%08x\\n\", @$t0, dwo(poi(@sp+0xa0)+0xc) } .else { .printf \"DO_BANK9_DATA10 n=%u INVALID\\n\", @$t0 }; gc"
bp QcDeviceMFT8380+0x3d363c ".if (@x0 != 0) { .printf \"DO_HISTORY n=%u ptr=%p short=%I64u\\n\", @$t0, @x0, poi(@x0+0x28) } .else { .printf \"DO_HISTORY n=%u NULL\\n\", @$t0 }; gc"
bp QcDeviceMFT8380+0x3d3908 ".printf \"DO_POST n=%u conv=%p out=%p pred=%08x compact98=%08x\\n\", @$t0, @x20, @x19, dwo(@x20+0xd8), dwo(@x19+0x98); .printf \"DO_POST_LANES\\n\"; dq @x19 L7; r @$t0=@$t0+1; .if (@$t0 >= 0n18) { .printf \"DO_CAPTURE_COMPLETE caps=%u\\n\", @$t0; bc *; .logclose; .detach; q } .else { gc }"
.printf "DO_BREAKPOINTS_ARMED\n"
g
