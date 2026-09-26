.logopen C:\Users\Geoca\Documents\E007L-oracle.log
r @$t2=0
r @$t3=0
bp QcDeviceMFT8380+0x9255f0 ".if ((@lr == QcDeviceMFT8380+0x9241c4) || (@lr == QcDeviceMFT8380+0x92425c)) { r @$t0=qwo(@x1+0x1ff8); $$><C:\\Users\\Geoca\\Documents\\E007L\\entry.cmd } .else { gc }"
bp QcDeviceMFT8380+0x9241c4 "$$><C:\\Users\\Geoca\\Documents\\E007L\\post.cmd"
bp QcDeviceMFT8380+0x92425c "$$><C:\\Users\\Geoca\\Documents\\E007L\\post.cmd"
.printf "E007L_BREAKPOINTS_ARMED R4_R18 TMC141_SOLVER\n"
bl
g
