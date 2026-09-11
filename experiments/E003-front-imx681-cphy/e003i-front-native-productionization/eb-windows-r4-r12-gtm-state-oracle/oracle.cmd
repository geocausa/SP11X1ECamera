.logopen C:\Users\Geoca\Documents\E003I-EB-oracle.log
r @$t2=0
r @$t3=0
bp QcDeviceMFT8380+0x9aa6e0 ".if (@lr == QcDeviceMFT8380+0xa28f2c) { r @$t0=qwo(@x19+0x1ff8); r @$t1=poi(@x0+0x50); $$><C:\\Users\\Geoca\\Documents\\E003I-EB\\entry.cmd } .else { gc }"
bp QcDeviceMFT8380+0xa290a8 "r @$t0=qwo(@x19+0x1ff8); $$><C:\\Users\\Geoca\\Documents\\E003I-EB\\post.cmd"
.printf "EB_BREAKPOINTS_ARMED R4_R12\n"
bl
g
