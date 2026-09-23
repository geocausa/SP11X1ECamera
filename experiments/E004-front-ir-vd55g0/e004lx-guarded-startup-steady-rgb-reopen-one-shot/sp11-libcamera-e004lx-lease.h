/* SPDX-License-Identifier: MIT
 * Offline candidate ONLY: experimental SP11 libcamera Simple routing lease.
 * Not production exclusivity. Requires a distinct guarded one-shot boot and
 * root-only service preflight before any CameraManager activation.
 */
#pragma once
#include "sp11-libcamera-route-gate.h"
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <memory>
#include <string>
#include <unistd.h>

namespace sp11 {
class ExperimentalLibcameraLease {
public:
    ~ExperimentalLibcameraLease()
    {
        /* Do not guess rollback here: the dedicated one-shot runner must
         * return to Golden on ANY uncertain state or process exit.
         */
        if (fd_ >= 0) ::close(fd_);
    }
    ExperimentalLibcameraLease(const ExperimentalLibcameraLease &) = delete;
    ExperimentalLibcameraLease &operator=(const ExperimentalLibcameraLease &) = delete;
    ExperimentalLibcameraLease() = default;

    bool initialize(const std::string &mediaNode)
    {
        if (attempted_ || ::geteuid() != 0 || mediaNode != "/dev/media0" ||
            !bootAuthorized()) return false;
        attempted_ = true;
        if (!sensorsSuspended() || !cameraNodesRootOnly()) return false;
        fd_ = ::open(mediaNode.c_str(), O_RDWR | O_CLOEXEC | O_NOFOLLOW |
                                       O_NONBLOCK);
        if (fd_ < 0) return false;
        if (::lockf(fd_, F_TLOCK, 0) < 0) return false;
        locked_ = true;
        auto owner = [this] {
            return locked_ && fd_ >= 0 && ::fcntl(fd_, F_GETFD) >= 0 &&
                   cameraNodesRootOnly();
        };
        auto idle = [this] {
            return !streaming_ && sensorsSuspended();
        };
        return gate_.attach(std::make_unique<NativeSession>(
            fd_, kernelTopologyIoctl, owner, idle));
    }
    bool ready() const { return locked_ && gate_.admitted(); }
    bool setupLinks(const std::string &name)
    {
        return ready() && gate_.setupLinks(name);
    }
    bool beforeStream(const std::string &name)
    {
        if (!ready()) return false;
        if (!gate_.beforeStream(name)) return false;
        streaming_ = true;
        return true;
    }
    void retireUncertainStreamStop()
    {
        gate_.retireUncertainStreamStop();
    }
    bool afterStream()
    {
        /* The worker has already completed streamOff; stopDevice may
         * also be called after failing before STREAMON. The callback
         * must test quiescence now, not an earlier configured state.
         */
        streaming_ = false;
        return ready() && gate_.afterStream();
    }
    bool parkRouteUntilStart()
    {
        return ready() && gate_.parkRouteUntilStart();
    }
    bool neutralizeWhenIdle()
    {
        return ready() && gate_.neutralizeWhenIdle();
    }
    /* There is no independent active-subdevice-routing validator yet.
     * Reject hasStreams() devices before the Simple resetRoutingTable path.
     */
    static bool allowActiveRoutingReset() { return false; }

private:
    /* DAC, unlike a cooperative media-fd lock, denies every non-root
     * process access to the actual video, media and subdevice nodes.
     * The candidate runner applies 0600 root:root AFTER device creation,
     * checks no preexisting fds, and confirms the seal before launch.
     * Recheck on EVERY kernel graph transition, not just admission.
     * Root-equivalent adversaries are explicitly OUTSIDE this limited
     * single-use test's security model: this is NOT production ownership.
     */
    static bool cameraNodesRootOnly()
    {
        DIR *dir = ::opendir("/dev");
        if (!dir) return false;
        unsigned mediaCount=0, videoCount=0, subdevCount=0;
        bool good=true;
        for (struct dirent *entry; (entry=::readdir(dir)); ) {
            const std::string name(entry->d_name);
            std::string type;
            if (name == "media0") type = "media";
            else if (name.rfind("video", 0) == 0 &&
                     name.size() > 5) type = "video";
            else if (name.rfind("v4l-subdev", 0) == 0 &&
                     name.size() > 10) type = "subdev";
            else if (name.rfind("media", 0) == 0 &&
                     name.size() > 5) { good=false; break; }
            else continue;
            const auto first = type == "video" ? 5U :
                               type == "subdev" ? 10U : name.size();
            for (size_t i=first; i<name.size(); ++i)
                if (name[i] < '0' || name[i] > '9') good=false;
            if (!good) break;
            const std::string path = "/dev/" + name;
            struct stat st{};
            if (::lstat(path.c_str(), &st) ||
                !S_ISCHR(st.st_mode) || st.st_uid != 0 || st.st_gid != 0 ||
                (st.st_mode & 0777) != 0600) { good=false; break; }
            if (type == "media") ++mediaCount;
            else if (type == "video") ++videoCount;
            else ++subdevCount;
        }
        ::closedir(dir);
        return good && mediaCount == 1 && videoCount == 16 &&
               subdevCount == 28;
    }
    static bool bootAuthorized()
    {
        FILE *stream = std::fopen("/proc/cmdline", "r");
        if (!stream) return false;
        char text[8192]{};
        const bool got = std::fgets(text, sizeof(text), stream);
        std::fclose(stream);
        return got &&
               std::strstr(text, "sp11_camera_e004lx_xrgb8888=1") &&
               std::strstr(text, "sp11_entry=7.1.5-sp11-camera-e004lx-xrgb8888") &&
               std::strstr(text, "modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0");
    }
    static bool sensorsSuspended()
    {
        /* Scan dynamic CCI bus names; require each exact sensor in standby.
         * A bounded one-shot launcher separately refuses all external
         * video/subdev readers before starting libcamera.
         */
        unsigned count = 0;
        for (const char *model : {"sony,imx681", "ovti,ov13858",
                                  "microsoft,sp11-vd55g0"}) {
            bool found = false;
            for (int bus = 0; bus != 32; ++bus) {
                for (const char *address : {"0010", "0060"}) {
                    const std::string base = "/sys/bus/i2c/devices/" +
                        std::to_string(bus) + "-" + address;
                    FILE *compatible = std::fopen((base + "/of_node/compatible").c_str(),"rb");
                    if (!compatible) continue;
                    char name[128]{};
                    auto size = std::fread(name, 1, sizeof(name), compatible);
                    std::fclose(compatible);
                    if (!size || std::string(name) != model) continue;
                    FILE *status = std::fopen((base + "/power/runtime_status").c_str(),"r");
                    if (!status) return false;
                    char state[48]{};
                    bool read = std::fgets(state, sizeof(state), status);
                    std::fclose(status);
                    if (!read || std::strcmp(state, "suspended\n")) return false;
                    ++count;
                    found = true;
                }
            }
            if (!found) return false;
        }
        return count == 3;
    }
    bool attempted_ = false;
    bool locked_ = false;
    bool streaming_ = false;
    int fd_ = -1;
    LibcameraRouteGate gate_;
};
} /* namespace sp11 */
