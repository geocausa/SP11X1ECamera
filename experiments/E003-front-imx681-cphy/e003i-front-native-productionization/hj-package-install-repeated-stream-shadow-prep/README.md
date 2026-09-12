# E003i-HJ — package/install staging and repeated-stream shadow preparation

HJ packages the committed HI stable tree into a relocatable `/usr/lib/sp11-front-imx681` layout, builds the accepted CAMSS/IMX681 modules plus production userspace, and verifies the staged launcher from outside the source workspace.

The package is built from `git archive HEAD`, so ignored HG authority caches and historical runtime debris cannot accidentally enter the install image. Production binaries/modules are overlaid from a fresh build and every staged file is SHA256-manifested.

Runtime validation, if later authorized, must use a fresh disposable boot identity and the launcher default `shadow` policy. HJ packaging itself performs no camera runtime.
