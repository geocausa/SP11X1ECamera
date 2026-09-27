/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef CAMSS_E008K_REAR_BRIDGE_H
#define CAMSS_E008K_REAR_BRIDGE_H

#include <linux/types.h>

struct camss;
struct csid_device;
struct v4l2_subdev;
struct media_entity;

int e008k_rear_validate_route(struct camss *camss, struct v4l2_subdev *sensor);
int e008k_rear_rtcdm_open_start(struct camss *camss);
int e008k_rear_rtcdm_submit_bl(struct camss *camss, u32 dma, u16 bytes);
void e008k_rear_rtcdm_stop_close(struct camss *camss);
bool e008k_rear_rtcdm_stopped(struct camss *camss);
int e008k_rear_subdev_stream(struct v4l2_subdev *sd, bool enable);
int e008k_rear_pipeline_pm_get(struct media_entity *entity);
void e008k_rear_pipeline_pm_put(struct media_entity *entity);

bool csid680_e008k_rear_mode0(struct csid_device *csid);
int csid680_e008k_rear_enable(struct csid_device *csid);

int csid680_e008a_rear_quiesce(struct csid_device *csid,
			       bool exact_rear_owner);

#endif
