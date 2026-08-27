# Windows X1E80100 C-PHY table reverse engineering

Local oracle binary (not committed): `qccammipicsi8380.sys`
SHA-256: `033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407`.

PE `.data` raw offset `0xea00` maps to RVA `0x10000`. Disassembly of the Windows C-PHY path passes VA `0x140010c50` (raw file offset `0xf650`) and count `0x79` = 121 to the table writer at `0x140005d00`. Records are three little-endian u32 values: register offset, value, delay field.

The writer stores the value to `[CSIPHY base + offset]`, then converts a nonzero third field with `(delay * 0x10624dd3) >> 38`. The two values present in the 121-record table convert mechanically as:

- `1,000,000 -> 1,000`
- `10,000,000 -> 10,000`

For converted delays above 50, Windows multiplies by `-10` before passing the relative interval to its delay routine, matching 100-ns NT interval units. Therefore the table's third field is nanoseconds and Linux `delay_us` is the field divided by 1000.

The three delayed records become 10,000 us, 1,000 us and 10,000 us respectively. All other records have zero delay.

`extract-windows-cphy-table.py` preserves all 121 records, including duplicate and zero-valued writes. Its last-write-wins map has 118 unique offsets; all 118 match both independent KD live snapshots exactly, with zero mismatches.
