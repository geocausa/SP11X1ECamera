/* SPDX-License-Identifier: MIT
 * E004ll single-use, bounded, non-streaming native SP11 media route check.
 * Only on dedicated one-shot boot. Not an installed driver or libcamera backend.
 */
#include "sp11-native-session.h"
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string>

static bool bootAuthorized()
{
    FILE *stream = std::fopen("/proc/cmdline", "r");
    if (!stream) return false;
    char text[8192]{};
    const bool got = std::fgets(text, sizeof(text), stream);
    std::fclose(stream);
    return got &&
           std::strstr(text, "sp11_camera_e004ll_native_route=1") &&
           std::strstr(text, "sp11_entry=7.1.5-sp11-camera-e004ll-native-route") &&
           std::strstr(text, "modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0");
}

static bool sensorsSuspended()
{
    /* The one-shot shell checks exact compat strings and sensor runtime
     * states before entry. These three discovered devices are rechecked on
     * each transaction callback; bus numbers are not assumed.
     */
    unsigned matches = 0;
    for (const char *model : {"sony,imx681", "ovti,ov13858",
                              "microsoft,sp11-vd55g0"}) {
        bool found = false;
        for (int bus = 0; bus != 32; ++bus) {
            for (const char *address : {"0010", "0060"}) {
                const std::string base = "/sys/bus/i2c/devices/" +
                    std::to_string(bus) + "-" + address;
                FILE *compatible = std::fopen((base + "/of_node/compatible").c_str(), "rb");
                if (!compatible) continue;
                char name[128]{};
                auto size = std::fread(name, 1, sizeof(name), compatible);
                std::fclose(compatible);
                if (size == 0 || std::string(name) != model) continue;
                FILE *status = std::fopen((base + "/power/runtime_status").c_str(), "r");
                if (!status) return false;
                char state[48]{};
                bool read = std::fgets(state, sizeof(state), status);
                std::fclose(status);
                if (!read || std::strcmp(state, "suspended\n")) return false;
                found = true;
                ++matches;
            }
        }
        if (!found) return false;
    }
    return matches == 3;
}

int main(int argc, char **argv)
{
    if (::geteuid() || argc != 2 || std::string(argv[1]) != "/dev/media0" ||
        !bootAuthorized()) {
        std::fputs("E004LL_DENY=UNAUTHORIZED_BOOT_OR_ARGUMENT\n", stderr);
        return 2;
    }
    if (!sensorsSuspended()) {
        std::fputs("E004LL_DENY=SENSOR_NOT_SUSPENDED\n", stderr);
        return 3;
    }
    int fd = ::open(argv[1], O_RDWR | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
    if (fd < 0) { std::perror("E004LL_DENY=MEDIA_OPEN"); return 4; }
    struct stat st{};
    if (::fstat(fd, &st) || !S_ISCHR(st.st_mode) || ::lockf(fd, F_TLOCK, 0)) {
        std::fputs("E004LL_DENY=MEDIA_NODE_OR_ADVISORY_LOCK\n", stderr);
        ::close(fd);
        return 4;
    }
    bool held = true;
    auto owner = [&]() { return held; };
    sp11::NativeSession transaction(fd, sp11::kernelTopologyIoctl, owner,
                                    sensorsSuspended);
    if (!transaction.initialize()) {
        std::fputs("E004LL_DENY=NON_NEUTRAL_OR_BAD_INITIAL_GRAPH\n", stderr);
        ::close(fd);
        return 5;
    }
    /* No duplicate/parallel sensor routes; deliberate neutral between each. */
    for (const std::string target : {"front","neutral","rear","neutral"}) {
        if (!transaction.transition(target)) {
            std::fprintf(stderr, "E004LL_FAIL_ROUTE=%s POISONED=%u\n",
                         target.c_str(), transaction.poisoned());
            /* NEVER guess a rollback after any uncertain kernel write. The
             * one-shot unit reboots straight to protected Golden on failure.
             */
            ::close(fd);
            return 6;
        }
        std::printf("E004LL_NATIVE_ROUTE=%s FRESH_FULL_GRAPH=PASS\n",
                    target.c_str());
        std::fflush(stdout);
    }
    held = false;
    ::close(fd);
    std::puts("E004LL_NATIVE_ROUTE_CYCLE=PASS STREAMON=0 IR_EMITTER=0");
    return 0;
}
