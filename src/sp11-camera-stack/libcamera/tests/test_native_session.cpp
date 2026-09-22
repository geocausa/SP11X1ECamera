/* SPDX-License-Identifier: MIT
 * Synthetic native ioctl transaction tests; no real /dev/media device.
 */
#define main topology_decoder_selftest_main
#include "test_media_topology.cpp"
#undef main
#include "../sp11-native-session.h"

static Topology *mutableTop = nullptr;
static int writeMode = 0;
static unsigned writes = 0;
static int sessionIoctl(int fd, unsigned long op, void *raw)
{
    if (op != MEDIA_IOC_SETUP_LINK)
        return fakeIoctl(fd, op, raw);
    if (fd != 17 || !mutableTop || writeMode == 1) return -1;
    ++writes;
    if (writeMode == 2) return 0; // False-success ioctl must poison.
    const auto &request = *static_cast<media_link_desc *>(raw);
    if (request.flags != 0 && request.flags != MEDIA_LNK_FL_ENABLED)
        return -1;
    unsigned sourcePad = 0, sinkPad = 0;
    for (const auto &p : mutableTop->pads) {
        if (p.entity_id == request.source.entity &&
            p.index == request.source.index)
            sourcePad = p.id;
        if (p.entity_id == request.sink.entity &&
            p.index == request.sink.index)
            sinkPad = p.id;
    }
    if (!sourcePad || !sinkPad) return -1;
    unsigned matches = 0;
    for (auto &link : mutableTop->links) {
        if ((link.flags & MEDIA_LNK_FL_LINK_TYPE) == MEDIA_LNK_FL_DATA_LINK &&
            link.source_id == sourcePad && link.sink_id == sinkPad &&
            !(link.flags & MEDIA_LNK_FL_IMMUTABLE)) {
            link.flags = request.flags;
            ++matches;
        }
    }
    if (matches != 1) return -1;
    if (writeMode == 3)
        mutableTop->links[44].flags = MEDIA_LNK_FL_ENABLED; // unapproved IR path
    return 0;
}
static void bind(Fixture &fixture)
{
    mutableTop = &fixture.top;
    mockTop = &fixture.top;
    mockMode = mockStep = 0;
    writes = 0;
}
int main()
{
    Fixture normal;
    bind(normal);
    bool owns = true, stopped = true;
    NativeSession session(17, sessionIoctl, [&]() { return owns; },
                          [&]() { return stopped; });
    assert(session.initialize());
    assert(session.transition("front") && writes == 2);
    Graph check;
    assert(decodeTopology(normal.top, check));
    State enabled;
    assert(validGraph(check, enabled) && phase(enabled) == "front");
    assert(session.transition("rear") && writes == 6);
    assert(decodeTopology(normal.top, check));
    assert(validGraph(check, enabled) && phase(enabled) == "rear");
    assert(session.transition("neutral") && writes == 8);
    assert(decodeTopology(normal.top, check));
    assert(validGraph(check, enabled) && phase(enabled) == "neutral");
    assert(!session.poisoned());

    Fixture ownership;
    bind(ownership);
    owns = false;
    NativeSession noOwner(17, sessionIoctl, [&]() { return owns; },
                          [&]() { return stopped; });
    assert(!noOwner.initialize() && noOwner.poisoned() && writes == 0);
    owns = true;

    Fixture idle;
    bind(idle);
    NativeSession notIdle(17, sessionIoctl, [&]() { return owns; },
                          [&]() { return stopped; });
    assert(notIdle.initialize());
    stopped = false;
    assert(!notIdle.transition("front") && notIdle.poisoned() && writes == 0);
    stopped = true;

    Fixture unexpectedInitial;
    for (const auto &edge : route("rear")) assert(unexpectedInitial.set(edge));
    bind(unexpectedInitial);
    NativeSession strict(17, sessionIoctl, [&]() { return owns; },
                         [&]() { return stopped; });
    assert(!strict.initialize() && strict.poisoned() && writes == 0);

    Fixture rearInitial;
    for (const auto &edge : route("rear")) assert(rearInitial.set(edge));
    bind(rearInitial);
    NativeSession adopted(17, sessionIoctl, [&]() { return owns; },
                          [&]() { return stopped; });
    assert(adopted.adoptStoppedRouteAndNeutralize() && writes == 2);
    Graph afterAdoption;
    State adoptedFlags;
    assert(decodeTopology(rearInitial.top, afterAdoption));
    assert(validGraph(afterAdoption, adoptedFlags));
    assert(phase(adoptedFlags) == "neutral");

    Fixture partialInitial;
    assert(partialInitial.set(*route("rear").begin()));
    bind(partialInitial);
    NativeSession rejectPartial(17, sessionIoctl, [&]() { return owns; },
                                [&]() { return stopped; });
    assert(!rejectPartial.adoptStoppedRouteAndNeutralize() &&
           rejectPartial.poisoned() && writes == 0);

    for (int fault : {1, 2, 3}) {
        Fixture failing;
        bind(failing);
        writeMode = fault;
        NativeSession poisoned(17, sessionIoctl, [&]() { return owns; },
                               [&]() { return stopped; });
        assert(poisoned.initialize());
        assert(!poisoned.transition("front"));
        assert(poisoned.poisoned());
        unsigned previous = writes;
        assert(!poisoned.transition("rear") && writes == previous);
        writeMode = 0;
    }
    std::cout << "PASS native ioctl transaction: 8 exact route writes, "
                 "fresh graph per step, neutral/front/rear transitions, "
                 "missing ownership/stopped, rear-only adoption-to-neutral, partial route and 3 link faults fail closed\n";
}
