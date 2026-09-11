.logopen C:\Users\Geoca\Documents\E003I-FA-oracle.log
r @$t17=0
r @$t19=0
bp QcDeviceMFT8380+0x6bfa68 "$$><C:\\Users\\Geoca\\Documents\\E003I-FA\\ga.cmd"
bp QcDeviceMFT8380+0x68fa00 "$$><C:\\Users\\Geoca\\Documents\\E003I-FA\\pub.cmd"
.printf "FA_BREAKPOINTS_ARMED R4_R12 GA_RVA=6bfa68 PUB_RVA=68fa00\n"
bl
g
