#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Connect retained public FULL output to the existing two-generation runner."""
from pathlib import Path
import re
def once(t,a,b):
 if t.count(a)!=1:raise RuntimeError("public output anchor drift: "+a[:100])
 return t.replace(a,b,1)
def apply(camss):
 camss=Path(camss)
 names=["camss-vfe-e008d-rear-dma.inc","camss-vfe-e008j-rear-prebus.inc","camss-vfe-e008k-rear-runner.inc","camss-vfe-e008n-rear-single-use.inc","native-rear-startup-entry.inc","native-rear-reclaim.inc"]
 texts={n:(camss/n).read_text() for n in names}
 n=names[0];t=texts[n]
 t=once(t,"\tbool allocated;\n\tbool prepared_disabled;","\tstruct native_rear_video_lease public_full;\n\tbool allocated;\n\tbool prepared_disabled;")
 anchor="static void\ne008d_rear_release_partial("
 full_valid="""static bool __used
native_rear_dma_full_valid(const struct e008d_rear_dma_set *set)
{
 if (!set)
  return false;
 if (set->public_full.acquired)
  return native_rear_video_lease_valid(&set->public_full) && !set->full.cpu &&
         set->full.size == NATIVE_REAR_NV12_BYTES &&
         set->full.dma == set->public_full.span.y_iova;
 return !set->public_full.dbuf && !set->public_full.attachment &&
        !set->public_full.table && set->full.cpu &&
        set->full.size == VFE680_E004NT_REAR_TOTAL_BYTES;
}

"""
 t=once(t,anchor,full_valid+anchor)
 a=t.index(anchor);b=t.index("static int __used\ne008d_rear_dma_alloc",a)
 part=t[a:b]
 part=once(part,"\tunsigned int i;\n","\tunsigned int i;\n\n\t/* Retained public mappings cannot be released by generic VB2 cancel. */\n\tif (set->public_full.acquired &&\n\t    (!native_rear_video_lease_valid(&set->public_full) ||\n\t     (set->public_full.exposed && !set->public_full.stop_proven)))\n\t\treturn;\n")
 part=once(part,"\tmemset(set, 0, sizeof(*set));","\tif (set->public_full.acquired)\n\t\t(void)native_rear_video_lease_put(&set->public_full);\n\tmemset(set, 0, sizeof(*set));")
 t=t[:a]+part+t[b:]
 # Reuse the exact auxiliary allocator/error unwind; FULL is a retained lease.
 a=t.index("static int __used\ne008d_rear_dma_alloc");b=t.index("static int\ne008d_rear_build_addresses",a)
 alloc=t[a:b]
 alloc=once(alloc,"e008d_rear_dma_alloc(struct vfe_device *vfe, struct e008d_rear_dma_set *set)","native_rear_public_dma_alloc(struct vfe_device *vfe,\n struct e008d_rear_dma_set *set, struct camss_buffer *buffer)")
 alloc=once(alloc,"if (set->allocated || set->prepared_disabled || set->full.cpu)","if (set->allocated || set->prepared_disabled || set->full.cpu ||\n\t    set->public_full.acquired)")
 alloc=once(alloc,"\tret = vfe680_e004nt_rear_surface_alloc(vfe, &set->full);","\tret = native_rear_video_lease_get(vfe,\n\t\t&vfe->line[VFE_LINE_PIX].video_out, buffer, &set->public_full);")
 alloc=once(alloc,"\tfor (i = 0; i < E008D_REAR_AUX_COUNT; i++) {","\tset->full.dma = set->public_full.span.y_iova;\n\tset->full.size = NATIVE_REAR_NV12_BYTES;\n\n\tfor (i = 0; i < E008D_REAR_AUX_COUNT; i++) {")
 t=t[:b]+alloc+t[b:]
 old="\tret = vfe680_e004nt_rear_surface_addrs(vfe, &set->full, &full);\n\tif (ret)\n\t\treturn ret;"
 new="""\tif (set->public_full.acquired) {
\t\tif (!native_rear_dma_full_valid(set) || set->full.in_flight)
\t\t\treturn -EINVAL;
\t\tfull = (struct vfe680_e004nt_rear_wm_addrs) {
\t\t\t.y_image = set->public_full.span.y_iova,
\t\t\t.c_image = set->public_full.span.uv_iova,
\t\t};
\t} else {
\t\tret = vfe680_e004nt_rear_surface_addrs(vfe, &set->full, &full);
\t\tif (ret)
\t\t\treturn ret;
\t}"""
 t=once(t,old,new);texts[n]=t
 n=names[1];t=texts[n]
 a=t.index("static int __used\ne008j_rear_alloc_pair_no_mmio");b=t.index("static int __used\ne008j_rear_bind_pair_no_mmio",a)
 alloc=t[a:b]
 alloc=once(alloc,"e008j_rear_alloc_pair_no_mmio(struct vfe_device *vfe,\n\t\t\t      struct e008h_rear_prime_pair *pair)","native_rear_public_pair_alloc(struct vfe_device *vfe,\n struct e008h_rear_prime_pair *pair, struct camss_buffer *buffers[2])")
 alloc=once(alloc,"\tif (!vfe680_e004nt_rear_4k_target(vfe) || !pair)","\tif (!vfe680_e004nt_rear_4k_target(vfe) || !pair || !buffers ||\n\t    !buffers[0] || !buffers[1] || buffers[0] == buffers[1])")
 for s in range(2):
  alloc=once(alloc,f"e008d_rear_dma_alloc(vfe, &pair->dma[{s}])",f"native_rear_public_dma_alloc(vfe, &pair->dma[{s}], buffers[{s}])")
 alloc=once(alloc,"\tret = e008d_rear_build_addresses(vfe, &pair->dma[0], &pair->addr[0]);",
 """\tif (pair->dma[0].public_full.dbuf == pair->dma[1].public_full.dbuf) {
\t\tret = -EADDRINUSE;
\t\tgoto fail;
\t}
\tret = e008d_rear_build_addresses(vfe, &pair->dma[0], &pair->addr[0]);""")
 texts[n]=t[:b]+alloc+t[b:]
 # Propagate only kernel-held buffer pointers; no new register/pointer UAPI.
 for n,structname in [(names[2],"e008k_rear_request"),(names[3],"e008n_rear_request"),(names[4],"native_rear_startup_request")]:
  t=texts[n];a=t.index("struct "+structname+" {");b=t.index("};",a);part=t[a:b]
  part=once(part,"struct v4l2_subdev *sensor;","struct v4l2_subdev *sensor;\n struct camss_buffer *public_video[2];")
  texts[n]=t[:a]+part+t[b:]
 texts[names[3]]=once(texts[names[3]]," dst->sensor = src->sensor;"," dst->sensor = src->sensor;\n dst->public_video[0] = src->public_video[0];\n dst->public_video[1] = src->public_video[1];")
 texts[names[4]]=once(texts[names[4]]," run.sensor = request->sensor;"," run.sensor = request->sensor;\n run.public_video[0] = request->public_video[0];\n run.public_video[1] = request->public_video[1];")
 n=names[2];t=texts[n]
 t=once(t," ret = native_rear_validate_prepared_commands(req->commands);",
 """ if (!!req->public_video[0] != !!req->public_video[1] ||
     (req->public_video[0] && req->public_video[0] == req->public_video[1]))
  return -EINVAL;
 ret = native_rear_validate_prepared_commands(req->commands);""")
 t=once(t,"\tret = e008j_rear_alloc_pair_no_mmio(vfe, pair);",
 """\tif (req->public_video[0])
\t\tret = native_rear_public_pair_alloc(vfe, pair, req->public_video);
\telse
\t\tret = e008j_rear_alloc_pair_no_mmio(vfe, pair);""")
 anchor="\tcsid_streaming = true; /* Configuration may expose CSID even on failure. */\n\thardware_touched = true;"
 t=once(t,anchor,anchor+"""
\tif (req->public_video[0]) {
\t\tret = native_rear_video_lease_expose(&pair->dma[0].public_full);
\t\tif (ret)
\t\t\tgoto out_pin;
\t\tret = native_rear_video_lease_expose(&pair->dma[1].public_full);
\t\tif (ret)
\t\t\tgoto out_pin;
\t}""")
 # On uncertain hardware stop retain the wrapper too, so leases stay tracked.
 t=once(t,"\t\t/* PM ref + DMA stay pinned intentionally until reboot. */\n\t\tkfree(pair);",
 """\t\t/* Retain public mapping descriptors as well as PM/DMA on uncertainty.
\t\t * The caller marks the queue fatal; no subsequent stream may start.
\t\t */\n\t\tif (!req->public_video[0])
\t\t\tkfree(pair);""")
 t=once(t,"\tif (vfe != &camss->vfe[1])\n\t\treturn -EINVAL;",
        "\tif (vfe != &camss->vfe[1])\n\t\treturn -EINVAL;\n\tif (vfe->native_rear_faulted_pair)\n\t\treturn -EBUSY;")
 t=once(t,"\t\tif (!req->public_video[0])\n\t\t\tkfree(pair);",
        "\t\tif (req->public_video[0])\n\t\t\tvfe->native_rear_faulted_pair = pair;\n\t\telse\n\t\t\tkfree(pair);")
 texts[n]=t
 n=names[5];t=texts[n]
 t=once(t,"!set->full.in_flight || !set->full.cpu ||\n            set->full.size != VFE680_E004NT_REAR_TOTAL_BYTES ||",
        "!set->full.in_flight || !native_rear_dma_full_valid(set) ||\n            (set->public_full.acquired && (!set->public_full.exposed ||\n                                          set->public_full.stop_proven)) ||")
 anchor="    for (s = 0; s < E008H_REAR_SLOTS; s++) {\n        pair->dma[s].full.in_flight = false;"
 mark="""    /* Validate all retained leases before releasing any output/aux allocation. */
    for (s = 0; s < E008H_REAR_SLOTS; s++) {
        struct native_rear_video_lease *lease = &pair->dma[s].public_full;
        if (lease->acquired &&
            native_rear_video_lease_stop(lease, result->csid_quiesced,
                result->bus_stopped, result->rtcdm_stopped, result->source_stopped))
            return -EBUSY;
    }

"""
 t=once(t,anchor,mark+anchor);texts[n]=t
 header=(camss/"camss-vfe.h").read_text()
 header=once(header,"struct vfe_device {","struct vfe_device {\n\tstruct e008h_rear_prime_pair *native_rear_faulted_pair;")
 texts["camss-vfe.h"]=header
 for n,t in texts.items():(camss/n).write_text(t)
 return dict(public_FULL_retained_mapping_connected=True,auxiliary_and_command_DMA_remain_owned=True,
             same_ten_WM_consumed_identity_ledger=True,uncertain_exposed_leases_and_wrapper_retained=True,
             source_files=names,ordinary_V4L2_callbacks_connected=False)
