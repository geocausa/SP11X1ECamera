.logopen C:\Users\Geoca\Documents\E003I-CQ4-cdb.log
bp 0x7FF9DE5A9F88 ".printf \"CQ4_HIT\\nFINAL_PAIR\\n\"; dd @x20+0x10 L2; .printf \"GAIN_TIME_RAW\\n\"; dd @x20 L4; bc 0; .detach; q"
g
