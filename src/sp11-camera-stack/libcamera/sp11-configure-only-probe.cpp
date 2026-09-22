/* SPDX-License-Identifier: MIT
 * E004lq: one-shot libcamera RGB CONFIGURE ONLY, no capture or STREAMON.
 * Requires dedicated nondefault boot and an independently root-sealed bundle.
 */
#include <libcamera/camera.h>
#include <libcamera/camera_manager.h>
#include <libcamera/control_ids.h>
#include <libcamera/property_ids.h>
#include <libcamera/stream.h>
#include "sp11-media-topology.h"
#include <fcntl.h>
#include <sys/ioctl.h>
#include <cstdio>
#include <cstring>
#include <memory>
#include <string>
#include <unistd.h>

static bool authorized()
{
    FILE *f = ::fopen("/proc/cmdline","r");
    if (!f) return false;
    char text[8192]{};
    const bool found = ::fgets(text,sizeof(text),f);
    ::fclose(f);
    return ::geteuid() == 0 && found &&
           std::strstr(text,"sp11_camera_e004lq_rgb_configure=1") &&
           std::strstr(text,"sp11_entry=7.1.5-sp11-camera-e004lq-configure") &&
           std::strstr(text,"modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0");
}
static int readOnlyMediaIoctl(int fd,unsigned long command,void *arg)
{
    if (command != MEDIA_IOC_DEVICE_INFO &&
        command != MEDIA_IOC_G_TOPOLOGY) return -1;
    return ::ioctl(fd,command,arg);
}
static bool kernelGraphNeutral()
{
    const int fd=::open("/dev/media0",O_RDONLY|O_NOFOLLOW|O_CLOEXEC|O_NONBLOCK);
    if (fd<0) return false;
    sp11::Graph graph;
    sp11::State active;
    const bool ok=sp11::readFreshTopology(fd,graph,readOnlyMediaIoctl) &&
                  sp11::validGraph(graph,active) && active.empty();
    ::close(fd);
    return ok;
}
int main()
{
    if (!authorized()) {
        std::fputs("E004LQ_DENY=UNAUTHORIZED_BOOT\n",stderr);
        return 2;
    }
    libcamera::CameraManager manager;
    if (manager.start() < 0) {
        std::fputs("E004LQ_FAIL=CAMERA_MANAGER_START\n",stderr);
        return 3;
    }
    unsigned front=0,rear=0;
    for (auto camera : manager.cameras()) {
        auto model=camera->properties().get(libcamera::properties::Model);
        if (!model) continue;
        const std::string name(*model);
        if (name != "imx681" && name != "ov13858") continue;
        if ((name=="imx681" && ++front != 1) ||
            (name=="ov13858" && ++rear != 1)) {
            std::fputs("E004LQ_FAIL=DUPLICATE_CAMERA\n",stderr);
            return 4;
        }
        if (camera->acquire()) {
            std::fprintf(stderr,"E004LQ_FAIL=ACQUIRE_%s\n",name.c_str());
            return 5;
        }
        auto config=camera->generateConfiguration({libcamera::StreamRole::Raw});
        if (!config || config->size()!=1 ||
            config->validate()==libcamera::CameraConfiguration::Invalid) {
            std::fprintf(stderr,"E004LQ_FAIL=RAW_CONFIG_GENERATION_%s\n",name.c_str());
            return 6;
        }
        const auto &entry=config->at(0);
        std::printf("E004LQ_RAW_PROPOSED camera=%s size=%s pixel=%s\n",
                    name.c_str(),entry.size.toString().c_str(),
                    entry.pixelFormat.toString().c_str());
        std::fflush(stdout);
        if (camera->configure(config.get())) {
            std::fprintf(stderr,"E004LQ_FAIL=CONFIGURE_%s\n",name.c_str());
            return 7;
        }
        std::printf("E004LQ_CONFIGURE=PASS CAMERA=%s SIZE=%s FORMAT=%s STREAMON=NO\n",
                    name.c_str(),config->at(0).size.toString().c_str(),
                    config->at(0).pixelFormat.toString().c_str());
        std::fflush(stdout);
        if (!kernelGraphNeutral()) {
            std::fprintf(stderr,"E004LQ_FAIL=NOT_NEUTRAL_AFTER_CONFIGURE_%s\n",name.c_str());
            return 10;
        }
        std::printf("E004LQ_GRAPH_AFTER_CONFIGURE=NEUTRAL CAMERA=%s\n",name.c_str());
        std::fflush(stdout);
        if (camera->release()) {
            std::fprintf(stderr,"E004LQ_FAIL=RELEASE_%s\n",name.c_str());
            return 8;
        }
    }
    if (front!=1 || rear!=1) {
        std::fprintf(stderr,"E004LQ_FAIL=MISSING_REAL_RGB front=%u rear=%u\n",front,rear);
        return 9;
    }
    if (!kernelGraphNeutral()) {
        std::fputs("E004LQ_FAIL=NOT_NEUTRAL_AFTER_BOTH_RELEASES\n",stderr);
        return 11;
    }
    manager.stop();
    std::puts("E004LQ_BOTH_REAL_RGB_CONFIGURED=PASS STREAMON=NO IR_EMITTER=NO GRAPH=NEUTRAL");
    return 0;
}
