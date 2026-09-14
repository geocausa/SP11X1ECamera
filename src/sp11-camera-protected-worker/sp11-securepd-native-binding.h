/* SPDX-License-Identifier: MIT */
#ifndef SP11_SECUREPD_NATIVE_BINDING_H
#define SP11_SECUREPD_NATIVE_BINDING_H
#include "sp11-securepd-camera-wire.h"

#define SP11_SECUREPD_CAMERA_THREAD_STACK (128u * 1024u)
#define SP11_SECUREPD_CAMERA_THREAD_PRIORITY 0x96u
#define SP11_SECUREPD_MAP_PERMISSION_RW 3u
#define SP11_SECUREPD_PROXY_PACKET_BYTES 96u
#define SP11_SECUREPD_PROXY_RESPONSE_BYTES 8u

int sp11_securepd_native_process_packet(
    const struct sp11_securepd_gaussian_packet *packet,
    sp11_securepd_camera_response_t *response);
void sp11_securepd_camera_worker_thread(void *arg);
void algo_main(void *arg);

#endif
