# SP11 VD55G0 safe-42 configuration probe

This diagnostic extends the proven E004f Surface patch/boot prefix while deliberately isolating the Windows illumination-coupled sensor write `0x0468=0x02`.

`generate_windows_header.py` reads the exact local Surface VD55G0 Windows package. It verifies:

- exact package SHA256;
- exact 552-byte Surface patch SHA256;
- exact Windows final 43-write sequence hash;
- exactly one `0x0468=0x02` entry;
- exact 42-write sequence hash after removing that one entry.

The generated header is not committed.

Runtime order:

1. revalidate model 0x3047 / CUT1 0x1111;
2. replay the E004f-proven 554-write patch/setup/boot prefix to SW_STBY;
3. read `0x0468` before final configuration;
4. apply the other 42 Windows final-configuration writes in original order;
5. read `0x0468` again and require it to be byte-identical to the pre-write value;
6. read back transport/timing/exposure/ROI/GPIO configuration groups;
7. require GPIO0/2/3 selector values 1 and require GPIO1 to remain at its pre-write value;
8. remain in SW_STBY and power off.

CAMSS, V4L2, streaming, the isolated strobe-selector write, and external illumination are absent.
