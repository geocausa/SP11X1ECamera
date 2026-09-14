# E004eg — static full-light Windows/Linux AEC parity

The room is static and empty, with side and main lights on. A fresh Windows oracle was captured immediately before this Linux one-shot.

Windows Camera had Studio Effects **Off**. A central preview-only crop measured mean luma 110.9/255 and median 115/255, so the scene is not underexposed. A fresh 12-request QcDeviceMFT8380 DM trace returned `capflag=0` on all requests and a stable compact block containing 954,179,854 and 1,340,473,362.

This experiment runs the canonical Linux package **unchanged** with post-G3 policy `shadow`; no later native write is authorized. It preserves the live STATS3A/TLBG blobs and QC10C frames. Analysis happens offline afterward through the same native request-loop sources, so diagnostics cannot alter live sensor behavior.
