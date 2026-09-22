/* SPDX-License-Identifier: MIT
 * One-shot, strictly read-only SP11 camera topology diagnostic.
 * No source files/images, STREAMON, SETUP_LINK, libcamera, PMIC or IR action.
 */
#include "sp11-media-topology.h"
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <linux/media.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string>

static int readOnlyIoctl(int fd, unsigned long request, void *arg)
{
    if (request != MEDIA_IOC_DEVICE_INFO &&
        request != MEDIA_IOC_G_TOPOLOGY) {
        errno = EPERM;
        return -1;
    }
    return ::ioctl(fd, request, arg);
}
int main(int argc, char **argv)
{
    if (argc != 2 || ::geteuid() != 0) {
        std::fputs("DENY: root and one exact /dev/mediaN argument required\n", stderr);
        return 2;
    }
    const std::string node(argv[1]);
    if (node.rfind("/dev/media", 0) != 0 ||
        node.size() < 11 || node.size() > 14 ||
        node.find_first_not_of("0123456789", 10) != std::string::npos) {
        std::fputs("DENY: media-node spelling\n", stderr);
        return 2;
    }
    FILE *cmdline = std::fopen("/proc/cmdline", "r");
    if (!cmdline) return 3;
    char line[8192]{};
    const bool bounded = std::fgets(line, sizeof(line), cmdline) &&
        std::strstr(line, "sp11_camera_e004lk_v2_probe=1") &&
        std::strstr(line, "sp11_entry=7.1.5-sp11-camera-e004lk-v2-probe");
    std::fclose(cmdline);
    if (!bounded) {
        std::fputs("DENY: no unique guarded diagnostic boot marker\n", stderr);
        return 3;
    }
    const int fd = ::open(node.c_str(), O_RDONLY | O_CLOEXEC | O_NOFOLLOW |
                                      O_NONBLOCK);
    if (fd < 0) {
        std::perror("DENY: media node open");
        return 4;
    }
    struct stat st{};
    if (::fstat(fd, &st) || !S_ISCHR(st.st_mode)) {
        std::fputs("DENY: media node is not a character device\n", stderr);
        ::close(fd);
        return 4;
    }
    media_v2_topology counts{};
    if (readOnlyIoctl(fd, MEDIA_IOC_G_TOPOLOGY, &counts) != 0) {
        std::fputs("E004LK_V2_COUNTS=IOCTL_FAILED\n", stderr);
        ::close(fd);
        return 5;
    }
    std::printf("kernel_v2_counts=%u,%u,%u,%u\n",
                counts.num_entities, counts.num_interfaces,
                counts.num_pads, counts.num_links);
    std::fflush(stdout);
    sp11::Graph graph;
    sp11::Topology top;
    const bool ok = sp11::readFreshTopology(fd, graph, readOnlyIoctl, &top);
    ::close(fd);
    if (!ok) {
        std::fputs("E004LK_V2_TOPOLOGY=REJECTED\n", stderr);
        return 5;
    }
    sp11::State enabled;
    if (!sp11::validGraph(graph, enabled)) return 5;
    const std::string current = sp11::phase(enabled);
    if (current == "invalid") {
        std::fputs("E004LK_UNADMITTED_INITIAL_ROUTE=REJECTED\n", stderr);
        return 6;
    }
    std::printf("E004LK_V2_TOPOLOGY=PASS\n"
                "entities=%zu interfaces=%zu pads=%zu links=%zu\n"
                "enabled_mutable_links=%zu\ninitial_route=%s\n"
                "all_ioctls=READ_ONLY\nno_camera_stream_or_route_mutation=YES\n",
                top.entities.size(), top.interfaces.size(),
                top.pads.size(), top.links.size(), enabled.size(),
                current.c_str());
    return 0;
}
