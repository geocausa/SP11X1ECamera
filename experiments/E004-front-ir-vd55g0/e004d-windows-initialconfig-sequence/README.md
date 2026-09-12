# E004d — Windows VD55G0 InitialConfig sequence authority

Status: **PASS / offline Windows reconstruction only**.

E004d reconstructs the complete first-start VD55G0 InitialConfig transaction captured from the same Surface Pro 11 and proves it is an exact executable representation of the 601-row regSetting in the exact installed Surface sensor package.

No Linux sensor-data write is authorized by E004d.

## Exact authority inputs

- Surface VD55G0 package SHA256: `e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794`
- live Windows first-start InitialConfig packet: 4,880 bytes, SHA256 `81e96e0470cbfa58065eba12ea1a998349b306111f2edee296d7044a69146cdd`
- exact installed `surfacecamauxsensor8380.sys` SHA256: `e5b6b064f39cf239ab07e22ca2434e3c08c93b691dc7d27cebb90861226efa75`
- Linux E004c already proved the physical sensor is model 0x3047 / revision **0x1111 CUT1**.

## Exact Windows command format

The exact aux-driver parser proves the captured packet contains two relevant command forms.

A poll record is 20 bytes. The driver uses:

- byte 0: data type;
- byte 1: address type;
- bytes 2/3: command/opcode signature `01 09`;
- u16 at +4: loop count;
- u16 at +8: register;
- u32 at +12: expected value.

The parser calls its delay helper after a mismatch. That helper multiplies the integer delay by `-10000` and passes the relative interval to `KeDelayExecutionThread`. Windows intervals are 100 ns units, so one loop delay is exactly 1 ms.

A write block has an 8-byte header followed by `count * 8` bytes. The exact driver reads:

- u16 at +0: write count;
- byte +4: data type;
- byte +5: address type;
- each 8-byte entry: u16 register at +0 and u16 data at +4.

For this packet the driver takes its address-type 2 / data-type 1 branch, i.e. 16-bit register address and 8-bit data.

## Complete first-start sequence

The 4,880-byte live packet contains exactly seven commands and maps to all 601 Surface package rows with zero unmatched rows and zero extra packet operations:

1. poll `0x002c == 0x01`, up to 6 x 1 ms;
2. write 553 register entries:
   - 552 contiguous bytes `0x2000..0x2227`, Surface patch SHA256 `5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321`;
   - immediately followed, in the same Windows write command, by `0x0200 = 0x02`;
3. poll `0x0200 == 0x00`, up to 28 x 1 ms;
4. write `0x0200 = 0x01`;
5. poll `0x0200 == 0x00`, up to 6 x 1 ms;
6. poll `0x002c == 0x02`, up to 4 x 1 ms;
7. write 43 post-boot timing/config registers.

The public ST driver is used only as a naming dictionary: it calls `0x0200=2` PATCH_SETUP, `0x0200=1` BOOT, FSM state 1 READY_TO_BOOT and FSM state 2 SW_STBY. Those names do not establish SP11 behavior; the raw sequence above is established by Windows.

## Final Windows configuration facts

The 43-write post-boot block establishes:

- external clock 19.2 MHz;
- MIPI data rate 840 Mbps;
- line length 1200;
- frame length 1955;
- full 644x604 ROI: X 0..643, Y 0..603;
- raw sensor GPIO-control bytes `1,2,1,1`.

ST naming maps GPIO-control value 1 to disabled and value 2 to strobe, so as a **reference-only interpretation** Windows configures sensor GPIO1 to the strobe selector while GPIO0/2/3 use the disabled selector. This does not authorize Linux illumination.

## Verification

Run:

```
python3 experiments/E004-front-ir-vd55g0/e004d-windows-initialconfig-sequence/verify_e004d.py
```

The verifier reparses the exact Surface package, reparses the live packet, replays all 601 rows, checks E004c's real CUT1 result, and disassembles the exact installed aux driver at the parser/write/delay RVAs.

## Next bounded gate

E004e may test only the exact Windows prefix through software standby:

- power/identity/revision checks;
- poll READY_TO_BOOT;
- write the **Surface** 552-byte patch one register transaction at a time;
- write PATCH_SETUP and perform the exact 28 ms poll;
- write BOOT and perform the exact 6 ms poll;
- poll SW_STBY for 4 ms;
- stop there and power off.

The 43 post-boot configuration writes, streaming, CAMSS activation and any external illumination remain prohibited in that prefix experiment.
