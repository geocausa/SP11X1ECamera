/* SPDX-License-Identifier: MIT
 * Source-only SP11 media-link transaction adapter. NOT live-admitted.
 * Caller must hold and independently prove exclusive, quiescent ownership.
 */
#pragma once
#include "sp11-media-topology.h"
#include <functional>
#include <map>
#include <string>
#include <utility>

namespace sp11 {
inline bool sameGraph(const Graph &a, const Graph &b)
{
    return a.malformed == b.malformed && a.pads == b.pads &&
           a.outgoing == b.outgoing && a.incoming == b.incoming &&
           a.identity == b.identity;
}

class NativeSession {
public:
    using Guard = std::function<bool()>;
    NativeSession(int mediaFd, TopologyIoctl ioctlFn, Guard owns, Guard stopped)
        : fd_(mediaFd), ioctl_(ioctlFn), owns_(std::move(owns)),
          stopped_(std::move(stopped)),
          transaction_([this](Graph &g) { return read(g); },
                       [this](const Edge &e, bool state) { return write(e, state); },
                       [this]() { return idle(); })
    {
    }
    bool initialize() { return transaction_.initialize(); }
    bool adoptStoppedRouteAndNeutralize()
    {
        return transaction_.initialize(true);
    }
    bool transition(const std::string &name)
    {
        return transaction_.transition(name);
    }
    bool poisoned() const { return transaction_.poisoned(); }

private:
    bool idle() const
    {
        /* Both predicates must refer to the CURRENT session, not a stale
         * launch-time check. Missing callbacks fail closed. The caller must
         * enforce process-level ownership and prove no active sensor/readers.
         */
        return fd_ >= 0 && ioctl_ && owns_ && stopped_ &&
               owns_() && stopped_();
    }
    bool read(Graph &out)
    {
        if (!idle()) return false;
        Graph graph;
        if (!readFreshTopology(fd_, graph, ioctl_)) return false;
        lastGraph_ = graph;
        out = std::move(graph);
        return true;
    }
    bool write(const Edge &edge, bool enable)
    {
        if (!idle()) return false;
        /* The transaction already took a pre-write snapshot. Check a
         * SECOND fresh kernel read immediately before any SETUP_LINK.
         */
        Graph now;
        Topology top;
        if (!readFreshTopology(fd_, now, ioctl_, &top) ||
            !sameGraph(now, lastGraph_) || !idle())
            return false;
        std::map<unsigned, std::string> names;
        std::map<unsigned, media_v2_pad> pads;
        for (const auto &e : top.entities)
            names[e.id] = entityName(e);
        for (const auto &p : top.pads)
            pads.emplace(p.id, p);
        media_link_desc desc{};
        unsigned matches = 0;
        for (const auto &link : top.links) {
            if ((link.flags & MEDIA_LNK_FL_LINK_TYPE) !=
                MEDIA_LNK_FL_DATA_LINK)
                continue;
            const auto &source = pads.at(link.source_id);
            const auto &sink = pads.at(link.sink_id);
            Edge candidate{names.at(source.entity_id), source.index,
                           names.at(sink.entity_id), sink.index};
            if (candidate != edge) continue;
            if ((link.flags & MEDIA_LNK_FL_IMMUTABLE) ||
                (link.flags & MEDIA_LNK_FL_ENABLED) ==
                    (enable ? MEDIA_LNK_FL_ENABLED : 0))
                return false;
            desc.source.entity = source.entity_id;
            desc.source.index = source.index;
            desc.sink.entity = sink.entity_id;
            desc.sink.index = sink.index;
            desc.flags = enable ? MEDIA_LNK_FL_ENABLED : 0;
            ++matches;
        }
        if (matches != 1 || !idle()) return false;
        /* The only side-effecting syscall. The transaction must verify
         * the complete kernel graph again before considering it accepted.
         */
        return ioctl_(fd_, MEDIA_IOC_SETUP_LINK, &desc) == 0;
    }
    int fd_;
    TopologyIoctl ioctl_;
    Guard owns_, stopped_;
    Graph lastGraph_;
    Transaction transaction_;
};
} /* namespace sp11 */
