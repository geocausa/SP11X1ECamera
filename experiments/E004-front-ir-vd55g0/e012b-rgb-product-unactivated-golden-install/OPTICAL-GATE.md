# E012C visual-first gate

The first live acceptance on the current E012 product path is optical, not soak.

Before any repeated switching or long-duration service run, the fresh guarded product boot must produce root-private current-product renders from both RGB cameras:

- front: 1920x1080 rendered frame from the maintained front product path;
- rear: 3840x2160 rendered frame from the maintained rear product path.

Each image must be inspected for geometry, orientation, Bayer/channel order, obvious corruption/tearing, gross colour errors, and gross exposure failure. The images remain private/local evidence and are not committed.

Only after both renders are accepted may E012C proceed to repeated front/rear switching and longer product-service soak.
