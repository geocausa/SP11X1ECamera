.logopen C:\\Users\\Geoca\\Documents\\E007N-oracle.log
r @$t5=0
bp QcDeviceMFT8380+0x9241c0 "r @$t5=@$t5+1; r @$t1=1; r @$t0=qwo(@x1+0x1ff8); r @$t3=dwo(@x1+8); $$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E007N\\\\entry.cmd"
bp QcDeviceMFT8380+0x924258 "r @$t5=@$t5+1; r @$t1=2; r @$t0=qwo(@x1+0x1ff8); r @$t3=dwo(@x1+8); $$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E007N\\\\entry.cmd"
.printf "E007N_BREAKPOINTS_ARMED TMC141_CALLSITES_UNFILTERED_INPUT_ONLY\\n"
bl
g
