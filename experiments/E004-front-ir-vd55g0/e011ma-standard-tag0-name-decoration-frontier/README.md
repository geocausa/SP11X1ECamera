# E011MA — standard tag 0 name decoration

PASS. The original `0x5DEA14 -> 0x5E07B0` path resolves standard tag 0 to `ColorCorrectionMode` using the original metadata lookup plus `%s%s` formatter. The helper writes only the record `+0x3C` 128-byte name field; numeric/core record bytes remain untouched. This confirms the name path is decoration rather than numeric transport.

NEXT E011MB resumes at `0x5DEA18` and qualifies the numeric/core fields for the first 168-byte standard metadata record.
