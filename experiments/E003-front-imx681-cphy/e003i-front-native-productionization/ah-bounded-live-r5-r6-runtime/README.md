# E003i-AH — expanded-selector bounded live R5/R6 runtime

Status: **prepared fresh one-shot runtime; not yet executed.**

AH is the fresh package after AG reached live STREAMON but failed closed before R5 because the live temporal CCTs (4875/4808/4784 K) fell in the lower-AEC child `4500..5000` CCT interpolation gap. Commit `54bb21e` replaces the retained-Z-only direct-leaf shortcut with the serialized two-dimensional selector: lower CCT-tree selection/interpolation first, then outer AEC-tree selection/interpolation.

AH makes no kernel change. It reuses the exact accepted Z/Y generation-tagged 3A/TL_BG CAMSS module, accepted IMX681 module, front-only DTB, existing deferred V4L2 IQ FIFO, template-free R4 bootstrap, and corrected AE producer. There are no R5/R6 input capsule files. The child producer inherits the same video fd, must report READY before STREAMON, consumes G1 for state, submits R5 from G2 and R6 from G3, while the parent independently captures six frames and paired stats.

The mandatory Golden-side `prearm-check.sh` is tied to the actual consumed AG G1-G3 evidence. It SHA-verifies those six snapshot files, runs the complete corrected producer under root Python, requires `gap_4500_5000` followed by `gap_390_490`, and pins the corrected dynamic capsule identities:

- R5 `b05698889f607d5786a441a7c85ef07b6f61852d20a1894ff8f4919b07051d94`
- R6 `f694734412fe7cf4669fd1bfadb0f7eecc4d8f4b34f94f60a4a9068537dc546e`

It also reruns the cross-domain expanded-selector proof, requiring retained Z to keep its prior R5/R6 hashes. Actual-AG offline p95 is about 7.56/7.57 ms for G2->R5/G3->R6, comfortably inside 33.333 ms.

The one-shot/no-same-boot-retry and mandatory-Golden-return rules remain unchanged. Any producer, generation pairing, FIFO, provider, stream, frame-order or kernel-health error fails closed. This is still a bounded six-frame dynamic-LSC proof; unrestricted continuous AEC/LSC is not claimed.
