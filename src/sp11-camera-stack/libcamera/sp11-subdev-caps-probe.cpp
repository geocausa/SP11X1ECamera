/* SPDX-License-Identifier: MIT
 * E004ln one-shot SP11 read-only V4L2 subdevice streams-capability observer.
 * Never writes media links, formats, STREAMON, sensor controls or IR light.
 */
#include "sp11-media-topology.h"
#include <algorithm>
#include <cerrno>
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <linux/v4l2-subdev.h>
#include <map>
#include <set>
#include <string>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>
#include <utility>
#include <vector>

static int mediaReadOnly(int fd, unsigned long command, void *argument)
{
    if (command != MEDIA_IOC_DEVICE_INFO &&
        command != MEDIA_IOC_G_TOPOLOGY) {
        errno = EPERM;
        return -1;
    }
    return ::ioctl(fd, command, argument);
}
static bool bootAuthorized()
{
    FILE *f = std::fopen("/proc/cmdline", "r");
    if (!f) return false;
    char line[8192]{};
    bool got = std::fgets(line, sizeof(line), f);
    std::fclose(f);
    return got &&
        std::strstr(line, "sp11_camera_e004ln_subdev_caps=1") &&
        std::strstr(line, "sp11_entry=7.1.5-sp11-camera-e004ln-subdev-caps") &&
        std::strstr(line, "modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0");
}
int main(int argc, char **argv)
{
    if (::geteuid() != 0 || argc != 2 ||
        std::string(argv[1]) != "/dev/media0" || !bootAuthorized()) {
        std::fputs("E004LN_DENY=BOOT_OR_ARGUMENT\n", stderr);
        return 2;
    }
    int media = ::open(argv[1], O_RDONLY|O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC);
    if (media < 0) return 3;
    sp11::Graph graph;
    sp11::Topology topology;
    sp11::State active;
    if (!sp11::readFreshTopology(media, graph, mediaReadOnly, &topology) ||
        !sp11::validGraph(graph, active) || !active.empty()) {
        std::fputs("E004LN_DENY=NOT_FRESH_COMPLETE_NEUTRAL_GRAPH\n", stderr);
        ::close(media);
        return 4;
    }
    ::close(media);
    std::map<unsigned, media_v2_interface> interfaceById;
    std::map<unsigned, std::string> names;
    std::map<unsigned, std::string> entityByInterface;
    std::set<unsigned> linkedInterfaces;
    for (const auto &item : topology.interfaces)
        interfaceById.emplace(item.id, item);
    for (const auto &item : topology.entities)
        names.emplace(item.id, sp11::entityName(item));
    for (const auto &link : topology.links) {
        if ((link.flags & MEDIA_LNK_FL_LINK_TYPE) !=
            MEDIA_LNK_FL_INTERFACE_LINK)
            continue;
        if (!linkedInterfaces.insert(link.source_id).second ||
            !interfaceById.count(link.source_id) ||
            !names.count(link.sink_id) ||
            !entityByInterface.emplace(link.source_id,
                                       names.at(link.sink_id)).second)
            return 5;
    }
    if (linkedInterfaces.size() != topology.interfaces.size()) return 5;
    std::map<std::pair<unsigned, unsigned>, std::string> allowed;
    for (const auto &item : topology.interfaces) {
        if (item.intf_type != MEDIA_INTF_T_V4L_SUBDEV) continue;
        if (!allowed.emplace(
                std::make_pair(item.devnode.major, item.devnode.minor),
                entityByInterface.at(item.id)).second)
            return 5;
    }
    if (allowed.size() != 28) {
        std::fprintf(stderr, "E004LN_DENY=UNEXPECTED_SUBDEV_INTERFACE_COUNT=%zu\n",
                     allowed.size());
        return 5;
    }
    std::set<std::pair<unsigned, unsigned>> seen;
    unsigned streams = 0;
    for (unsigned i=0; i != 96; ++i) {
        const std::string node = "/dev/v4l-subdev" + std::to_string(i);
        struct stat info{};
        if (::lstat(node.c_str(), &info) != 0) {
            if (errno == ENOENT) continue;
            return 6;
        }
        if (!S_ISCHR(info.st_mode)) return 6;
        const auto dev = std::make_pair(static_cast<unsigned>(major(info.st_rdev)),
                                        static_cast<unsigned>(minor(info.st_rdev)));
        auto expected = allowed.find(dev);
        if (expected == allowed.end() || !seen.insert(dev).second) return 6;
        int fd = ::open(node.c_str(), O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK);
        if (fd < 0) return 6;
        struct v4l2_subdev_capability caps{};
        int rc = ::ioctl(fd, VIDIOC_SUBDEV_QUERYCAP, &caps);
        ::close(fd);
        if (rc < 0 || (caps.capabilities & ~
                       (V4L2_SUBDEV_CAP_STREAMS|V4L2_SUBDEV_CAP_RO_SUBDEV))) {
            std::fprintf(stderr, "E004LN_DENY=QUERYCAP_ERROR_%s\n",
                         expected->second.c_str());
            return 7;
        }
        if (caps.capabilities & V4L2_SUBDEV_CAP_STREAMS) ++streams;
        std::printf("SUBDEV=%s CAP_STREAMS=%u CAP_RO=%u\n",
                    expected->second.c_str(),
                    !!(caps.capabilities & V4L2_SUBDEV_CAP_STREAMS),
                    !!(caps.capabilities & V4L2_SUBDEV_CAP_RO_SUBDEV));
    }
    if (seen.size() != allowed.size() || streams != 0) {
        std::fprintf(stderr, "E004LN_DENY=SUBDEV_COUNTS_OR_STREAMS count=%zu streams=%u\n",
                     seen.size(), streams);
        return 8;
    }
    std::printf("E004LN_NATIVE_SUBDEV_CAPS=PASS COUNT=%zu STREAMS_CAPABLE=%u IOCTL_ONLY=QUERYCAP\n",
                seen.size(), streams);
    return 0;
}
