.logopen C:\\Users\\Geoca\\Documents\\E003I-GD-oracle.log
r @$t17=0
r @$t18=0
r @$t19=0
bp QcDeviceMFT8380+0x6bfa68 "$$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E003I-GD\\\\ga.cmd"
bp QcDeviceMFT8380+0x68fa00 "$$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E003I-GD\\\\pub.cmd"
bp QcDeviceMFT8380+0x88e1e8 "$$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E003I-GD\\\\entry.cmd"
bp QcDeviceMFT8380+0xa03b34 "$$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E003I-GD\\\\post.cmd"
.printf "GD_BREAKPOINTS_ARMED R4_R24 COMBINED_AWB_LSC\n"
bl
g
