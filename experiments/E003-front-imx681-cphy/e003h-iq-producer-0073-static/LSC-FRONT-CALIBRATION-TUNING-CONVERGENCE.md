# E003h 0073 — front LSC calibration/tuning provenance convergence

Status: **accepted static/offline + historical-dump proof**. No camera runtime and no Linux request6 are performed or authorized.

## Result

The previously separate questions “why does the verified front stream use rear/default-equivalent calibration?” and “why does its live LSC41 interpolation resolve rear/default tuning?” now converge on **one remaining provenance boundary: the verified-front request-private tuning tree**.

The raw calibration source itself remains front-local and physical. `LSC-FRONT-RAW-OTP-PROVENANCE.md` proves that both normal front paths source the IMX681 camera module's physical EEPROM. This proof closes what happens next:

1. the exact front EEPROM name is `gt24p128f_imx681`; rear is `st_m24c64`;
2. neither appears in DeviceMFT's exact 11-entry custom EEPROM-plugin table, so both fall through to generic `EEPROMData` formatting;
3. front and rear use a **byte-identical LSC `lightInfo` descriptor**, SHA `bbe16d16…`, covering four 221-sample u16 planes at raw EEPROM `0x103d..0x1724`;
4. generic `EEPROMData::FormatLSCData` at RVA `0x723e40` directly decodes those raw bytes and has no call to the tuning-tree lookup at RVA `0x6f39f8`;
5. later, `IFELSC411::CheckAndUpdateChromatixData` resolves both `lsc41_ife_v2` **and** `lscgolden41_ife_v2` through the **same request manager/root loaded from `ISPInputData+0x1fe8`**, with both lookup calls targeting RVA `0x6f39f8`.

Therefore there is no hidden front EEPROM plugin or golden substitution inside `FormatLSCData`. The already-proven rear/default live x22 source and rear/default live golden authority are two objects selected from the **same unresolved front request tuning tree**.

## Exact EEPROM READ contracts

The front and rear sensor-module `EEPROMDriverData` objects each contain one `regSetting` READ entry. DeviceMFT's exact `GetMemorySizeBytes` loop tests operation `3` and sums the dereferenced `registerData` value for each such entry.

| Contract | Front IMX681 | Rear OV13858 |
| --- | ---: | ---: |
| EEPROM name | `gt24p128f_imx681` | `st_m24c64` |
| slave | `0xa0` | `0xa0` |
| register address | `0` | `0` |
| register-address type | `2` | `2` |
| register-data type | `1` | `1` |
| operation | `3` (READ) | `3` (READ) |
| READ bytes | **`0x1762`** | **`0x174a`** |
| delay | `0` | `0` |

The front READ byte count is not inferred from the LSC range; it is the exact `registerData` child value in the front serialized memory-map entry. Rear independently carries `0x174a`.

Exact DeviceMFT anchors for the READ-size summation are recorded in the oracle/proof, including RVAs `0x714384..0x714420`.

## Generic formatter identity

The DeviceMFT custom EEPROM table at VA `0x181151f60` contains exactly 11 legacy plugin names. Neither active Surface module name matches it. Both modules therefore execute the same generic formatter sequence after the no-plugin path.

The decisive front/rear LSC `lightInfo` objects are byte-identical:

`bbe16d1678d41c05bb885d4b1680b6be9b86e32e20a67d15576b5a6e764d4599`

They describe:

- light type `3`;
- 221 samples per channel;
- 2-byte advancement per channel/sample;
- u16 pairs beginning at `0x103d`, `0x11f7`, `0x13b1`, `0x156b`;
- one contiguous LSC raw window `0x103d..0x1724` (`0x6e8` bytes).

The WB `lightInfo` objects are also byte-identical, SHA `747eda77…`. This confirms that the two Surface modules intentionally share substantial EEPROM calibration layout; byte similarity alone must not be used as a physical-camera identity test.

## Aug-4 historical cache is conclusively rear

A read-only search of restored Windows found the rear-equivalent 0x6e8 LSC sequence in:

`Windows/LiveKernelReports/NetAdapterCx-20260804-1913.dmp`

Source dump SHA256:

`2ca55e2a058df20936068bd5dfe4c111769ee2d0758c96072adbd3c71a27db40`

The proof parses the ARM64 active-memory `SDMPDUMP` bitmap directly, walks the crash dump's ARM64 page tables using DTB `0x8182b000`, and parses `PsLoadedModuleList` from the captured kernel address space.

The candidate raw buffer maps as:

- source file offset `0x2f78b000`;
- physical address `0x9b2330000`;
- kernel VA `0xffff94826f130000`.

Its durable `0x174a`-byte carve SHA is:

`1d6297455b1afd0184089668020a3b2d99e2758dea30bec1fbda4980a317cd21`

and its LSC subrange `0x103d..0x1724` has SHA:

`679fc75878367f717cea2dbd99f704109adcc48c86b82e7b8ba260cc7eb260fe`

Two independent references classify it as rear:

1. the exact raw pointer is referenced at kernel VA `0xfffff8003945f7e8`. The dump's own loaded-module list places this address inside `surfacecamrearsensor8380.sys`, base `0xfffff80039440000`, size `0x42000`, at **rear-KMD RVA `0x1f7e8`**. The front KMD is separately loaded at `0xfffff80039490000` and does not own this address;
2. a second captured heap object stores the same raw pointer followed immediately by qword **`0x174a`**, the exact rear READ size, while the same page contains `com.surface.tuned.rfc_ov13858.bin` twice.

The generic formatter replay of that raw carve reproduces the preserved rear VSS `0xdf0` LSC calibration slot exactly.

**Conclusion:** this historical raw cache is OV13858/rear. It is explicitly excluded as evidence for the physical front EEPROM bytes.

Minimal retained evidence is under `oracle-aug4-rear-eeprom/` so the 3.23-GB dump does not have to be committed.

## Front raw-byte boundary remains correctly fail-closed

The verified-front x22/x23 equations uniquely determine every direct red/blue value and 218/221 averaged-green pairs. Three green positions each retain two mathematically valid physical `(G1,G2)` pairs, yielding exactly **8 possible raw front LSC byte strings**.

The rear carve happens to select one of those eight combinations, but the historical-dump proof above shows that cache is physically rear. Therefore it must **not** be used to select the front values at those three points.

For parity at the accepted x23 boundary this ambiguity is harmless: Windows averages the two calibrated green channels, and all eight raw candidates are equivalent at the captured x23 output. Physical-front EEPROM identity remains fail-closed unless a future front-specific raw oracle resolves those three pairs.

## One tuning-tree gate, not two provenance problems

At `IFELSC411::CheckAndUpdateChromatixData` RVA `0xa02420`:

- request tuning manager is loaded from `ISPInputData+0x1fe8` at RVA `0xa02448`;
- `lsc41_ife_v2` lookup calls `0x6f39f8` at RVA `0xa024b4`;
- the same manager/root is reloaded for `lscgolden41_ife_v2`;
- golden lookup calls the same `0x6f39f8` at RVA `0xa02534`;
- the same tuning-mode selector array at `ISPInputData+0x2060` is used.

`LSC-TUNING-MANAGER-OWNERSHIP-CLOSURE.md` already proves that this manager comes from the same CaptureDevice private DataManager via CapturePipe/common-context wiring. Random/global rear-manager request injection is excluded on the normal path.

Consequently, the next tuning provenance question is singular:

> **What exact source buffer/tree backs the verified-front CaptureDevice's own private DataManager/TuningDataManager?**

The eventual dynamic oracle, if static parsing cannot close it, remains the tiny correlation of front selected Sensor ID + DataManager `+0x38/+0x30` source bytes + DataManager `+0x28` manager + context `+0x2460` + request `ISPInputData+0x1fe8`.

## Remaining parity gates

This convergence proof does not close front sequential Tintless. The old exact TINTCTX request5→request6 replay remains OV13858 rear mode 1 and cannot satisfy the front gate.

The remaining hard front work is therefore:

1. continue static/private-DataManager tuning-tree provenance mining, with the small live front source-buffer hash oracle only if needed;
2. recover/mine a genuine verified-front sequential Tintless capsule that consumes the proven request4 pre-Tintless mesh `839cae7d…` and reproduces front post-calculation staging;
3. pass one atomic integrated front producer/output replay before a separate Linux request6 authorization review.

Linux request6 remains forbidden.

## Proof artifacts

- `prove-lsc-front-calibration-tuning-convergence.py`
- `lsc-front-calibration-tuning-convergence-oracle.json`
- `oracle-aug4-rear-eeprom/RAW_EEPROM_REAR_174A.bin`
- `oracle-aug4-rear-eeprom/KMD_REAR_REF_PAGE_1000.bin`
- `oracle-aug4-rear-eeprom/HEAP_REAR_REF_PAGE_1000.bin`
- `oracle-aug4-rear-eeprom/metadata.json`
