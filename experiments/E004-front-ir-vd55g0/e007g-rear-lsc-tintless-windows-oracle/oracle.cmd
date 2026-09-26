.logopen C:\Users\Geoca\Documents\E007G-oracle.log
r @$t2=0
r @$t3=0
bp QcDeviceMFT8380+0x88e1e8 "r @$t0=qwo(@x1+0x1ff8); r @$t1=poi(@x0+0xa0); r @$t4=@x1+0x2080; $$><C:\\Users\\Geoca\\Documents\\E007G\\entry.cmd"
bp QcDeviceMFT8380+0xa03b34 "r @$t0=qwo(@x20+0x1ff8); $$><C:\\Users\\Geoca\\Documents\\E007G\\post.cmd"
.printf "E007G_BREAKPOINTS_ARMED R4_R18 REAR4K\n"
bl
g
