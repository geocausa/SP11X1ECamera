/* SPDX-License-Identifier: GPL-2.0-only */
#include <linux/firmware.h>
#include <crypto/sha2.h>
#include "native-front-profile.h"
MODULE_FIRMWARE(NATIVE_FRONT_PROFILE_FIRMWARE);

static int native_front_profile_load(struct camss_video *video)
{
 const struct firmware *firmware;
 u8 digest[SHA256_DIGEST_SIZE];
 u8 *capsule;
 int ret;
 bool present;

 if (!camss_x1e_native_front_profile_trial_allowed(video->camss))
  return 0;
 mutex_lock(&video->native_params_lock);
 present = video->native_params_profile != NULL;
 mutex_unlock(&video->native_params_lock);
 if (present)
  return 0;
 if (video->vb2_q.streaming || READ_ONCE(video->x1e_pix_live_active) ||
     READ_ONCE(video->x1e_pix_worker_started))
  return -EBUSY;
 /* Direct filesystem load: no executable firmware or userspace fallback helper.
  * The board/mode name and admitted digest are fixed in the driver.
  */
 ret = request_firmware_direct(&firmware, NATIVE_FRONT_PROFILE_FIRMWARE,
                               video->camss->dev);
 if (ret)
  return ret;
 if (firmware->size != NATIVE_FRONT_PROFILE_BYTES) {
  ret = -EINVAL;
  goto out_release;
 }
 sha256(firmware->data, firmware->size, digest);
 ret = native_front_profile_validate(firmware->data, firmware->size, digest);
 if (ret)
  goto out_release;
 capsule = kzalloc(CAMSS_X1E_PIX_CAPSULE_BYTES, GFP_KERNEL);
 if (!capsule) {
  ret = -ENOMEM;
  goto out_release;
 }
 ret = native_front_profile_materialize(firmware->data, firmware->size, digest,
                                       capsule, CAMSS_X1E_PIX_CAPSULE_BYTES);
 if (!ret)
  ret = native_front_params_profile_store(video, capsule,
                                          CAMSS_X1E_PIX_CAPSULE_BYTES);
 if (!ret)
  ret = camss_x1e_pix_iq_provider_open(video,
                                      CAMSS_X1E_PIX_IQ_FIRST_STEADY_REQUEST);
 if (!ret)
  ret = camss_x1e_pix_iq_provider_enqueue(video, capsule,
                                          CAMSS_X1E_PIX_CAPSULE_BYTES);
 if (ret) {
  camss_x1e_pix_iq_provider_close(video);
  camss_x1e_pix_iq_provider_purge(video);
  camss_x1e_front_params_clear(video);
 } else {
  dev_info(video->camss->dev,
           "NATIVE_FRONT_PROFILE_LOADED data_only=1 raw_control=0\n");
 }
 memzero_explicit(capsule, CAMSS_X1E_PIX_CAPSULE_BYTES);
 kfree(capsule);
out_release:
 memzero_explicit(digest, sizeof(digest));
 release_firmware(firmware);
 return ret;
}
