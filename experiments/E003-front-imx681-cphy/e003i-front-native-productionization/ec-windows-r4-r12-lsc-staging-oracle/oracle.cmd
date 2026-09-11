.logopen C:\Users\Geoca\Documents\E003I-EC-oracle.log
r @$t2=0
bp QcDeviceMFT8380+0xa03b34 "r @$t0=qwo(@x20+0x1ff8); $$><C:\\Users\\Geoca\\Documents\\E003I-EC\\capture.cmd"
.printf "EC_BREAKPOINT_ARMED R4_R12\n"
bl
g
