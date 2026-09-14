# SP11 protected camera worker — offline canonical source

This directory is the maintained **offline-only** source for the Windows-exact protected camera transfer worker recovered through E004dg/E004dh/E004dj.

It is not a production-loadable SecurePD module. It is deliberately unsigned, unadmitted and has no runtime launcher. `build-offline.sh` performs only host-side algorithm/wire tests and an offline Hexagon-v73 relocatable partial link.

The final path reuses Qualcomm's shipped 96-byte Gaussian/loadalgo proxy contract unchanged. The camera control prefix occupies the first 32 bytes of protected HEAP; the worker uses the proven parity core and Windows-exact SWABF/SWASF implementation. The canonical build must reproduce combined Hexagon object SHA-256:

`4d413d54fb29d898b0a662edcc957eb02ccf4769e7036aa4c986b0c8be6afc48`

and exactly ten unresolved imports, all of which are imported by the shipping Qualcomm SecurePD example image:

`dsc_verify_buffer`, `get_secure_channel_handle`, `qurt_sleep`, `secure_pd_mapping_create_64`, `secure_pd_mapping_delete_64`, `secure_pd_mb_delete`, `secure_pd_mb_get`, `secure_pd_mb_receive`, `secure_pd_mb_send`, `secure_pd_thread_create`.

Full-frame verification against the pinned 644x604 Windows oracle must remain zero-difference for luma and the neutral UV tail.

## Security boundary

E004de/E004df proved that the production SP11 CDSP trust policy exposes no legitimate source-controlled admission route for a new camera parity worker with the credentials/material available to this project. Do **not** patch signature verification, enable a test/debug trust root, alter root firmware, or claim this object is loadable. If a legitimate Qualcomm/Microsoft/OEM production signing/admission route becomes available later, this source is ready for that independent step.
