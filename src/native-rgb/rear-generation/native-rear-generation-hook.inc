/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Disposable rear generation/stop qualification. Diagnostic data-only input
 * is compiler-bound to this SP11 candidate, privately generated and SHA-pinned.
 * This is not a product firmware format, userspace command ABI or pixel ISP.
 * No data/profile value or digest is logged. Both output/command DMA and PM
 * remain pinned until reboot on every exposed return, including complete frames.
 */
#include <linux/firmware.h>
#include <crypto/sha2.h>
#include "native-rear-generation-identity.h"

MODULE_FIRMWARE(NATIVE_REAR_GENERATION_FIRMWARE);
static bool native_rear_generation_trial;
module_param(native_rear_generation_trial, bool, 0400);
MODULE_PARM_DESC(native_rear_generation_trial, "Disposable rear two-slot completion proof; mandatory reboot");
static DEFINE_MUTEX(native_rear_generation_lock);
static atomic_t native_rear_generation_consumed = ATOMIC_INIT(0);

bool camss_x1e_rear_generation_trial_allowed(struct camss *camss)
{
 return native_rear_generation_trial && camss && camss->res &&
        camss->res->version == CAMSS_X1E80100 && camss->res->vfe_num > 1;
}

int camss_x1e_rear_generation_once(struct camss_video *video)
{
 struct native_rear_startup_input *input = NULL;
 struct native_rear_startup_result result = {};
 struct native_rear_startup_request request = {};
 const struct firmware *firmware = NULL;
 struct camss *camss;
 struct media_pad *sensor_pad;
 u8 digest[SHA256_DIGEST_SIZE] = {};
 int ret;
 static_assert(sizeof(struct native_rear_startup_input) == NATIVE_REAR_GENERATION_INPUT_BYTES);

 if (!video || !camss_x1e_rear_generation_trial_allowed(video->camss))
  return -EOPNOTSUPP;
 camss = video->camss;
 if (video != &camss->vfe[1].line[VFE_LINE_PIX].video_out)
  return -EINVAL;
 mutex_lock(&native_rear_generation_lock);
 if (atomic_cmpxchg(&native_rear_generation_consumed, 0, 1)) {
  ret = -EALREADY;
  goto out;
 }
 dev_info(camss->dev, "NATIVE_REAR_GENERATION_ATTEMPT identity=12 consumed=1\n");
 if (video->vb2_q.streaming || READ_ONCE(video->x1e_pix_live_active) ||
     READ_ONCE(video->x1e_pix_worker_started) || READ_ONCE(video->x1e_pix_runner_pinned)) {
  ret = -EBUSY;
  goto out;
 }
 sensor_pad = media_pad_remote_pad_first(&camss->csiphy[1].pads[MSM_CSIPHY_PAD_SINK]);
 if (!sensor_pad || sensor_pad->entity->function != MEDIA_ENT_F_CAM_SENSOR) {
  ret = -ENOLINK;
  goto out;
 }
 request.sensor = media_entity_to_v4l2_subdev(sensor_pad->entity);
 ret = e008k_rear_validate_route(camss, request.sensor);
 if (ret)
  goto out;
 ret = request_firmware_direct(&firmware, NATIVE_REAR_GENERATION_FIRMWARE, camss->dev);
 if (ret)
  goto out;
 if (firmware->size != sizeof(*input)) {
  ret = -EINVAL;
  goto out;
 }
 sha256(firmware->data, firmware->size, digest);
 if (memcmp(digest, native_rear_generation_input_sha256, sizeof(digest))) {
  ret = -EBADMSG;
  goto out;
 }
 input = kmemdup(firmware->data, firmware->size, GFP_KERNEL);
 if (!input) {
  ret = -ENOMEM;
  goto out;
 }
 request.input = input;
 request.first_request_generation = 1;
 request.epoch_timeout_us = 500000;
 request.done_timeout_us = 1000000;
 /* Only this synchronous, one-use, exact-profile callback grants permission.
  * Every exposed return is pinned by the unchanged wrapper/runner cleanup.
  */
 WRITE_ONCE(native_rear_diagnostic_active, true);
 ret = native_rear_startup_run_once_unreachable(&camss->vfe[1], &request, &result);
 WRITE_ONCE(native_rear_diagnostic_active, false);
out:
 dev_info(camss->dev,
  "NATIVE_REAR_GENERATION_RESULT ret=%d composed=%u once=%u prepared=%u owner=%llu packets=%u%u%u%u epochs=%u events=%u slot0=%u slot1=%u complete=%u csid_stop=%u bus_stop=%u rtcdm_stop=%u source_stop=%u dma_pinned=%u dma_reclaimed=%u owner_released=%u arena_released=%u reboot=%u\n",
  ret, result.composed, result.once.identity_consumed, result.once.preflight_materialized,
  (unsigned long long)result.once.transaction.owner_epoch,
  result.once.transaction.packet_submitted[0], result.once.transaction.packet_submitted[1],
  result.once.transaction.packet_submitted[2], result.once.transaction.packet_submitted[3],
  result.once.transaction.epoch0_seq, result.once.transaction.done_events,
  result.once.transaction.slot0_enabled, result.once.transaction.slot1_programmed,
  result.once.transaction.both_frames_complete, result.once.transaction.csid_quiesced,
  result.once.transaction.bus_stopped, result.once.transaction.rtcdm_stopped,
  result.once.transaction.source_stopped, result.once.transaction.dma_intentionally_pinned,
  result.once.transaction.dma_reclaimed, result.once.transaction.owner_released,
  result.once.command_arena_released, result.once.reboot_required);
 memzero_explicit(digest, sizeof(digest));
 if (input) {
  memzero_explicit(input, sizeof(*input));
  kfree(input);
 }
 if (firmware)
  release_firmware(firmware);
 mutex_unlock(&native_rear_generation_lock);
 return ret;
}
