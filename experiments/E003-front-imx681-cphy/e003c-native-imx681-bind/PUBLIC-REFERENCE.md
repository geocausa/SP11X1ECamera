# Public IMX681 Linux references used for E003c structure

E003c hardware programming is derived from this SP11 X1E's own Windows oracle and accepted E003b. Public Linux work is used only to avoid reinventing V4L2 sensor-driver structure and to add an independent Sony silicon-ID check.

Public references checked 2026-08-27:

- linux-surface/kernel PR #164, Surface Pro 11 Intel work, head `8ab9347b169233b08950086f49dafd1d58bb5bbf`;
- linux-surface/kernel PR #176, IMX681/SONY0681 RFC, head `0e02f1ca92e365ee723b6bb5312f430e7ef1c379`.

Downloaded reference `imx681.c` SHA-256 values in the local non-repo reference directory:

- PR #164: `346fe6d16f7e130978b3f49f1ca35b671ed06b9a30df908f356ef2046902afb5`;
- PR #176: `b63c8722cf99c2d8989da0615c2ef8a58e55c25ccdd548c7e54190e0d761f362`.

The public RFC checks Sony chip ID register `0x0016` for value `0x0681` and describes the native CFA as RGGB before its Intel-specific H-flip. E003c therefore requires both the SP11 Windows identity (`0x0004 = 0x0aff`) and the independent Sony identity (`0x0016 = 0x0681`). E003c performs no orientation write and advertises native RGGB RAW10 metadata only.

No public transport assumption is reused: the Intel examples are D-PHY. This SP11 X1E's Windows oracle independently proves C-PHY, which remains deliberately absent from E003c.
