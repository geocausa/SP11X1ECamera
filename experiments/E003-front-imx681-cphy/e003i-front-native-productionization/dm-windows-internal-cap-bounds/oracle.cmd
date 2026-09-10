.logopen C:\Users\Geoca\Documents\E003I-DM-oracle.log
r @$t0=0
r @$t3=0
bp QcDeviceMFT8380+0x3ce03c ".printf \"DM_PRE n=%u conv=%p out=%p bounds=%p pred=%08x flag=%08x\n\", @$t0, @x19, @x20, poi(@x19+0x98), dwo(@x19+0xd8), dwo(@x20+0x98); r @$t1=@x19; r @$t2=@x20; .printf \"DM_COMPACT_PRE\n\"; dq @x20 L7; .printf \"DM_BOUNDS_238\n\"; dq poi(@x19+0x98) L47; gc"
bp QcDeviceMFT8380+0x3ce040 ".printf \"DM_POST n=%u conv=%p out=%p pred=%08x\n\", @$t0, @x19, @x20, dwo(@x19+0xd8); .printf \"DM_COMPACT_POST\n\"; dq @x20 L7; r @$t0=@$t0+1; gc"
bp QcDeviceMFT8380+0x375170 ".printf \"DM_REQUEST n=%u frame=%I64u out=%p capflag=%u\n\", @$t0, poi(@x19+0x165d0), @x19+0x14cf8, dwo(@x19+0x14d9c); r @$t3=@$t3+1; .if (@$t3 >= 12) { .printf \"DM_CAPTURE_COMPLETE caps=%u requests=%u\n\", @$t0, @$t3; bc *; .logclose; .detach; q } .else { gc }"
.printf "DM_BREAKPOINTS_ARMED\n"
g
