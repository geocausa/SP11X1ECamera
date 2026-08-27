# E003f preflight — receiver-only X1E C-PHY electrical activation

## Goal

Execute the accepted X1E80100/CSIPHY2 one-trio C-PHY receiver programming for the first time while the IMX681 transmitter remains reset/off and its `s_stream(1)` callback remains hard-blocked.

## Static bug caught before runtime

The exact Windows 121-record C-PHY table programs common offsets `0x102c..0x1054` to 11 non-zero final values. Generic CAMSS code subsequently zeroed common CTRL11..CTRL21 as interrupt masks, which would clobber those 11 Windows values after the table ran.

E003f changes only X1E80100 + C-PHY: preserve the exact table tail instead of applying generic CTRL11..CTRL21 zeroing. D-PHY and every non-X1E path retain existing behaviour.

## Runtime boundary

The test is a separate one-shot module and is not auto-run during initrd boot. After candidate health is established it will:

1. find the live `acb7000.isp` CAMSS platform device and CSIPHY2 directly;
2. require C-PHY, one trio, trio position 0;
3. call only CSIPHY2 `s_power(1)`;
4. call only CSIPHY2 `s_stream(1)`;
5. compare 121 stable live MMIO offsets against both same-machine Windows KD snapshots;
6. call CSIPHY2 `s_stream(0)` and require common CTRL5/CTRL6 to become zero;
7. call CSIPHY2 `s_power(0)` on every exit path.

The harness never calls the IMX681 stream callback and contains no sensor register-write code. IMX681 must remain runtime-suspended/reset-low with front rails and MCLK4 off throughout.

First sensor transmission / MODE_SELECT remains forbidden until a later gate.
