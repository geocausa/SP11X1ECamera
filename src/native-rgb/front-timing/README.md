# Front sensor timing check

Development-only probe for the approved libcamera sensor timing ABI.
Identity: native-timing-20261007-01. Never rearm after ATTEMPT-CONSUMED.

A fresh isolated camera boot uses the source-built native-rgb-20261007-audit-04
modules and the accepted unified DTB. Golden FullIO v19c remains default; its
kernel, initrd and DTB are hashed and never overwritten. No product daemon,
loopback, software ISP, PIX capture or IR stream is activated.

The probe queues four kernel MMAP buffers without calling mmap/read or copying
pixels. It measures 120 sequential front RAW frames at FLL 3554 and another 120
at FLL 7116, with line length 6752 and known atomic exposure/gain controls.
Timestamp flag, payload length, sequence, errors and successful STREAMOFF are
checked. Sensor idle state and the complete 119-edge graph are checked before
route changes; an uncertain failure performs no guessed rollback.

The systemd unit orders itself after both verified GRUB writers and before the
display manager. Its stop hook returns to Golden on success, failure or timeout.
Asset manifests are root sealed. This unit is diagnostic boot tooling, not a
camera product runtime.

probe.c compiles with -Wall -Wextra -Werror. --self-test checks known synthetic
timing and nonmonotonic rejection without device access. Synthetic results are
explicitly labelled and never count as hardware proof. A Golden invocation is
refused before opening devices.

install.py prepares unarmed assets only. Its fixed identity/output paths are
intentional. Only arm a fresh prepared identity after source checkpoint,
Golden/idle and all asset checks; never rerun after consumption. Read RESULT.json
and verify protected Golden return before accepting or publishing a clock value.
Do not claim image quality from timestamp data.
