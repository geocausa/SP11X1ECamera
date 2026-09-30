#!/usr/bin/env python3
"""Derive a packet-isolated unreachable runner from the accepted orchestration."""
from pathlib import Path
import hashlib
HERE=Path(__file__).resolve().parent
EXP=HERE.parent
old=EXP/"e008k-rear-complete-unreachable-runner/camss-vfe-e008k-rear-runner.inc"
assert not (HERE/"camss-vfe-e011ar-rear-runner.inc").exists(),"already prepared; audit rather than overwrite"
s=old.read_text()
for name in ("request","result","submit_packet","materialize_all","collect_done","pair_stop_release","emergency_pin","run_unreachable","runner_ops","runner_recipe","runtime_authorization"):
    s=s.replace("e008k_rear_"+name,"e011ar_rear_"+name)
s=s.replace("VFE680_E008K_REAR_COMPLETE_RUNNER_INC","VFE680_E011AR_REAR_PACKET_RUNNER_INC")
s=s.replace("E008K_REAR_","E011AR_REAR_")
s=s.replace("E008k: complete rear two-slot runner orchestration, deliberately unreachable.",
            "E011AR: packet-isolated rear two-slot orchestration, deliberately unreachable.")
s=s.replace("\tstruct e007d_rear_register_state *regs;\n\tstruct e007v_rear_dmi_state *dmi_state;",
            "\tstruct e008o_rear_semantic_set *semantics;\n\tstruct e008l_rear_command_set *commands;")
s=s.replace("\tu64 packet_request_id[E007Y_STARTUP_PACKETS];\n","")
start=s.index("static int\ne011ar_rear_materialize_all")
end=s.index("static int\ne011ar_rear_collect_done",start)
s=s[:start]+"""static int
e011ar_rear_materialize_all(struct e011ar_rear_request *req)
{
	unsigned int p;
	int ret;

	if (!req || !req->sensor || !req->semantics || !req->commands ||
	    !req->first_request_generation ||
	    req->first_request_generation == U64_MAX)
		return -EINVAL;

	/*
	 * Validate all four independent semantic objects before materializing.
	 * The arena must still be unsubmitted. Never rewrite exposed commands.
	 * Caller exclusively owns semantics and arena through this transaction.
	 */
	ret = e008o_rear_materialize_commands(req->semantics, req->commands);
	if (ret)
		return ret;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		struct e007y_rear_startup_output *out =
			e008l_rear_command_output(req->commands, p);

		if (!out)
			return -EINVAL;
		req->packet[p] = *out;
	}
	return 0;
}

"""+s[end:]
needle="\tret = e008k_rear_rtcdm_open_start(camss);\n\tif (ret)\n\t\tgoto out_pin;\n\trtcdm_started = true;\n\thardware_touched = true;"
replacement="""	/*
	 * Pin command allocations before the first possible RT-CDM exposure.
	 * No materialization occurs after this boundary. Even a partially
	 * failing open/start must execute emergency stop and pin output DMA.
	 */
	{
		unsigned int p;

		for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
			ret = e008l_rear_command_mark_submitted(req->commands, p);
			if (ret)
				goto out_pin;
		}
	}
	hardware_touched = true;
	rtcdm_started = true; /* may be partially opened even on error */
	ret = e008k_rear_rtcdm_open_start(camss);
	if (ret)
		goto out_pin;"""
assert s.count(needle)==1
s=s.replace(needle,replacement)
for call,flag in (
("e008j_rear_prepare_slot0_after_packet0(vfe, pair)","bus_may_be_enabled"),
("csid680_e008k_rear_enable(csid)","csid_streaming"),
("e008k_rear_subdev_stream(&csiphy->subdev, true)","csiphy_streaming"),
("e008k_rear_subdev_stream(req->sensor, true)","sensor_streaming")):
    needle="\tret = "+call+";"
    assert s.count(needle)==1
    s=s.replace(needle,"\t"+flag+" = true; /* attempt may partially touch hardware */\n"+needle)
s=s.replace("\tbus_may_be_enabled = true; /* MMIO is now exposed; pin on all failures. */\n","")
s=s.replace("Caller must provide already allocated/mapped E007y command buffers in req.",
            "Caller provides an unexposed arena and four sealed packet semantics.")
(HERE/"camss-vfe-e011ar-rear-runner.inc").write_text(s)
print("E011AR runner generated; no hardware action")
