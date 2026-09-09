.logopen C:\Users\Geoca\Documents\E003I-CQ3-cdb.log
bp 0x7FF9E0809838 ".printf \"CQ3_HIT\\n\"; r w24; r w27; r w8; .printf \"PAIR\\n\"; dd @x20+0x10 L2; .printf \"POLICY\\n\"; dd @x19+0xb888 L1; .printf \"EXTRA\\n\"; dd @x19+0xb948 L1; bc 0; .detach; q"
g
