.logopen C:\\Users\\Geoca\\Documents\\E007M-oracle.log
r @$t2=0
bp QcDeviceMFT8380+0x9241c0 "r @$t1=1; r @$t0=qwo(@x1+0x1ff8); $$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E007M\\\\entry.cmd"
bp QcDeviceMFT8380+0x924258 "r @$t1=2; r @$t0=qwo(@x1+0x1ff8); $$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E007M\\\\entry.cmd"
.printf "E007M_BREAKPOINTS_ARMED R4_R18 TMC141_CALLSITES_INPUT_ONLY\\n"
bl
g
