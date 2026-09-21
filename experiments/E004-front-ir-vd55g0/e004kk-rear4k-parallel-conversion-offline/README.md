# E004kk — offline rear 4K converter throughput

E004kj proved sequential standard front/rear devices, but rear source delivery was 18.1231fps in the bounded workload. Hypothesis: scalar Bayer processing contributes backpressure. This camera-free candidate distributes disjoint two-row output tiles across at most four workers, retaining the exact accepted crop, upper-eight-bit RAW10 interpretation, interpolation, rounding and NV12 matrix. Input/conversion/output waits are measured separately. Frames remain bounded 1..240 and anonymous pipe output only. This does not improve image quality, decode front QC10C, or prove any live fps improvement.

Tests compare byte-exact outputs with the accepted scalar implementation for archived colourbar, nonuniform gradients across worker boundaries, black/white extremes and consecutive different frames. Bounds, extra and truncated input must still fail. No sensors, camera modules, video nodes, service or boot entry are activated.

## Measured outcome

Four-worker conversion was rejected for deployment: ABBA camera-free 120-frame tests delivered scalar 52.581/52.125fps to /dev/null, versus parallel 25.385/23.044fps, with parallel input waits 26.752/29.394ms. No cgroup CPU quota was observed in the command ancestry. These results do not identify the complete cause of the regression.

A separate single-worker variant changes only anonymous pipe capacity (request at most 1MiB each, smaller than one 12.44MB output frame), preserving all pixel mathematics and adding timing. It delivered 60.261/61.091fps to /dev/null versus scalar 52.850/50.217fps. The real camera-free converter→byte meter→GStreamer app chain still delivered only 14.046/18.978fps with larger pipes versus 11.137/10.720fps baseline. All four app runs consumed 120 complete buffers, with 1,492,992,000 exact forwarded bytes each; these repeated archived colourbar frames are NOT distinct live video. Results vary materially between runs and do not prove a live speedup.

The remaining copy-heavy test application path is itself a bottleneck candidate. Next isolate a native GStreamer V4L2 source directly into appsink (retaining full payload-size checks, private uniqueness hashes and monotonic timing), avoiding the V4L2-to-stdout/meter/Python-bytearray/appsrc copies during the new performance measurement. The metered E004kj evidence remains authoritative for the prior byte-exact path. No new hardware experiment was performed in E004kk.
