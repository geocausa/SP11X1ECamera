/* SPDX-License-Identifier: MIT
 * Run ONLY on camera-free protected Golden. Deny any unmarked runtime.
 */
#include "../sp11-libcamera-experimental-lease.h"
#include <cassert>
#include <cstdio>
#include <cstring>
#include <unistd.h>

int main()
{
    FILE *f = std::fopen("/proc/cmdline", "r");
    assert(f);
    char cmdline[8192]{};
    assert(std::fgets(cmdline, sizeof(cmdline), f));
    std::fclose(f);
    assert(!std::strstr(cmdline, "sp11_camera_e004lm_libcamera=1"));
    sp11::ExperimentalLibcameraLease lease;
    assert(!lease.initialize("/dev/media0"));
    assert(!lease.ready());
    assert(!lease.setupLinks("imx681 1-0010"));
    assert(!lease.beforeStream("imx681 1-0010"));
    assert(!lease.neutralizeWhenIdle());
    std::puts("PASS: ordinary Golden Linux rejects libcamera CAMSS guard before any camera open/link write");
    return 0;
}
