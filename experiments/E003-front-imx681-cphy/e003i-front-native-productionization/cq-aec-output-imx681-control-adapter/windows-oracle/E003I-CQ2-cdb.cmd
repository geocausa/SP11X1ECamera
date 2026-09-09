.logopen C:\Users\Geoca\Documents\E003I-CQ2-cdb.log
bp 0x7FF8BB7890C0 ".printf \"CQ2_HIT\\n\"; r w27; dd @x8+0x178 L1; bc 0; .detach; q"
g
