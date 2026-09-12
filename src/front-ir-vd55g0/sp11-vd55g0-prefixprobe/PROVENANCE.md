# SP11 VD55G0 Windows-prefix probe

This diagnostic is derived from the same-machine Windows E004d sequence authority.

The source does not contain a public ST patch and does not commit the Surface patch bytes. Before each build, `generate_surface_patch_header.py` extracts exactly 552 bytes from the exact local Surface Windows package and refuses to proceed unless both the package SHA256 and extracted patch SHA256 match the E004a/E004d authority.

The module replays only the Windows InitialConfig prefix through FSM software-standby:

1. require already-proven model 0x3047 and physical revision 0x1111 CUT1;
2. poll 0x002c == 1 for up to 6 one-millisecond attempts;
3. write 552 Surface patch bytes one 16-bit-address/8-bit-data transaction at a time;
4. write 0x0200 = 2;
5. poll 0x0200 == 0 for up to 28 one-millisecond attempts;
6. write 0x0200 = 1;
7. poll 0x0200 == 0 for up to 6 one-millisecond attempts;
8. poll 0x002c == 2 for up to 4 one-millisecond attempts;
9. stop and power off.

It deliberately omits the final 43 Windows configuration writes. Therefore it does not set the Windows-observed sensor GPIO1 strobe selector, activate CAMSS, register V4L2, stream, or control external illumination.
