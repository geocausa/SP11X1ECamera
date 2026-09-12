# E003i-HH — clean runtime authority reduction

Status: **PASS OFFLINE / no camera runtime.**

HG proved the IQ producer could be relocated, but still needed an ignored 10.7 MB local authority cache containing raw oracle data and the local IMX681 tuning blob. HH distills that dependency into one **250,690-byte decoded/derived authority file** at `src/front-imx681/userspace/iq/authority/authority.json`.

The authority contains only the runtime state actually needed by the proven algorithms: normalized composer state, selected LSC leaves/golden/OTP values, Tintless configuration/kernel, decoded GainAdj/AWB topology and selector state, and the small CCT/AGW tables. It does not embed the proprietary tuning blob, raw Windows log, or raw request DMI slots.

The proof physically hides **all 80 HG cache inputs** and deletes Python bytecode before executing the stable producer. Two independent clean-runtime replays still reproduce R5..R27 **23/23 byte-exact** against GM. A traced cache-hidden run opens no raw/local authority path, no project-local path outside the stable IQ root, and no camera device.

`build-clean-authority.py` is the offline regeneration bridge from the canonical reverse-engineering evidence. The shipped runtime does not require those generator inputs. The clean authority is currently pinned to this proven SP11 unit/profile; generalizing physical per-device OTP acquisition for other units is a later production concern.
