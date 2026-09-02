# E003h 0073 — live LSC golden authority closure

Status: **accepted offline forensic/static closure**. No Linux camera runtime and no Linux request6 were performed.

## Result

The recovered verified-front LSCTRIGSRC request5/request6 calibrated buffers uniquely identify the live `lscgolden41_ife_v2` authority as the **rear/default OV13858 tuning package**, not the nominal IMX681 package.

Live golden authority:

- tuning: `com.surface.tuned.rfc_ov13858.bin`
- tuning SHA-256: `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`
- `lscgolden41_ife_v2` region SymbolTableID: **`0x2ae`**
- region SHA-256: **`f771e54d183281251bf0ef6d94e94a0d439c641f8b8ed9a3ad60ead4094487d6`**

This is the same kind of tuning crossover already proved for the live front LSC41 x22 source. It does **not** mean the physical sensor is rear: independent sensor programming and front geometry still identify the verified stream as IMX681.

## Why the discriminator is exact

The raw NTFS carve recovered both sides of the calibration transform for two verified-front requests:

- req5 x22 `e35ad052…` → x23 `94cbaac5…`
- req6 x22 `3acd68d8…` → x23 `62b39d4e…`

Exact DeviceMFT calibration code has already proved the direct-channel operation:

`x23 = float32(float32(golden / float32(EEPROM_u16)) * x22)`

The two green planes are intentionally excluded from this authority test because Windows calibrates them independently and then averages them. Red plane 0 and blue plane 3 remain direct transforms, yielding **442 independent mesh positions**.

For every installed tuning blob containing `lscgolden41_ife_v2`, the proof searches the complete positive u16 EEPROM domain (`1..65535`). At each red/blue point it requires one integer EEPROM value that reproduces **both request5 and request6** calibrated float32 results bit-for-bit.

The rear/default OV13858 golden is the only candidate that survives:

- **442/442 pass**
- **442/442 unique integer solutions**
- **0 failures**
- inferred direct-channel EEPROM values span **181..1023**

The nominal IMX681 golden region SHA `b0023db8…` satisfies only **9/442** direct constraints and fails **433**.

All other installed platform/default/aux/front/rear-variant goldens also fail hundreds of positions. `lsc-live-golden-authority-oracle.json` records the exhaustive candidate table.

## Calibration-boundary correction

`LSC-CALIBRATION-APPLICATION-BOUNDARY.md` remains valid for:

- resolving a `lscgolden41_ife_v2` object;
- formatted EEPROM slot layout;
- `golden / EEPROM` ratio direction;
- Windows two-green averaging;
- application before geometry and Tintless.

Its previously decoded **nominal front IMX681 golden object** was a static package fact, not proof that the live verified-front request used that object. The recovered x22/x23 equations now supersede that provenance assumption and pin the live golden to rear/default OV13858.

## Combined live tuning picture

For the verified IMX681 physical stream:

- LSC41 generic x22 source: rear/default OV13858 `lsc41_ife_v2` regions `0x2a0/0x2a4`;
- LSC calibration golden: rear/default OV13858 `lscgolden41_ife_v2` region `0x2ae`;
- physical sensor/mode: still IMX681, independently proved;
- remaining upstream provenance question: why the front CaptureDevice's private DataManager/tree resolves these rear/default LSC objects despite front SCFG/KMD selection.

This strengthens, rather than weakens, the narrow live-DataManager provenance question.

Proof artifacts:

- `prove-lsc-live-golden-authority.py`
- `lsc-live-golden-authority-oracle.json`
- carved x22/x23 bytes under `oracle-carved-20260902/`

Linux request6 remains fail-closed and unauthorized.
