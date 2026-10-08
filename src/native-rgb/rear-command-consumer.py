"""Bind the retained rear semantic producer to its prepared-command consumer.

Only source composition; historical files are never edited and runtime remains
denied. All anchors are checked so a changed parent cannot be silently adapted.
"""
from pathlib import Path

def replace_once(text, before, after):
    if text.count(before) != 1:
        raise ValueError("rear prepared-consumer parent drift: " + before[:90])
    return text.replace(before, after, 1)

def apply(camss):
    camss = Path(camss)
    here = Path(__file__).resolve().parent
    (camss / "native-rear-prepared-commands.inc").write_bytes(
        (here / "native-rear-prepared-commands.inc").read_bytes())
    for name in ("native-rear-startup-scalars.h", "native-rear-scalar-binding.inc",
                 "native-rear-startup-geometry.inc", "native-rear-startup-statistics.inc",
                 "native-rear-startup-iq.inc", "native-rear-startup-compose.inc",
                 "native-rear-startup-entry.inc", "native-rear-pix-link.h",
                 "native-rear-csid-config.inc", "native-rear-vfe-config.inc"):
        (camss / name).write_bytes((here / name).read_bytes())
    # Find the exact required PIX video edge; metadata fan-out makes first-link
    # lookup order-dependent. Preserve the pinned original bridge as authority.
    path = camss / "camss-e008k-rear-rtcdm-bridge.inc"
    text = path.read_text()
    text = replace_once(text, '#include "camss-e008k-rear-bridge.h"',
                        '#include "camss-e008k-rear-bridge.h"\n'
                        '#include "native-rear-pix-link.h"')
    text = replace_once(text,
        "\tif (!camss_x1e_pix_link(&vfe->line[VFE_LINE_PIX].pads[MSM_VFE_PAD_SRC],\n"
        "\t\t\t\t&vfe->line[VFE_LINE_PIX].video_out.vdev.entity, 0))",
        "\tif (!native_rear_required_pix_video_link(\n"
        "\t\t&vfe->line[VFE_LINE_PIX].pads[MSM_VFE_PAD_SRC],\n"
        "\t\t&vfe->line[VFE_LINE_PIX].video_out.vdev.entity.pads[0]))")
    path.write_text(text)
    path = camss / "camss-e008k-rear-bridge.h"
    text = path.read_text()
    text = replace_once(text, "int csid680_e008k_rear_enable(struct csid_device *csid);",
        "int csid680_native_rear_configure(struct csid_device *csid);\n"
        "int csid680_native_rear_after_packet0_configure(struct csid_device *csid);\n"
        "int csid680_e008k_rear_enable(struct csid_device *csid);")
    path.write_text(text)
    path = camss / "camss-csid-680.c"
    text = replace_once(path.read_text(), '#include "camss-csid-e008k-rear-bridge.inc"',
        '#include "native-rear-csid-config.inc"\n#include "camss-csid-e008k-rear-bridge.inc"')
    text = replace_once(text,
        "\tval = CSID_RESET_CMD_HW_RESET | CSID_RESET_CMD_SW_RESET;",
        "\tval = native_rear_csid_reset_command(csid);")
    text = replace_once(text, "\twritel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);\n\n\t/* preserve registers */",
        "\tnative_rear_csid_route_before_reset(csid);\n"
        "\twritel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);\n\n\t/* preserve registers */")
    path.write_text(text)
    # Adopt validated inactive-cold-gamma derivatives; immutable parents retained.
    cold = here.parents[1] / "experiments/E004-front-ir-vd55g0/e011as-rear-explicit-inactive-cold-gamma"
    for original, replacement in (
        ("camss-e006g-rear-materializer.inc", "camss-e011as-e006g-rear-materializer.inc"),
        ("camss-e007e-bfstats25-dmi.inc", "camss-e011as-e007e-bfstats25-dmi.inc"),
        ("camss-e007f-dmi-integration.inc", "camss-e011as-e007f-dmi-integration.inc"),
        ("camss-e011as-cold-gamma-policy.inc", "camss-e011as-cold-gamma-policy.inc"),
    ):
        (camss / original).write_bytes((cold / replacement).read_bytes())
    path = camss / "camss-vfe-e008l-rear-command-dma.inc"
    text = path.read_text()
    text = replace_once(text, "\tbool allocated;\n\tbool hardware_exposed;\n};",
                        "\tbool allocated;\n\tbool hardware_exposed;\n\tbool prepared;\n\tu64 packet_request_id[E007Y_STARTUP_PACKETS];\n};")
    text = replace_once(text, "if (!p->allocated || p->submitted || !p->out.bl_count)",
                        "if (!set->prepared || !p->allocated || p->submitted || !p->out.bl_count)")
    path.write_text(text)

    path = camss / "camss-vfe-e008k-rear-runner.inc"
    text = path.read_text()
    text = replace_once(text, "\tstruct e007d_rear_register_state *regs;\n\tstruct e007v_rear_dmi_state *dmi_state;\n\tstruct e007y_rear_startup_output packet[E007Y_STARTUP_PACKETS];",
                        "\tstruct e008l_rear_command_set *commands;")
    a = text.index("static int\ne008k_rear_materialize_all(")
    b = text.index("static int\ne008k_rear_collect_done(", a)
    text = text[:a] + "static int\ne008k_rear_validate_prepared_packets(struct e008k_rear_request *req)\n{\n unsigned int p;\n int ret;\n if (!req || !req->sensor || !req->commands || !req->first_request_generation ||\n     req->first_request_generation == U64_MAX)\n  return -EINVAL;\n ret = native_rear_validate_prepared_commands(req->commands);\n if (ret)\n  return ret;\n for (p = 0; p < E007Y_STARTUP_PACKETS; p++)\n  if (req->packet_request_id[p] != req->commands->packet_request_id[p])\n   return -ESTALE;\n return 0;\n}\n\n" + text[b:]
    text = replace_once(text, "e008k_rear_materialize_all(req)", "e008k_rear_validate_prepared_packets(req)")
    for p in range(4):
        text = replace_once(text, f"&req->packet[{p}]", f"&req->commands->packet[{p}].out")
    anchor = "static int __used\ne008k_rear_run_unreachable("
    text = replace_once(text, anchor, "static int e008k_rear_runtime_authorization(void);\n\n" + anchor)
    anchor = "\tpair = kzalloc(sizeof(*pair), GFP_KERNEL);"
    text = replace_once(text, anchor,
                        "\t/* The prepared handoff does not grant rear hardware access. */\n"
                        "\tret = e008k_rear_runtime_authorization();\n\tif (ret)\n\t\treturn ret;\n\n" + anchor)
    # Reset powers CSID but rear lacks the front-only transport builder.
    # Configure only transport before packet0; packet-owned fields are untouched.
    text = replace_once(text,
        "\tret = csid680_e008i_rear_reset(csid, owner_epoch);\n\tif (ret)\n\t\tgoto out_clean_power;",
        "\tret = csid680_e008i_rear_reset(csid, owner_epoch);\n\tif (ret)\n\t\tgoto out_clean_power;\n\n"
        "\tcsid_streaming = true; /* Configuration may expose CSID even on failure. */\n"
        "\thardware_touched = true;\n\tret = csid680_native_rear_configure(csid);\n"
        "\tif (ret)\n\t\tgoto out_pin;")
    text = replace_once(text,
        "\t\t/* PM ref + DMA stay pinned intentionally until reboot. */",
        "\t\tresult->dma_intentionally_pinned = true;\n"
        "\t\t/* PM ref + DMA stay pinned intentionally until reboot. */")
    # A failed start may already have exposed hardware. Mark before attempting
    # each operation so emergency stop/pinning covers partial-start failures.
    text = replace_once(text,
        "\tret = e008k_rear_rtcdm_open_start(camss);\n\tif (ret)\n\t\tgoto out_pin;\n\trtcdm_started = true;\n\thardware_touched = true;",
        "\trtcdm_started = true; /* May expose hardware even on failure. */\n"
        "\thardware_touched = true;\n\tret = e008k_rear_rtcdm_open_start(camss);\n"
        "\tif (ret)\n\t\tgoto out_pin;")
    text = replace_once(text,
        "\tret = e008j_rear_prepare_slot0_after_packet0(vfe, pair);\n\tif (ret)\n\t\tgoto out_pin;\n\tbus_may_be_enabled = true; /* MMIO is now exposed; pin on all failures. */",
        "\tbus_may_be_enabled = true; /* Preparation may partially write BUS. */\n"
        "\tret = e008j_rear_prepare_slot0_after_packet0(vfe, pair);\n"
        "\tif (ret)\n\t\tgoto out_pin;")
    text = replace_once(text,
        "\tret = csid680_e008k_rear_enable(csid);\n\tif (ret)\n\t\tgoto out_pin;\n\tcsid_streaming = true;",
        "\tcsid_streaming = true;\n\tret = csid680_e008k_rear_enable(csid);\n"
        "\tif (ret)\n\t\tgoto out_pin;")
    text = replace_once(text,
        "\tret = e008k_rear_subdev_stream(&csiphy->subdev, true);\n\tif (ret)\n\t\tgoto out_pin;\n\tcsiphy_streaming = true;",
        "\tcsiphy_streaming = true;\n\tret = e008k_rear_subdev_stream(&csiphy->subdev, true);\n"
        "\tif (ret)\n\t\tgoto out_pin;")
    text = replace_once(text,
        "\tret = e008k_rear_subdev_stream(req->sensor, true);\n\tif (ret)\n\t\tgoto out_pin;\n\tsensor_streaming = true;",
        "\tsensor_streaming = true;\n\tret = e008k_rear_subdev_stream(req->sensor, true);\n"
        "\tif (ret)\n\t\tgoto out_pin;")
    # Shared IFE1 core/IRQ prefix and compressed BUS setup are not IQ packets.
    text = replace_once(text,
        "\tbus_may_be_enabled = true; /* Preparation may partially write BUS. */",
        "\tbus_may_be_enabled = true; /* Core prefix may expose BUS on failure. */\n"
        "\tret = native_rear_vfe_configure(vfe);\n\tif (ret)\n\t\tgoto out_pin;")
    text = replace_once(text, "\tret = native_rear_vfe_configure(vfe);", "\tret = csid680_native_rear_after_packet0_configure(csid);\n\tif (ret)\n\t\tgoto out_pin;\n\tret = native_rear_vfe_configure(vfe);")
    path.write_text(text)

    path = camss / "camss-vfe-e008n-rear-single-use.inc"
    text = path.read_text()
    anchor = "struct e008n_rear_request {"
    proto = ("struct e008o_rear_semantic_set;\n"
             "static int e008o_rear_materialize_commands(struct e008o_rear_semantic_set *,\n"
             "                                         struct e008l_rear_command_set *);\n"
             "static int e008o_rear_runtime_authorization(void);\n\n")
    text = replace_once(text, anchor, proto + anchor)
    text = replace_once(text,
       "\tstruct e007d_rear_register_state *regs;\n\tstruct e007v_rear_dmi_state *dmi_state;\n\tu64 packet_request_id[E007Y_STARTUP_PACKETS];",
       "\tstruct e008o_rear_semantic_set *semantics;")
    a = text.index("static void\ne008n_rear_fill_kreq(")
    b = text.index("/*\n * This wrapper", a)
    text = text[:a] + "static void\ne008n_rear_fill_kreq(struct e008k_rear_request *dst,\n                    struct e008n_rear_request *src,\n                    struct e008l_rear_command_set *commands)\n{\n unsigned int p;\n memset(dst, 0, sizeof(*dst));\n dst->sensor = src->sensor;\n dst->commands = commands;\n dst->first_request_generation = src->first_request_generation;\n dst->epoch_timeout_us = src->epoch_timeout_us;\n dst->done_timeout_us = src->done_timeout_us;\n for (p = 0; p < E007Y_STARTUP_PACKETS; p++)\n  dst->packet_request_id[p] = commands->packet_request_id[p];\n}\n\n" + text[b:]
    text = replace_once(text, "\te008n_rear_fill_kreq(&kreq, req, commands);\n\n", "")
    text = replace_once(text, "\tret = e008k_rear_materialize_all(&kreq);",
       "\tret = e008o_rear_materialize_commands(req->semantics, commands);\n"
       "\tif (ret)\n\t\tgoto out_release_clean;\n"
       "\te008n_rear_fill_kreq(&kreq, req, commands);\n"
       "\tret = e008k_rear_validate_prepared_packets(&kreq);")
    text = replace_once(text, "\tresult->preflight_materialized = true;",
       "\tresult->preflight_materialized = true;\n\n"
       "\t/* An offline-valid arena is not hardware authorization. */\n"
       "\tret = e008o_rear_runtime_authorization();\n"
       "\tif (ret)\n\t\tgoto out_release_clean;")
    text = replace_once(text, "out_release_clean:\n\t(void)e008l_rear_command_release(vfe, commands, false);",
        "out_release_clean:\n\t{\n"
        "\t\tint release_ret = e008l_rear_command_release(vfe, commands, false);\n"
        "\t\tif (release_ret) {\n\t\t\tresult->reboot_required = true;\n"
        "\t\t\treturn release_ret;\n\t\t}\n"
        "\t\tresult->command_arena_released = true;\n\t}\n")
    text = text.replace("E008k repeats these checks; that duplication is intentional so the",
                        "E008k revalidates prepared ownership without rewriting bytes; the")
    path.write_text(text)

    path = camss / "camss-vfe-e008o-rear-semantic-state.inc"
    text = path.read_text()
    # Preserve the current prepared-command materializer, adopt activity validation.
    derivative = (cold / "camss-e011as-vfe-e008o-rear-semantic-state.inc").read_text()
    begin = "static int\ne008o_rear_validate_packet_semantics("
    end = "static int\ne008o_rear_validate_semantic_set("
    text = text[:text.index(begin)] + derivative[derivative.index(begin):derivative.index(end)] + text[text.index(end):]
    a = text.index("static int\ne008o_rear_materialize_commands(")
    b = text.index("struct e008o_rear_semantic_ops {", a)
    text = text[:a] + "static int\ne008o_rear_materialize_commands(struct e008o_rear_semantic_set *set,\n                                 struct e008l_rear_command_set *commands)\n{\n unsigned int p;\n int ret;\n if (!commands || !commands->allocated || commands->prepared ||\n     commands->hardware_exposed)\n  return -EINVAL;\n for (p = 0; p < E007Y_STARTUP_PACKETS; p++)\n  if (!commands->packet[p].allocated || commands->packet[p].submitted)\n   return -EINVAL;\n ret = e008o_rear_validate_semantic_set(set);\n if (ret)\n  return ret;\n for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {\n  struct e007y_rear_startup_output *out = e008l_rear_command_output(commands, p);\n  struct e008o_rear_packet_semantics *s = &set->packet[p];\n  ret = e007y_rear_materialize(&s->regs, &s->dmi, s->request_id, p, out);\n  if (ret)\n   goto fail;\n  commands->packet_request_id[p] = s->request_id;\n }\n commands->prepared = true;\n ret = native_rear_validate_prepared_commands(commands);\n if (!ret)\n  return 0;\nfail:\n /* Publish all four together; no prefix may survive a later packet failure. */\n commands->prepared = false;\n memset(commands->packet_request_id, 0, sizeof(commands->packet_request_id));\n for (p = 0; p < E007Y_STARTUP_PACKETS; p++)\n  e007y_rear_clear_output(&commands->packet[p].out);\n return ret;\n}\n\n" + text[b:]
    path.write_text(text)

    path = camss / "camss-vfe-680.c"
    text = path.read_text()
    text = replace_once(text, '#include "camss-vfe-e008k-rear-runner.inc"',
                        '#include "native-rear-prepared-commands.inc"\n'
                        '#include "native-rear-vfe-config.inc"\n'
                        '#include "camss-vfe-e008k-rear-runner.inc"')
    text = replace_once(text, '#include "camss-e011z-rear-startup-adaptive-bind.inc"',
                        '#include "camss-e011z-rear-startup-adaptive-bind.inc"\n'
                        '#include "native-rear-scalar-binding.inc"\n'
                        '#include "native-rear-startup-geometry.inc"\n'
                        '#include "native-rear-startup-statistics.inc"\n'
                        '#include "camss-e011as-cold-gamma-policy.inc"\n'
                        '#include "native-rear-startup-iq.inc"\n'
                        '#include "native-rear-startup-compose.inc"\n'
                        '#include "native-rear-startup-entry.inc"')
    path.write_text(text)
    return {"shared_register_DMI_runner_removed": True,
            "prepared_arena_consumer": True, "all_or_none_materialization": True,
            "independent_packet_layouts_validated": True, "runtime_denied": True}
