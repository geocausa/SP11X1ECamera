# Retained front graph integration

Candidate26 joins qualified full source23 with FLL24 and retained power port25.
This adds an experimental Denali OLED target alongside the unchanged original
board target. Sensor mode tables and C-PHY/CAMSS bodies remain unchanged.

Retained E003b/E003c and the working dual-front source supply CCI1/master1
at400kHz, GPIO235/236, MCLK4 GPIO100/cam_aon at19.2MHz, active-low reset237,
PM8010-M LDO3 IO1.8V and PM8550-B LDO7 analog2.8V. Standard providers use
SMPS4_C and BOB2 respectively, with initial HPM3. B LDO7 is added under the
existing PM8550-B provider; there is one separate PM8010-M provider.
No actuator/VAF, IR or rear sensor is added.

The newer PHY API requires reciprocal links:
IMX681 -> PHY2 input port0; PHY2 output port1 -> CAMSS port2.
Relevant parsers receive explicit C-PHY/trio0/ABC. Sensor link-frequency is
1.203GHz for the imported2.406Gsymbol/s profile. PHY2 retains its8KiB aperture,
exclusive IRQ and clock/domain definitions. The shared L2_C/L1_C supplies come
from the retained native front graph; existing voltage constraints stay.
Electrical/runtime qualification of the newer standard graph remains pending.

The compiled-DTB auditor checks links, clocks, reset, regulators/parents,
pinmux, bus/profile and disabled other routes. Nine broken controls must fail.
Scoped CAMSS/PHY schema checks are separate. There is no dedicated IMX681
binding schema yet; sensor binding/maintainer review remains a gap.
Runtime privacy indication and fresh upstream boot/stream/stop/reopen remain
pending. No electrical or optical measurement is inferred from constraints.

Reproduce with fresh output paths:

    python3 prepare.py --parent-source /path/to/candidate23/source --output /path/to/new-source
    make -C /path/to/new-source O=/path/to/new-build ARCH=arm64 qcom/x1e80100-microsoft-denali-oled-front-camera.dtb
    python3 test-graph.py --dtb /path/to/new-build/arch/arm64/boot/dts/qcom/x1e80100-microsoft-denali-oled-front-camera.dtb --output /path/to/new-result.json

Use the prepared7.2 config and existing dtschema environment. The full build
derives from pinned candidate19 config; disable all old DWARF choices and
enable DEBUG_INFO_NONE. The removed PAHOLE language-capability symbol is a
debug-tool dependency. Other feature choices remain unchanged. Unique
LOCALVERSION=-sp11-upstream-front26 isolates candidate modules. The runner
stops if free space falls below512MiB.

Source, graph and reference pins are in manifest.json. Preparation hard-links
unchanged files but breaks each modified link before writing and rechecks the
original inputs afterward. Never modify a prepared source in place.
No installation, boot or capture happens through these tools. Proprietary
camera inputs remain excluded. Preserve native2.400/720MHz timing/calibration.
Both private startup-consumer replacements and release qualification remain.

Full build reproduction after preparation (fresh build path):

    mkdir /path/to/new-build
    cp /path/to/candidate19/build/.config /path/to/new-build/.config
    /path/to/new-source/scripts/config --file /path/to/new-build/.config -d DEBUG_INFO -d DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT -d DEBUG_INFO_DWARF4 -d DEBUG_INFO_DWARF5 -e DEBUG_INFO_NONE
    make -C /path/to/new-source O=/path/to/new-build ARCH=arm64 LOCALVERSION=-sp11-upstream-front26 olddefconfig
    make -C /path/to/new-source O=/path/to/new-build ARCH=arm64 LOCALVERSION=-sp11-upstream-front26 -j4 W=1 Image modules
    python3 test-inputs.py --parent-source /path/to/candidate23/source --output /path/to/fresh-controls

Full build worker/logs retained on SP11 under candidate-26/final-qual02.
Full tree has baseline compiler/kernel-doc diagnostics; strict camera objects
pass W=1/KCFLAGS=-Werror. The evidence JSON records the exact scope.
