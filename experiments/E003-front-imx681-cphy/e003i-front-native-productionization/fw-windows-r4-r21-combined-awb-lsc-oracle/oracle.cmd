.logopen C:\\Users\\Geoca\\Documents\\E003I-FW-oracle.log
r @$t17=0
r @$t18=0
r @$t19=0
bp QcDeviceMFT8380+0x6bfa68 "$$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E003I-FW\\\\ga.cmd"
bp QcDeviceMFT8380+0x68fa00 "$$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E003I-FW\\\\pub.cmd"
bp QcDeviceMFT8380+0x88e1e8 "$$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E003I-FW\\\\entry.cmd"
bp QcDeviceMFT8380+0xa03b34 "$$><C:\\\\Users\\\\Geoca\\\\Documents\\\\E003I-FW\\\\post.cmd"
.printf "FW_BREAKPOINTS_ARMED R4_R21 COMBINED_AWB_LSC\n"
bl
g
