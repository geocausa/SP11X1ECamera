# E004jr — bounded media-graph diagnostics before another physical camera experiment

2026-09-20. Parent `ee5f340`. **Source-only/offline phase completed; no E004jr candidate boot has been staged, armed or run.** Protected Golden camera drivers, default kernel/DTB/initrd and IR remain unchanged.

## Root cause still unknown

E004jq's one-use real rear 4K candidate passed accepted source/R4/loopback and 4K GStreamer publisher/application preflights. It then loaded camera modules and probed OV13858, IMX681 and standby IR. The attempt failed closed before any rear colourbar, normal optical frame, virtual /dev/video90 or application buffer because unified media-graph discovery did not succeed. The runner discarded `discover-unified.py` stderr, so there is **no evidence distinguishing missing graph nodes from parser mismatch, unsuccessful media-ctl, temporary node registration or another cause**. E004jq was consumed, returned to Golden and retired, and MUST NEVER be rearmed.

## Implemented (offline source only)

`camera-media-graph-diagnostic.py` is a bounded, non-image, strictly read-only graph inspection helper for a **future distinct** camera-enabled candidate boot. By default it only parses an existing archived `media-ctl -p` text file. An explicitly requested `--live --out-dir ROOT_PRIVATE_DIRECTORY` would require root-owned mode 0700 directory, enumerate up to eight ordinary `/dev/mediaN` nodes, use only `media-ctl -d NODE -p` and preserve bounded media topology, stderr, return code and a machine-readable required-entity/missing-entity verdict. Each subprocess uses a bounded timeout within an eight-second aggregate budget; no camera stream, media link alteration, sensor control, modules, reboot, GRUB, GPU, IR emitter or pixel access is performed. It rejects reused output filenames and symlinked/non-private directories. It does **not** start or initialize physical sensors; those would be source-locked and fail-closed separately in a new candidate. All live topology text stays in a root-private ephemeral candidate directory until reviewed and redacted; only non-image status metadata should be committed.

Nine Python tests PASS on protected SP11 Golden, including an accepted archived full unified three-sensor media graph (44 parsed entities, all ten required roles present), another archived graph lacking both RGB sensors (42 entities, two explicitly missing roles), deliberate entity removal, exact media-node filtering, root-directory/overwrite gates, CLI failure codes and nonactivation source checks. This validates the **parser and diagnostic contract on archived text only**, not the unknown exact E004jq failed graph (which was never recorded).

## Offline replay

```bash
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004jr-media-graph-diagnostic \
  -p test_media_graph_diagnostic.py -v
python3 experiments/E004-front-ir-vd55g0/e004jr-media-graph-diagnostic/camera-media-graph-diagnostic.py \
  --from-file experiments/E004-front-ir-vd55g0/e004ec-side-light-post-g3-shadow-observation/evidence/LOAD-MEDIA.txt
```

**Next gate:** design a NEW unique, bounded camera-capable *diagnostic-only* one-shot with protected Golden return. After exact driver/source/GRUB safety checks and camera module bind, run this helper and persist failure/success details before even considering rear optical streaming. Preserve the original Windows 4K NV12 reference and E004jp synthetic 4K V4L2 milestone, but never label either as a real Linux 4K optical webcam. A later, further distinct source-locked camera boot will connect actual rear optical→4K converter→standard virtual endpoint when the media graph is independently established.
