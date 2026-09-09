.logopen /t C:\Users\Geoca\Documents\E003I-CR63-bank9-cdb.log
.echo CR63_BANK9_ATTACHED
bp 0x7FF9507C5F84 ".if (dwo(@x20+4) == 0x3f) { .echo CR63_BANK9_READ; .printf \"BANK9_BASE=%p SLOT63=%p LUX8=%p\\n\", @x0, @x0+0x3fc, @x0+0x8c; .echo SLOT63_BITS; dd @x0+0x3fc L1; .echo LUX8_BITS; dd @x0+0x8c L1; .echo GETTER_DESCRIPTOR; dd @x20 L4; .echo READ_STACK; kP 20; ba w4 @x0+0x3fc \".echo CR63_BANK9_WRITE; .echo WRITE_PC; r pc; .echo WRITE_REGS; r; .echo WRITE_STACK; kP 28; .echo WRITE_NEAR_PC; ub @pc L10; u @pc L10; bc *; .detach; q\"; bc 0; gc } .else { gc }"
g
