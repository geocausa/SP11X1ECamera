# E012C — RGB product optical-first guarded one-shot

E012C is the first live checkpoint of the E012 product-integration phase. It is **not** a soak-first run.

The candidate reuses the accepted unified camera DTB and exact accepted camera modules, boots the same Golden kernel/initrd with a unique product token, loads the camera authority only after boot, creates the two named V4L2 loopback endpoints, then starts the committed `sp11-camera-rgb` product daemon.

The first acceptance is two root-private rendered PNGs produced through the actual product service:

- front: 1920x1080 from `/dev/video91`;
- rear: 3840x2160 from `/dev/video90`.

The images are local/private evidence only. They are never committed. Repeated switching or long-duration soak is forbidden until both current-product renders are visually inspected and accepted.

IR/Hello remains out of product scope; VD55G0 is bind/standby only and no illumination or IR stream is requested.
