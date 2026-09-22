/* SPDX-License-Identifier: MIT
 * Synthetic libcamera lifecycle / native media transaction integration.
 * No libcamera library, camera devices or real kernel ioctls are used.
 */
#define main topology_decoder_selftest_main
#include "test_media_topology.cpp"
#undef main
#include "../sp11-libcamera-route-gate.h"
#include <cassert>
#include <iostream>
#include <memory>

static Topology *working = nullptr;
static unsigned writes = 0;
static int writeFailure = 0;
static int bridgeIoctl(int fd, unsigned long command, void *argument)
{
    if (command != MEDIA_IOC_SETUP_LINK)
        return fakeIoctl(fd, command, argument);
    if (fd != 17 || !working || writeFailure == 1) return -1;
    auto &request = *static_cast<media_link_desc *>(argument);
    unsigned sourcePad = 0, sinkPad = 0;
    for (const auto &p : working->pads) {
        if (p.entity_id == request.source.entity &&
            p.index == request.source.index)
            sourcePad = p.id;
        if (p.entity_id == request.sink.entity &&
            p.index == request.sink.index)
            sinkPad = p.id;
    }
    if (!sourcePad || !sinkPad) return -1;
    unsigned matches = 0;
    for (auto &link : working->links) {
        if ((link.flags & MEDIA_LNK_FL_LINK_TYPE) ==
                MEDIA_LNK_FL_DATA_LINK &&
            link.source_id == sourcePad && link.sink_id == sinkPad &&
            !(link.flags & MEDIA_LNK_FL_IMMUTABLE)) {
            link.flags = request.flags;
            ++matches;
        }
    }
    if (matches != 1) return -1;
    ++writes;
    return 0;
}
static void bind(Fixture &fixture)
{
    working = &fixture.top;
    mockTop = &fixture.top;
    mockMode = mockStep = 0;
    writes = 0;
    writeFailure = 0;
}
static std::unique_ptr<sp11::NativeSession> makeSession(
    const sp11::NativeSession::Guard &owns,
    const sp11::NativeSession::Guard &stopped)
{
    return std::make_unique<sp11::NativeSession>(
        17, bridgeIoctl, owns, stopped);
}

int main()
{
    assert(sp11::LibcameraRouteGate::camera("imx681 2-0010") == "front");
    assert(sp11::LibcameraRouteGate::camera("ov13858 30-0010") == "rear");
    assert(sp11::LibcameraRouteGate::camera("imx681 2-0011").empty());
    assert(sp11::LibcameraRouteGate::camera("sp11-vd55g0 2-0060").empty());
    assert(!sp11::LibcameraRouteGate::allowActiveRoutingReset());
    Fixture f;
    bind(f);
    bool owns = true;
    bool stopped = true;
    auto owner = [&]() { return owns; };
    auto idle = [&]() { return stopped; };
    sp11::LibcameraRouteGate gate;
    assert(!gate.admitted() && !gate.streaming());
    assert(gate.attach(makeSession(owner, idle)));
    assert(gate.admitted());
    assert(gate.setupLinks("imx681 1-0010") && writes == 2);
    assert(gate.beforeStream("imx681 1-0010") && gate.streaming() && writes == 2);
    assert(gate.afterStream() && writes == 4 && !gate.streaming());
    assert(gate.setupLinks("ov13858 3-0010") && writes == 6);
    assert(gate.beforeStream("ov13858 3-0010") && gate.streaming());
    assert(gate.afterStream() && writes == 8 && !gate.streaming());
    Graph graph; State enabled;
    assert(decodeTopology(f.top, graph) && validGraph(graph, enabled) &&
           phase(enabled) == "neutral");
    assert(gate.neutralizeWhenIdle() && writes == 8);
    /* Re-run frontend lifecycle with neutral hardware between configure and
     * STREAMON: no camera route remains active during ordinary app idle.
     */
    assert(gate.setupLinks("imx681 1-0010") && writes == 10);
    assert(gate.parkRouteUntilStart() && writes == 12);
    assert(decodeTopology(f.top, graph) && validGraph(graph, enabled));
    assert(phase(enabled) == "neutral");
    assert(gate.beforeStream("imx681 1-0010") && writes == 14);
    assert(gate.afterStream() && writes == 16);
    assert(decodeTopology(f.top, graph) && validGraph(graph, enabled));
    assert(phase(enabled) == "neutral");
    assert(!gate.attach(makeSession(owner, idle)));

    Fixture noLease;
    bind(noLease);
    owns = false;
    sp11::LibcameraRouteGate denied;
    assert(!denied.attach(makeSession(owner, idle)));
    assert(!denied.admitted() && writes == 0);
    owns = true;

    Fixture stoppedMissing;
    bind(stoppedMissing);
    stopped = false;
    sp11::LibcameraRouteGate notQuiescent;
    assert(!notQuiescent.attach(makeSession(owner, idle)));
    assert(!notQuiescent.admitted() && writes == 0);
    stopped = true;

    Fixture foreign;
    bind(foreign);
    sp11::LibcameraRouteGate rejectIr;
    assert(rejectIr.attach(makeSession(owner, idle)));
    assert(!rejectIr.setupLinks("sp11-vd55g0 2-0060"));
    assert(!rejectIr.admitted() && writes == 0);

    Fixture wrongStart;
    bind(wrongStart);
    sp11::LibcameraRouteGate rejectWrongCamera;
    assert(rejectWrongCamera.attach(makeSession(owner, idle)));
    assert(rejectWrongCamera.setupLinks("imx681 1-0010"));
    assert(!rejectWrongCamera.beforeStream("ov13858 3-0010"));
    assert(!rejectWrongCamera.admitted());
    unsigned oldWrites = writes;
    assert(!rejectWrongCamera.setupLinks("ov13858 3-0010"));
    assert(writes == oldWrites);

    Fixture concurrent;
    bind(concurrent);
    sp11::LibcameraRouteGate rejectConcurrent;
    assert(rejectConcurrent.attach(makeSession(owner, idle)));
    assert(rejectConcurrent.setupLinks("imx681 1-0010"));
    assert(rejectConcurrent.beforeStream("imx681 1-0010"));
    unsigned activeWrites = writes;
    assert(!rejectConcurrent.setupLinks("ov13858 3-0010"));
    assert(!rejectConcurrent.admitted() && writes == activeWrites);

    Fixture writeFail;
    bind(writeFail);
    sp11::LibcameraRouteGate failing;
    assert(failing.attach(makeSession(owner, idle)));
    writeFailure = 1;
    assert(!failing.setupLinks("imx681 1-0010") && !failing.admitted());
    assert(writes == 0);

    std::cout << "PASS libcamera-native RGB gate: exact front/rear stream "
                 "lifecycle with 16 exact native ioctl writes including idle-neutral parking; IR/foreign sensor, "
                 "missing ownership/quiescence, cross-camera start, "
                 "failed writer and active routing reset rejected\n";
    return 0;
}
