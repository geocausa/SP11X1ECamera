/* SPDX-License-Identifier: MIT
 * E004lt exact-boot, read-only full kernel RGB media-graph neutral check.
 * Used BETWEEN bounded independent libcamera RAW capture sessions.
 */
#include "sp11-media-topology.h"
#include <cstdio>
#include <cstring>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <string>
static int safeIoctl(int fd,unsigned long op,void *arg)
{
    if (op!=MEDIA_IOC_G_TOPOLOGY && op!=MEDIA_IOC_DEVICE_INFO)
        return -1;
    return ::ioctl(fd,op,arg);
}
int main()
{
    if (::geteuid()!=0) return 2;
    FILE *f=::fopen("/proc/cmdline","r");
    if (!f) return 2;
    char cmdline[8192]{};
    const bool got=::fgets(cmdline,sizeof(cmdline),f);
    ::fclose(f);
    if (!got || !std::strstr(cmdline,"sp11_camera_e004lt_xrgb8888=1") ||
        !std::strstr(cmdline,"sp11_entry=7.1.5-sp11-camera-e004lt-xrgb8888") ||
        !std::strstr(cmdline,"modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0"))
        return 2;
    const int fd=::open("/dev/media0",O_RDONLY|O_CLOEXEC|O_NOFOLLOW|O_NONBLOCK);
    if (fd<0) return 3;
    sp11::Graph graph;
    sp11::State enabled;
    bool valid=sp11::readFreshTopology(fd,graph,safeIoctl) &&
               sp11::validGraph(graph,enabled) && enabled.empty();
    ::close(fd);
    if (!valid) {
        std::fputs("E004LT_FULL_MEDIA_GRAPH=NOT_NEUTRAL\n",stderr);
        return 4;
    }
    std::puts("E004LT_FULL_MEDIA_GRAPH=NEUTRAL IOCTL=READ_ONLY");
    return 0;
}
