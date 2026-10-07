/* SPDX-License-Identifier: GPL-2.0-only */
/* Typed steady scalars over the existing qualified provider. Startup profile
 * remains a private development dependency; this is not the final product ABI.
 */
#include "native-front-params.h"
static_assert(sizeof(struct native_front_params) == NATIVE_FRONT_PARAMS_BYTES);

void camss_x1e_front_params_clear(struct camss_video *video)
{
 if (!video || READ_ONCE(video->x1e_pix_runner_pinned))
  return;
 mutex_lock(&video->native_params_lock);
 if (video->native_params_profile) {
  memzero_explicit(video->native_params_profile, CAMSS_X1E_PIX_CAPSULE_BYTES);
  kfree(video->native_params_profile);
  video->native_params_profile = NULL;
 }
 mutex_unlock(&video->native_params_lock);
}

static int native_front_params_profile_store(struct camss_video *video,
                                             const u8 *capsule, size_t bytes)
{
 struct camss_x1e_pix_capsule_inputs *inputs;
 u8 *profile;
 int ret;
 if (bytes != CAMSS_X1E_PIX_CAPSULE_BYTES)
  return -EINVAL;
 /* Only the one startup R4 profile crosses the diagnostic raw control. */
 if (get_unaligned_le64(capsule + 0x2c) != 4)
  return -EOPNOTSUPP;
 if (video->vb2_q.streaming || READ_ONCE(video->x1e_pix_live_active))
  return -EBUSY;
 inputs = kzalloc_obj(*inputs, GFP_KERNEL);
 if (!inputs)
  return -ENOMEM;
 ret = camss_x1e_pix_capsule_parse(capsule, bytes, inputs);
 if (!ret && inputs->steady.normalized_main.size != 0x958)
  ret = -EOPNOTSUPP;
 if (!ret)
  ret = native_nv12_commands_validate(inputs->steady.normalized_main.data,
                                     inputs->steady.normalized_main.size, false);
 kfree(inputs);
 if (ret)
  return ret;
 profile = kmemdup(capsule, bytes, GFP_KERNEL);
 if (!profile)
  return -ENOMEM;
 mutex_lock(&video->native_params_lock);
 if (video->native_params_profile) {
  ret = -EBUSY;
 } else {
  video->native_params_profile = profile;
  profile = NULL;
 }
 mutex_unlock(&video->native_params_lock);
 if (profile) {
  memzero_explicit(profile, bytes);
  kfree(profile);
 }
 return ret;
}

int camss_x1e_front_params_submit(struct camss_video *video,
                                const u8 *packet, size_t bytes)
{
 const u8 *section;
 size_t section_bytes;
 u32 values[9][6];
 u8 *capsule = NULL;
 u64 request;
 unsigned int i, j;
 int ret;

 if (!video || !camss_x1e_pix_iq_video(video) ||
     !camss_x1e_native_front_params_trial_allowed(video->camss))
  return -EOPNOTSUPP;
 ret = native_front_params_validate(packet, bytes);
 if (ret)
  return ret;
 if (READ_ONCE(video->x1e_pix_runner_pinned))
  return -EBUSY;
 if (video->vb2_q.streaming &&
     (!READ_ONCE(video->x1e_pix_worker_started) ||
      !READ_ONCE(video->x1e_pix_live_active)))
  return -EBUSY;
 mutex_lock(&video->native_params_lock);
 if (video->native_params_profile) {
  capsule = kmemdup(video->native_params_profile, CAMSS_X1E_PIX_CAPSULE_BYTES,
                    GFP_KERNEL);
  ret = capsule ? 0 : -ENOMEM;
 } else {
  ret = -ENODATA;
 }
 mutex_unlock(&video->native_params_lock);
 if (ret)
  return ret;
 ret = camss_x1e_pix_capsule_section(capsule,
       CAMSS_X1E_PIX_CAPSULE_TYPE_STEADY_MODULES, 0, &section, &section_bytes);
 if (ret || section_bytes != 9 * CAMSS_X1E_PIX_CAPSULE_MODULE_RECORD_BYTES) {
  ret = -EINVAL;
  goto out;
 }
 for (i = 0; i < 9; i++)
  for (j = 0; j < 6; j++)
   values[i][j] = get_unaligned_le32(section +
        i * CAMSS_X1E_PIX_CAPSULE_MODULE_RECORD_BYTES + 4 + 4*j);
 ret = native_front_params_apply(packet, bytes, values);
 if (ret)
  goto out;
 request = native_params_le64(packet + 8);
 put_unaligned_le64(request, capsule + 0x2c);
 for (i = 0; i < 9; i++)
  for (j = 0; j < 6; j++)
   put_unaligned_le32(values[i][j], (u8 *)section +
        i * CAMSS_X1E_PIX_CAPSULE_MODULE_RECORD_BYTES + 4 + 4*j);
 /* The existing FIFO checks monotonic request identity and bounded depth.
  * It owns a copy before this temporary profile-derived capsule is erased.
  */
 ret = camss_x1e_pix_iq_provider_enqueue(video, capsule,
                                        CAMSS_X1E_PIX_CAPSULE_BYTES);
 if (ret) {
  camss_x1e_pix_iq_provider_close(video);
  camss_x1e_pix_iq_provider_purge(video);
 } else {
  dev_info(video->camss->dev, "NATIVE_FRONT_PARAMS_ACCEPT request=%llu mask=%u\n",
           (unsigned long long)request, native_params_le32(packet + 16));
 }
out:
 memzero_explicit(capsule, CAMSS_X1E_PIX_CAPSULE_BYTES);
 kfree(capsule);
 return ret;
}
