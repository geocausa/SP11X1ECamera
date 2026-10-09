# SPDX-License-Identifier: GPL-2.0-only
BLOCK='\t/* Preserve accepted E008c source stop order: CSIPHY then sensor. */\n\tstop_ret = e008k_rear_subdev_stream(&csiphy->subdev, false);\n\tif (!stop_ret)\n\t\t*csiphy_streaming = false;\n\tret = e008k_rear_subdev_stream(sensor, false);\n\tif (!ret)\n\t\t*sensor_streaming = false;\n\tif (stop_ret || ret)\n\t\treturn stop_ret ? stop_ret : ret;\n\tresult->source_stopped = true;\n'
ANCHOR='\tret = csid680_e008a_rear_quiesce(csid, true);'
def undo_source_stop_order(text):
 before=BLOCK+"\n"+ANCHOR
 assert text.count(before)==1,"early source stop delta drift"
 text=text.replace(before,ANCHOR,1)
 after="\tresult->rtcdm_stopped = true;\n"
 assert text.count(after)==1
 return text.replace(after,after+"\n"+BLOCK,1)
