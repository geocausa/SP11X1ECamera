/* SPDX-License-Identifier: MIT
 * SP11-only, read-only native media topology snapshot for guarded RGB routing.
 * This adapter never changes a link, opens a sensor, or starts a camera.
 */
#pragma once
#include "sp11-rgb-graph.h"
#include <algorithm>
#include <cerrno>
#include <cstring>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <linux/media.h>
#include <sys/ioctl.h>

namespace sp11 {

struct Topology {
    std::vector<media_v2_entity> entities;
    std::vector<media_v2_interface> interfaces;
    std::vector<media_v2_pad> pads;
    std::vector<media_v2_link> links;
};

inline std::string entityName(const media_v2_entity &e)
{
    const auto *end = static_cast<const char *>(
        std::memchr(e.name, '\0', sizeof(e.name)));
    if (!end || end == e.name) return {};
    return canonical(std::string(e.name, end));
}

/* Reject missing, duplicate, foreign and malformed topology components.
 * Stable identities include immutable kernel IDs, but not topology_version,
 * which the kernel may update after intentional link-state changes.
 */
inline bool decodeTopology(const Topology &top, Graph &out)
{
    Graph graph;
    if (top.entities.size() != 44 || top.interfaces.size() != 44 ||
        top.pads.size() != 84 || top.links.size() != 163)
        return false;
    std::map<unsigned, std::string> names;
    std::map<unsigned, std::pair<std::string, unsigned>> pads;
    std::map<std::string, std::map<unsigned, unsigned>> flags;
    std::set<unsigned> ids;
    auto unique = [&](unsigned id) { return id && ids.insert(id).second; };
    for (const auto &e : top.entities) {
        auto name = entityName(e);
        if (name.empty() || !unique(e.id) || graph.pads.count(name))
            return false;
        names[e.id] = name;
        graph.pads[name] = {};
        graph.identity.push_back("e:" + std::to_string(e.id) + ":" + name);
    }
    std::set<unsigned> interface_ids;
    for (const auto &intf : top.interfaces) {
        if (!unique(intf.id) ||
            (intf.intf_type != MEDIA_INTF_T_V4L_VIDEO &&
             intf.intf_type != MEDIA_INTF_T_V4L_SUBDEV) ||
            intf.devnode.major == 0 || !interface_ids.insert(intf.id).second)
            return false;
        graph.identity.push_back("i:" + std::to_string(intf.id) + ":" +
                                 std::to_string(intf.devnode.major) + ":" +
                                 std::to_string(intf.devnode.minor));
    }
    for (const auto &p : top.pads) {
        auto name = names.find(p.entity_id);
        if (!unique(p.id) || name == names.end() || p.index >= 8 ||
            (p.flags != MEDIA_PAD_FL_SINK && p.flags != MEDIA_PAD_FL_SOURCE) ||
            !flags[name->second].emplace(p.index, p.flags).second)
            return false;
        pads.emplace(p.id, std::make_pair(name->second, p.index));
        graph.identity.push_back("p:" + std::to_string(p.id) + ":" +
                                 std::to_string(p.entity_id) + ":" +
                                 std::to_string(p.index));
    }
    for (auto &[name, byIndex] : flags) {
        auto &destination = graph.pads[name];
        for (unsigned index = 0; index < byIndex.size(); ++index) {
            auto item = byIndex.find(index);
            if (item == byIndex.end()) return false;
            destination.push_back(item->second);
        }
    }
    std::set<unsigned> usedInterfaces, linkedEntities;
    unsigned dataLinks = 0, interfaceLinks = 0;
    for (const auto &l : top.links) {
        if (!unique(l.id)) return false;
        unsigned type = l.flags & MEDIA_LNK_FL_LINK_TYPE;
        if (type == MEDIA_LNK_FL_INTERFACE_LINK) {
            if ((l.flags & ~MEDIA_LNK_FL_LINK_TYPE) !=
                    (MEDIA_LNK_FL_ENABLED | MEDIA_LNK_FL_IMMUTABLE) ||
                !interface_ids.count(l.source_id) ||
                !names.count(l.sink_id) ||
                !usedInterfaces.insert(l.source_id).second ||
                !linkedEntities.insert(l.sink_id).second)
                return false;
            ++interfaceLinks;
            graph.identity.push_back("il:" + std::to_string(l.id) + ":" +
                 std::to_string(l.source_id) + ":" + std::to_string(l.sink_id));
            continue;
        }
        if (type != MEDIA_LNK_FL_DATA_LINK ||
            (l.flags & ~(MEDIA_LNK_FL_LINK_TYPE | MEDIA_LNK_FL_ENABLED |
                         MEDIA_LNK_FL_IMMUTABLE)) != 0)
            return false;
        auto source = pads.find(l.source_id), sink = pads.find(l.sink_id);
        if (source == pads.end() || sink == pads.end()) return false;
        Edge edge{source->second.first, source->second.second,
                  sink->second.first, sink->second.second};
        if (!graph.outgoing.emplace(edge, l.flags).second ||
            !graph.incoming.emplace(edge, l.flags).second)
            return false;
        graph.identity.push_back("dl:" + std::to_string(l.id) + ":" +
             std::to_string(l.source_id) + ":" + std::to_string(l.sink_id));
        ++dataLinks;
    }
    if (dataLinks != 119 || interfaceLinks != 44 ||
        usedInterfaces.size() != 44 || linkedEntities.size() != 44 ||
        pads.size() != 84)
        return false;
    std::sort(graph.identity.begin(), graph.identity.end());
    State enabled;
    if (!validGraph(graph, enabled)) return false;
    out = std::move(graph);
    return true;
}

/* fd is a previously opened exact CAMSS media device; no path enumeration,
 * automatic retries, caching, or writes. A torn/version-changed snapshot
 * fails closed. The caller separately owns quiescence and exclusive access.
 */
using TopologyIoctl = int (*)(int, unsigned long, void *);
inline int kernelTopologyIoctl(int fd, unsigned long request, void *arg)
{
    return ::ioctl(fd, request, arg);
}
inline bool readFreshTopology(int fd, Graph &out,
                              TopologyIoctl request = kernelTopologyIoctl)
{
    if (fd < 0 || !request) return false;
    media_device_info info{};
    if (request(fd, MEDIA_IOC_DEVICE_INFO, &info) < 0 ||
        std::strncmp(info.driver, "qcom-camss", sizeof(info.driver)) ||
        std::strncmp(info.bus_info, "platform:acb7000.isp",
                     sizeof(info.bus_info)))
        return false;
    media_v2_topology first{};
    if (request(fd, MEDIA_IOC_G_TOPOLOGY, &first) < 0 ||
        first.num_entities != 44 || first.num_interfaces != 44 ||
        first.num_pads != 84 || first.num_links != 163)
        return false;
    Topology payload;
    payload.entities.resize(first.num_entities);
    payload.interfaces.resize(first.num_interfaces);
    payload.pads.resize(first.num_pads);
    payload.links.resize(first.num_links);
    media_v2_topology second{};
    second.num_entities = first.num_entities;
    second.num_interfaces = first.num_interfaces;
    second.num_pads = first.num_pads;
    second.num_links = first.num_links;
    second.ptr_entities = reinterpret_cast<__u64>(payload.entities.data());
    second.ptr_interfaces = reinterpret_cast<__u64>(payload.interfaces.data());
    second.ptr_pads = reinterpret_cast<__u64>(payload.pads.data());
    second.ptr_links = reinterpret_cast<__u64>(payload.links.data());
    if (request(fd, MEDIA_IOC_G_TOPOLOGY, &second) < 0 ||
        first.topology_version != second.topology_version ||
        first.num_entities != second.num_entities ||
        first.num_interfaces != second.num_interfaces ||
        first.num_pads != second.num_pads ||
        first.num_links != second.num_links)
        return false;
    return decodeTopology(payload, out);
}
} /* namespace sp11 */
