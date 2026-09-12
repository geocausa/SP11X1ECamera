# E003i-HI — production launcher and stable device discovery

Status: **PASS OFFLINE / no camera runtime.**

HI moves the stable HH runtime one step closer to ordinary use without changing the proven 27-frame camera algorithm. The production capture helper is generated deterministically from the frozen HC helper with one safety feature: **post-G3 physical sensor writes default to `shadow`**. The existing HA one-write cap-release path can only be enabled by the explicit `cap-release-one-shot` policy, and the launcher requires an additional `--allow-one-native-write` acknowledgement when execution is requested.

Device discovery no longer pins the IMX681 I2C entity or `/dev/videoN`/`/dev/v4l-subdevN` numbers. Five archived live topologies are replayed, including the real entity drift from `imx681 3-0010` to `imx681 4-0010`; a synthetic test also renumbers the sensor to `9-0010`, the subdev to 31 and video to 12. Discovery still pins the already-proven X1E pipeline entity identities (`msm_csiphy2 -> msm_csid1 -> msm_vfe1_pix -> msm_vfe1_video3`) rather than selecting an unproven route.

The launcher is dry-run by default. An offline traced dry run opens no camera device. The accepted template-free R4 bootstrap is stored as a derived 41,088-byte production asset with its known SHA. Stable userspace builds are deterministic on the protected host toolchain.

HI does **not** claim repeated-stream robustness or production-native post-G3 feedback. The latter remains parked behind the brighter-diffuse-real-scene gate.
