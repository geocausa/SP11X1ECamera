/* SPDX-License-Identifier: MIT
 * Fully synthetic SP11 media-controller v2 ioctl payload, no camera access.
 */
#include "../sp11-media-topology.h"
#include <cassert>
#include <cstring>
#include <iostream>
#include <map>
#include <string>
#include <utility>
using namespace sp11;

struct Fixture {
    Topology top;
    std::map<std::string, unsigned> entities;
    std::map<std::pair<std::string, unsigned>, unsigned> pads;
    unsigned nextEntity = 1, nextIntf = 101, nextPad = 201, nextLink = 401;
    void entity(const std::string &name, unsigned nPads, bool sensor = false,
                bool video = false)
    {
        media_v2_entity e{};
        e.id = nextEntity++;
        std::strncpy(e.name, name.c_str(), sizeof(e.name) - 1);
        top.entities.push_back(e);
        entities[name] = e.id;
        media_v2_interface intf{};
        intf.id = nextIntf++;
        intf.intf_type = video ? MEDIA_INTF_T_V4L_VIDEO : MEDIA_INTF_T_V4L_SUBDEV;
        intf.devnode.major = 81;
        intf.devnode.minor = static_cast<unsigned>(top.interfaces.size());
        top.interfaces.push_back(intf);
        media_v2_link il{};
        il.id = nextLink++;
        il.source_id = intf.id;
        il.sink_id = e.id;
        il.flags = MEDIA_LNK_FL_INTERFACE_LINK | MEDIA_LNK_FL_ENABLED |
                   MEDIA_LNK_FL_IMMUTABLE;
        top.links.push_back(il);
        for (unsigned index = 0; index != nPads; ++index) {
            media_v2_pad p{};
            p.id = nextPad++;
            p.entity_id = e.id;
            p.index = index;
            p.flags = sensor || (!video && index > 0) ?
                      MEDIA_PAD_FL_SOURCE : MEDIA_PAD_FL_SINK;
            top.pads.push_back(p);
            pads[{name, index}] = p.id;
        }
    }
    void edge(const std::string &a, unsigned ap, const std::string &b,
              unsigned bp, bool immutable = false)
    {
        media_v2_link l{};
        l.id = nextLink++;
        l.source_id = pads.at({a, ap});
        l.sink_id = pads.at({b, bp});
        l.flags = immutable ? MEDIA_LNK_FL_ENABLED | MEDIA_LNK_FL_IMMUTABLE : 0;
        top.links.push_back(l);
    }
    Fixture()
    {
        for (int phy : {0, 1, 2, 4})
            entity("msm_csiphy" + std::to_string(phy), 2);
        for (int csid = 0; csid != 5; ++csid)
            entity("msm_csid" + std::to_string(csid), 5);
        for (int vfe = 0; vfe != 4; ++vfe)
            for (int port = 0; port != 4; ++port) {
                const std::string prefix = "msm_vfe" + std::to_string(vfe);
                const std::string capture = prefix + "_" +
                    (vfe < 2 && port == 3 ? "pix" :
                     "rdi" + std::to_string(port));
                const std::string video = prefix + "_video" +
                    std::to_string(port);
                entity(capture, 2);
                entity(video, 1, false, true);
            }
        entity("sp11-vd55g0 2-0060", 1, true);
        entity("ov13858 3-0010", 1, true);
        entity("imx681 1-0010", 1, true);
        for (int phy : {0, 1, 2, 4})
            for (int csid = 0; csid != 5; ++csid)
                edge("msm_csiphy" + std::to_string(phy), 1,
                     "msm_csid" + std::to_string(csid), 0);
        for (int vfe = 0; vfe != 4; ++vfe)
            for (int port = 0; port != 4; ++port) {
                const std::string prefix = "msm_vfe" + std::to_string(vfe);
                const std::string capture = prefix + "_" +
                    (vfe < 2 && port == 3 ? "pix" :
                     "rdi" + std::to_string(port));
                edge(capture, 1, prefix + "_video" + std::to_string(port),
                     0, true);
                for (int csid = 0; csid != 5; ++csid)
                    edge("msm_csid" + std::to_string(csid), port + 1,
                         capture, 0);
            }
        for (const auto &[sensor, phy] :
             std::map<std::string, int>{{"sp11-vd55g0 2-0060", 0},
                                        {"ov13858 3-0010", 1},
                                        {"imx681 1-0010", 2}})
            edge(sensor, 0, "msm_csiphy" + std::to_string(phy), 0, true);
    }
    bool set(const Edge &target)
    {
        for (auto &l : top.links) {
            if ((l.flags & MEDIA_LNK_FL_LINK_TYPE) != MEDIA_LNK_FL_DATA_LINK)
                continue;
            std::map<unsigned, std::pair<std::string, unsigned>> reverse;
            for (const auto &[p, id] : pads) reverse[id] = p;
            if (reverse.at(l.source_id) == std::make_pair(std::get<0>(target),
                    std::get<1>(target)) &&
                reverse.at(l.sink_id) == std::make_pair(std::get<2>(target),
                    std::get<3>(target))) {
                l.flags |= MEDIA_LNK_FL_ENABLED;
                return true;
            }
        }
        return false;
    }
};

#include "mock_media_ioctl.inc"
int main()
{
    Fixture base;
    assert(base.top.entities.size() == 44 && base.top.pads.size() == 84);
    assert(base.top.interfaces.size() == 44 && base.top.links.size() == 163);
    Graph neutral;
    assert(decodeTopology(base.top, neutral));
    State active;
    assert(validGraph(neutral, active) && phase(active) == "neutral");
    assert(neutral.identity.size() == 335);
    Fixture front = base;
    for (const auto &edge : route("front")) assert(front.set(edge));
    Graph frontGraph;
    assert(decodeTopology(front.top, frontGraph));
    assert(validGraph(frontGraph, active) && phase(active) == "front");
    assert(neutral.identity == frontGraph.identity);
    Fixture rear = base;
    for (const auto &edge : route("rear")) assert(rear.set(edge));
    Graph rearGraph;
    assert(decodeTopology(rear.top, rearGraph));
    assert(validGraph(rearGraph, active) && phase(active) == "rear");

    unsigned rejected = 0;
    auto reject = [&](Topology candidate) {
        Graph out = neutral;
        if (decodeTopology(candidate, out)) { std::cerr << "UNEXPECTED_ACCEPTED_CASE=" << (rejected + 1) << "\n"; std::abort(); }
        assert(out.identity == neutral.identity);
        ++rejected;
    };
    auto run = [&](auto change) {
        Topology candidate = base.top;
        change(candidate);
        reject(std::move(candidate));
    };
    run([](Topology &t) { t.entities.pop_back(); });
    run([](Topology &t) { t.interfaces.pop_back(); });
    run([](Topology &t) { t.pads.pop_back(); });
    run([](Topology &t) { t.links.pop_back(); });
    run([](Topology &t) { t.entities[1].id = t.entities[0].id; });
    run([](Topology &t) { std::memset(t.entities[0].name, 'a', 64); });
    run([](Topology &t) { t.entities[0].name[0] = 'x'; });
    run([](Topology &t) { t.pads[0].index = 7; });
    run([](Topology &t) { t.pads[0].flags = MEDIA_PAD_FL_SOURCE; });
    run([](Topology &t) { t.pads[0].id = t.pads[1].id; });
    run([](Topology &t) { t.interfaces[0].intf_type = 0; });
    run([](Topology &t) { t.interfaces[0].devnode.major = 0; });
    run([](Topology &t) { t.links[0].sink_id = t.links[1].sink_id; });
    run([](Topology &t) { t.links[0].flags = MEDIA_LNK_FL_INTERFACE_LINK; });
    run([](Topology &t) { t.links[0].id = t.links[1].id; });
    run([](Topology &t) { t.links[44].source_id = 0; });
    run([](Topology &t) { t.links[44].flags = MEDIA_LNK_FL_DYNAMIC; });
    run([](Topology &t) { t.links[44].flags = MEDIA_LNK_FL_ENABLED | MEDIA_LNK_FL_IMMUTABLE; });
    run([](Topology &t) { t.links[44].sink_id = t.links[45].sink_id; });
    auto partial = front.top;
    partial.links[44].flags = MEDIA_LNK_FL_ENABLED;
    Graph partialGraph; assert(decodeTopology(partial, partialGraph)); assert(validGraph(partialGraph, active)); assert(phase(active) == "invalid"); // transaction must deny
    assert(!readFreshTopology(-1, neutral));
    mockTop = &base.top;
    mockMode = mockStep = 0;
    Graph native;
    assert(readFreshTopology(17, native, fakeIoctl));
    assert(native.identity == neutral.identity);
    for (int mode = 1; mode != 8; ++mode) {
        mockMode = mode;
        mockStep = 0;
        native = neutral;
        assert(!readFreshTopology(17, native, fakeIoctl));
        assert(native.identity == neutral.identity);
    }
    assert(!readFreshTopology(17, native, nullptr));
    std::cout << "PASS native v2 graph: 3 phases, 44 entities, 84 pads, "
                 "119 data edges, 44 interfaces; " << rejected
              << " malformed/topology/route negatives; 7 simulated ioctl failures; invalid fd denied\n";
}
