# E004dv — canonical unified three-camera hardware product

Status: **PASS / OFFLINE PRODUCT AUTHORITY / NO NEW RUNTIME**.

E004du moved the tested IR-gated CAMSS receiver path into maintained source and repaired exact production-module reproducibility. E004dv goes one layer higher: `src/sp11-camera-stack` is now the maintained hardware authority for rear RGB + front RGB + front IR together.

The canonical builder reconstructs the exact live-tested hardware set from maintained/frozen authority inputs and fails closed on hash drift. Its manifest SHA is:

`3b84ddcbb5728d04ea0e86d8ae066e1b4436e0f707afca1c4f7fb00e0e4ba140`

The manifest contains the exact unified DTB, four kernel modules, front capture binary and front bootstrap binary used by the accepted stack lineage.

CAMSS and IMX681 rebuild byte-exact from maintained source. VD55G0 also rebuilds byte-exact from a disposable source copy using the accepted Windows-generated register header and canonical debug-path mapping. Rear OV13858 is handled honestly: its exact accepted source is frozen, but the runtime module was an in-tree kernel build, so the canonical hardware authority freezes that accepted module instead of pretending an external-module compile is equivalent.

No runtime was needed for E004dv because these artifact hashes are exactly the authorities already exercised by E004dp/E004dr/E004ds. SP11 stays on protected Golden FullIO v19c. Linux SecureISP, illumination, direct IR stream and protected ownership remain untouched.
