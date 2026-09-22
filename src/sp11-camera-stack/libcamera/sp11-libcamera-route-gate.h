/* SPDX-License-Identifier: MIT
 * SP11 RGB-only integration boundary for libcamera Simple.
 * Source-only: no device fd, OS lease, stream-stop proof or installation.
 */
#pragma once
#include "sp11-native-session.h"
#include <memory>
#include <string>
#include <string_view>

namespace sp11 {
class LibcameraRouteGate {
public:
    /* Caller must own the previously opened exact CAMSS media fd, supply
     * current exclusive/quiescent proof and retain fd+lease through STOP.
     * If independent proofs cannot be established, do not call attach().
     */
    bool attach(std::unique_ptr<NativeSession> session)
    {
        if (everAttached_ || !session || session->poisoned()) return false;
        everAttached_ = true;
        session_ = std::move(session);
        if (!session_->initialize()) {
            session_.reset();
            return false;
        }
        return true;
    }
    bool admitted() const { return !failed_ && !!session_ && !session_->poisoned(); }
    bool streaming() const { return streaming_; }

    static std::string camera(std::string_view sensor)
    {
        const auto name = canonical(sensor);
        if (name == "imx681") return "front";
        if (name == "ov13858") return "rear";
        return {};
    }

    /* Intercepts BOTH SimpleCameraData::init() and configure() setupLinks.
     * Never call MediaLink::setEnabled in the CAMSS branch.
     */
    bool setupLinks(std::string_view sensor)
    {
        if (!admitted() || streaming_) return fail();
        const std::string target = camera(sensor);
        if (target.empty()) return fail();
        if (!session_->transition(target)) return fail();
        selected_ = target;
        return true;
    }

    /* Called BEFORE libcamera start and AFTER hardware stop. If no stream
     * starts, the hardware routing controller can still return to neutral.
     */
    bool beforeStream(std::string_view sensor)
    {
        if (!admitted() || streaming_ || camera(sensor) != selected_ ||
            !session_->transition(selected_))
            return fail();
        streaming_ = true;
        return true;
    }
    void retireUncertainStreamStop()
    {
        /* streamOff() returned an error: never attempt neutral with a
         * potentially running sensor; only the outer guarded one-shot
         * reboot can recover this untrusted hardware state.
         */
        failed_ = true;
    }
    bool afterStream()
    {
        /* libcamera invokes stopDevice() after partial start failures.
         * That is also valid if STREAMON never happened, or if the
         * pipeline already returned neutral. Do not manufacture a
         * failure solely because no stream was active.
         */
        if (!admitted()) return fail();
        streaming_ = false;
        selected_.clear();
        if (!session_->transition("neutral")) return fail();
        return true;
    }
    bool parkRouteUntilStart()
    {
        /* Leave the sensor choice intact, but park the hardware neutral
         * after configuration and before app STREAMON.
         */
        if (!admitted() || streaming_ || selected_.empty()) return fail();
        if (!session_->transition("neutral")) return fail();
        return true;
    }
    bool neutralizeWhenIdle()
    {
        if (!admitted() || streaming_) return fail();
        selected_.clear();
        if (!session_->transition("neutral")) return fail();
        return true;
    }

    /* Must not reset ACTIVE subdevice routing unless separately audited.
     * An empty/TRY-only route check is not equivalent to an active reset.
     */
    static bool allowActiveRoutingReset() { return false; }

private:
    bool fail()
    {
        failed_ = true;
        return false;
    }
    bool everAttached_ = false;
    bool streaming_ = false;
    bool failed_ = false;
    std::string selected_;
    std::unique_ptr<NativeSession> session_;
};
} /* namespace sp11 */
