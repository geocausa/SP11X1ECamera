.logopen C:\\Users\\Geoca\\Documents\\E003I-FX-oracle.log
bp QcDeviceMFT8380+0x6c4234 ".printf \"FX_SELECTOR_HIT x20=%p x19=%p region=%u\\n\",@x20,@x19,@w22; r s8; .writemem C:\\Users\\Geoca\\Documents\\E003I-FX\\CSFSTATDIST-OBJECT.bin @x20 @x20+0x23f; .printf \"FX_SELECTOR_OBJECT_CAPTURED bytes=0x240\\n\"; bc *; .logclose; .detach; q"
.printf "FX_BREAKPOINT_ARMED SELECTOR_CALL=0x6c4234\n"
bl
g
