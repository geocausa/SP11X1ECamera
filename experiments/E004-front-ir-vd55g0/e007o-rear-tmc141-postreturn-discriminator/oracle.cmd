.logopen C:\Users\Geoca\Documents\E007O-oracle.log
r @$t5=0
r @$t4=0
bp QcDeviceMFT8380+0x9241c0 "r @$t5=@$t5+1; r @$t1=1; r @$t4=@x2; r @$t0=dwo(@x1+8); $$><C:\\Users\\Geoca\\Documents\\E007O\\entry.cmd"
bp QcDeviceMFT8380+0x924258 "r @$t5=@$t5+1; r @$t1=2; r @$t4=@x2; r @$t0=dwo(@x1+8); $$><C:\\Users\\Geoca\\Documents\\E007O\\entry.cmd"
bp QcDeviceMFT8380+0x9241c4 "$$><C:\\Users\\Geoca\\Documents\\E007O\\post.cmd"
bp QcDeviceMFT8380+0x92425c "$$><C:\\Users\\Geoca\\Documents\\E007O\\post.cmd"
.printf "E007O_BREAKPOINTS_ARMED TMC141_PREPOST_FIRST20\n"
bl
g
