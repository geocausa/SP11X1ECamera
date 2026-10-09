# SPDX-License-Identifier: GPL-2.0-only
"""Exact declared timestamp delta reversal for original transport comparisons."""
def undo_queue_timestamp(text):
 new="#ifdef __KERNEL__\n  buffer->vb.vb2_buf.timestamp = video->native_rear_statistics_tick;\n  video->native_rear_statistics_tick = 0;\n#else\n  buffer->vb.vb2_buf.timestamp = ktime_get_ns();\n#endif"
 assert text.count(new)==1,"declared statistics timestamp delta drift"
 return text.replace(new,"  buffer->vb.vb2_buf.timestamp = ktime_get_ns();",1)
