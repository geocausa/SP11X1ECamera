/* SPDX-License-Identifier: MIT
 * Explicit SP11 RGB path selection. Not a graph transaction/ownership guard.
 */
#pragma once

#include <array>
#include <cctype>
#include <string>
#include <string_view>

namespace sp11 {

inline std::string canonical(std::string_view name)
{
    for (const auto &sensor : { "imx681", "ov13858", "sp11-vd55g0" }) {
        std::string prefix = std::string(sensor) + " ";
        if (name.substr(0, prefix.size()) != prefix)
            continue;
        auto address = name.substr(prefix.size());
        auto dash = address.find('-');
        std::string_view expected = std::string_view(sensor) == "sp11-vd55g0"
                                  ? "0060" : "0010";
        if (dash == std::string_view::npos || dash == 0 ||
            address.substr(dash + 1) != expected)
            continue;
        bool digits = true;
        for (char c : address.substr(0, dash))
            digits &= c >= '0' && c <= '9';
        if (digits)
            return sensor;
    }
    return std::string(name);
}

inline std::array<std::string_view, 5> path(std::string_view sensor)
{
    const std::string model = canonical(sensor);
    if (model == "imx681")
        return { "imx681", "msm_csiphy2", "msm_csid1",
                 "msm_vfe1_rdi0", "msm_vfe1_video0" };
    if (model == "ov13858")
        return { "ov13858", "msm_csiphy1", "msm_csid0",
                 "msm_vfe0_rdi0", "msm_vfe0_video0" };
    return {};
}

inline bool sensorAllowed(std::string_view sensor)
{
    return !path(sensor)[0].empty();
}

inline bool edgeAllowed(std::string_view sensor,
                        std::string_view source, unsigned int sourcePad,
                        std::string_view sink, unsigned int sinkPad)
{
    auto route = path(sensor);
    if (route[0].empty())
        return false;
    std::string a = canonical(source), b = canonical(sink);
    for (unsigned int i = 0; i != 4; ++i) {
        if (a == route[i] && b == route[i + 1] &&
            sourcePad == (i == 0 ? 0U : 1U) && sinkPad == 0)
            return true;
    }
    return false;
}
} /* namespace sp11 */
