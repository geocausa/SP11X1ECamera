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
                 "native-rear-startup-geometry.inc"):
        (camss / name).write_bytes((here / name).read_bytes())
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
    text = text[:a] + "static int\ne008k_rear_validate_prepared_packets(struct e008k_rear_request *req)\n{\n unsigned int p;\n int ret;\n if (!req || !req->sensor || !req->commands || !req->first_request_generation)\n  return -EINVAL;\n ret = native_rear_validate_prepared_commands(req->commands);\n if (ret)\n  return ret;\n for (p = 0; p < E007Y_STARTUP_PACKETS; p++)\n  if (req->packet_request_id[p] != req->commands->packet_request_id[p])\n   return -ESTALE;\n return 0;\n}\n\n" + text[b:]
    text = replace_once(text, "e008k_rear_materialize_all(req)", "e008k_rear_validate_prepared_packets(req)")
    for p in range(4):
        text = replace_once(text, f"&req->packet[{p}]", f"&req->commands->packet[{p}].out")
    anchor = "static int __used\ne008k_rear_run_unreachable("
    text = replace_once(text, anchor, "static int e008k_rear_runtime_authorization(void);\n\n" + anchor)
    anchor = "\tpair = kzalloc(sizeof(*pair), GFP_KERNEL);"
    text = replace_once(text, anchor,
                        "\t/* The prepared handoff does not grant rear hardware access. */\n"
                        "\tret = e008k_rear_runtime_authorization();\n\tif (ret)\n\t\treturn ret;\n\n" + anchor)
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
    a = text.index("static int\ne008o_rear_materialize_commands(")
    b = text.index("struct e008o_rear_semantic_ops {", a)
    text = text[:a] + "static int\ne008o_rear_materialize_commands(struct e008o_rear_semantic_set *set,\n                                 struct e008l_rear_command_set *commands)\n{\n unsigned int p;\n int ret;\n if (!commands || !commands->allocated || commands->prepared ||\n     commands->hardware_exposed)\n  return -EINVAL;\n for (p = 0; p < E007Y_STARTUP_PACKETS; p++)\n  if (!commands->packet[p].allocated || commands->packet[p].submitted)\n   return -EINVAL;\n ret = e008o_rear_validate_semantic_set(set);\n if (ret)\n  return ret;\n for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {\n  struct e007y_rear_startup_output *out = e008l_rear_command_output(commands, p);\n  struct e008o_rear_packet_semantics *s = &set->packet[p];\n  ret = e007y_rear_materialize(&s->regs, &s->dmi, s->request_id, p, out);\n  if (ret)\n   goto fail;\n  commands->packet_request_id[p] = s->request_id;\n }\n commands->prepared = true;\n ret = native_rear_validate_prepared_commands(commands);\n if (!ret)\n  return 0;\nfail:\n /* Publish all four together; no prefix may survive a later packet failure. */\n commands->prepared = false;\n memset(commands->packet_request_id, 0, sizeof(commands->packet_request_id));\n for (p = 0; p < E007Y_STARTUP_PACKETS; p++)\n  e007y_rear_clear_output(&commands->packet[p].out);\n return ret;\n}\n\n" + text[b:]
    path.write_text(text)

    path = camss / "camss-vfe-680.c"
    text = path.read_text()
    text = replace_once(text, '#include "camss-vfe-e008k-rear-runner.inc"',
                        '#include "native-rear-prepared-commands.inc"\n'
                        '#include "camss-vfe-e008k-rear-runner.inc"')
    text = replace_once(text, '#include "camss-e011z-rear-startup-adaptive-bind.inc"',
                        '#include "camss-e011z-rear-startup-adaptive-bind.inc"\n'
                        '#include "native-rear-scalar-binding.inc"\n'
                        '#include "native-rear-startup-geometry.inc"')
    path.write_text(text)
    return {"shared_register_DMI_runner_removed": True,
            "prepared_arena_consumer": True, "all_or_none_materialization": True,
            "independent_packet_layouts_validated": True, "runtime_denied": True}
