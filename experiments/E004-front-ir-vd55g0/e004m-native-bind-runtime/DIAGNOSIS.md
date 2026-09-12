# E004m runtime diagnosis — safe pre-sensor abort

The single authorized E004m attempt was consumed and was not retried.

Observed sequence:

1. Candidate boot and inert-client preflight passed.
2. Exact pinned E004k CAMSS module loaded successfully.
3. The acceptance script attempted to read:
   `/sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity`
   as the unprivileged user.
4. The E004k parameter is declared mode `0400`, so its sysfs file is root-readable only.
5. The plain `cat` therefore returned no value; the script interpreted that as `missing` and set the bounded failure flag.
6. Because the failure flag was already set, the native VD55G0 sensor module was never inserted.

Loaded-module identity was checked before returning Golden:

- loaded qcom_camss srcversion: `B7CF41C55172B14CD629043`
- pinned E004k qcom-camss.ko srcversion: `B7CF41C55172B14CD629043`
- stock Golden qcom_camss srcversion: `7FA30D4F4B8441472FBD74C`

Thus the exact pinned CAMSS module did load; this was not an auto-load/stock-module substitution.

Safety outcome:

- native VD55G0 module never loaded;
- no Surface patch/config sensor writes occurred;
- no sensor stream callback occurred;
- no E004j CSIPHY receiver programming marker occurred;
- no capture request occurred;
- no illumination occurred;
- no serious kernel fault occurred;
- SP11 returned to protected Golden and the candidate was retired.

The correction is purely in the next package's acceptance script: read the 0400 CAMSS parameter via `sudo -n cat`. E004m itself remains consumed and is not retried.
