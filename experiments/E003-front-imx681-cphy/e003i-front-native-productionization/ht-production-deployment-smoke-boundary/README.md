# E003i-HT — production deployment smoke-plan / distro integration boundary

Status: **PASS / offline + read-only Golden inspection**.

HS proves that the runtime image can be installed and rolled back transactionally. HT asks the next production question: is installing that image onto protected Golden sufficient to make the camera usable? The answer is **no**, and this is now explicit rather than implicit.

Golden currently has no camera modules, no media/video/subdev nodes, no pending one-shot, and no production package installed. Live discovery therefore fails closed with zero matches. The HR runtime package intentionally owns only the private userspace/runtime tree and private copies of the two camera modules; it contains no `/boot`, `/etc`, `/lib/modules`, or systemd integration. The installer likewise does not run `modprobe`, `insmod`, `depmod`, GRUB commands, or service actions.

Every proven live front-RGB candidate separately supplied the front-only camera DTB/graph, firmware search path, exact candidate module load sequence, and a fail-closed boot-token gate. Those authorities must be productionized before a real-root package install can be meaningful. HT therefore blocks real Golden deployment and routes next work to HU boot/module/firmware integration authority.
