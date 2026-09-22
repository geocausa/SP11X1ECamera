/* SPDX-License-Identifier: MIT */
#pragma once
#include <functional>
#include <map>
#include <set>
#include <string>
#include <tuple>
#include <vector>
#include <linux/media.h>
#include "sp11-rgb-paths.h"

namespace sp11 {
using Edge = std::tuple<std::string, unsigned int, std::string, unsigned int>;
using State = std::set<Edge>;
struct Graph {
    std::map<std::string, std::vector<unsigned int>> pads;
    std::map<Edge, unsigned int> outgoing, incoming;
    std::vector<std::string> identity;
    bool malformed = false;
};
inline State route(const std::string &camera)
{
    if (camera == "front")
        return { {"msm_csiphy2", 1, "msm_csid1", 0},
                 {"msm_csid1", 1, "msm_vfe1_rdi0", 0} };
    if (camera == "rear")
        return { {"msm_csiphy1", 1, "msm_csid0", 0},
                 {"msm_csid0", 1, "msm_vfe0_rdi0", 0} };
    return {};
}
inline std::vector<Edge> orderedRoute(const std::string &camera)
{
    if (camera == "front")
        return { {"msm_csiphy2", 1, "msm_csid1", 0},
                 {"msm_csid1", 1, "msm_vfe1_rdi0", 0} };
    if (camera == "rear")
        return { {"msm_csiphy1", 1, "msm_csid0", 0},
                 {"msm_csid0", 1, "msm_vfe0_rdi0", 0} };
    return {};
}
inline bool validGraph(const Graph &graph, State &enabled)
{
    if (graph.malformed || graph.outgoing != graph.incoming)
        return false;
    std::map<std::string, std::vector<unsigned int>> pads;
    std::map<Edge, bool> edges;
    auto add = [&](const std::string &a, unsigned ap,
                   const std::string &b, unsigned bp, bool immutable = false) {
        edges[{a, ap, b, bp}] = immutable;
    };
    for (int phy : {0, 1, 2, 4}) {
        std::string name = "msm_csiphy" + std::to_string(phy);
        pads[name] = {MEDIA_PAD_FL_SINK, MEDIA_PAD_FL_SOURCE};
        for (int csid = 0; csid != 5; ++csid)
            add(name, 1, "msm_csid" + std::to_string(csid), 0);
    }
    for (int csid = 0; csid != 5; ++csid)
        pads["msm_csid" + std::to_string(csid)] =
            {MEDIA_PAD_FL_SINK, MEDIA_PAD_FL_SOURCE, MEDIA_PAD_FL_SOURCE,
             MEDIA_PAD_FL_SOURCE, MEDIA_PAD_FL_SOURCE};
    for (int vfe = 0; vfe != 4; ++vfe) {
        std::string prefix = "msm_vfe" + std::to_string(vfe);
        for (int port = 0; port != 4; ++port) {
            std::string capture = prefix + "_" +
                (vfe < 2 && port == 3 ? "pix" : "rdi" + std::to_string(port));
            std::string video = prefix + "_video" + std::to_string(port);
            pads[capture] = {MEDIA_PAD_FL_SINK, MEDIA_PAD_FL_SOURCE};
            pads[video] = {MEDIA_PAD_FL_SINK};
            add(capture, 1, video, 0, true);
            for (int csid = 0; csid != 5; ++csid)
                add("msm_csid" + std::to_string(csid), port + 1, capture, 0);
        }
    }
    for (const auto &[sensor, phy] :
         std::map<std::string, int>{{"imx681",2},{"ov13858",1},{"sp11-vd55g0",0}}) {
        pads[sensor] = {MEDIA_PAD_FL_SOURCE};
        add(sensor, 0, "msm_csiphy" + std::to_string(phy), 0, true);
    }
    if (graph.pads != pads || graph.outgoing.size() != edges.size())
        return false;
    enabled.clear();
    for (const auto &[edge, immutable] : edges) {
        auto found = graph.outgoing.find(edge);
        if (found == graph.outgoing.end())
            return false;
        unsigned flags = found->second;
        if (immutable) {
            if (flags != (MEDIA_LNK_FL_ENABLED | MEDIA_LNK_FL_IMMUTABLE))
                return false;
        } else {
            if (flags != 0 && flags != MEDIA_LNK_FL_ENABLED)
                return false;
            if (flags)
                enabled.insert(edge);
        }
    }
    return true;
}
inline std::string phase(const State &state)
{
    if (state.empty()) return "neutral";
    if (state == route("front")) return "front";
    if (state == route("rear")) return "rear";
    return "invalid";
}
class Transaction {
public:
    using Read = std::function<bool(Graph &)>;
    using Write = std::function<bool(const Edge &, bool)>;
    using Idle = std::function<bool()>;
    Transaction(Read read, Write write, Idle idle)
        : read_(read), write_(write), idle_(idle) {}
    bool initialize(bool adoptAndNeutralize = false)
    {
        if (initialized_ || poisoned_) return false;
        poisoned_ = true;
        Graph graph;
        if (!idle_() || !read_(graph) || !validGraph(graph, expected_))
            return false;
        const auto initial = phase(expected_);
        if (initial == "invalid" ||
            (initial != "neutral" && !adoptAndNeutralize))
            return false;
        identity_ = graph.identity;
        initialized_ = true;
        poisoned_ = false;
        /* An explicitly adopted complete front/rear route may be
         * DISABLED only with independently verified idle/ownership
         * guards. Failure poisons the session, never guesses rollback.
         */
        if (initial != "neutral")
            return transition("neutral");
        return true;
    }
    bool transition(const std::string &target)
    {
        if (!initialized_ || poisoned_) return false;
        poisoned_ = true; /* Includes callback exceptions/uncertain writes. */
        if ((target != "neutral" && target != "front" && target != "rear") ||
            !verify()) return false;
        std::string current = phase(expected_);
        if (current == "invalid") return false;
        if (current != target) {
            auto before = orderedRoute(current);
            for (auto it = before.rbegin(); it != before.rend(); ++it)
                if (!change(*it, false)) return false;
            for (const Edge &edge : orderedRoute(target))
                if (!change(edge, true)) return false;
        }
        if (!verify() || expected_ != route(target)) return false;
        poisoned_ = false;
        return true;
    }
    bool poisoned() const { return poisoned_; }
private:
    bool verify()
    {
        Graph graph;
        State state;
        return idle_() && read_(graph) && validGraph(graph, state) &&
               graph.identity == identity_ && state == expected_;
    }
    bool change(const Edge &edge, bool enable)
    {
        if (!verify() || !write_(edge, enable)) return false;
        if (enable) expected_.insert(edge);
        else expected_.erase(edge);
        return verify();
    }
    Read read_;
    Write write_;
    Idle idle_;
    State expected_;
    std::vector<std::string> identity_;
    bool initialized_ = false, poisoned_ = false;
};
} /* namespace sp11 */
