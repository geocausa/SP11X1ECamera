/* SPDX-License-Identifier: GPL-2.0-only
 * Development-only front sensor timing measurement. Never reads pixel memory.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/videodev2.h>
#include <math.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <unistd.h>

#define FRAMES 120
#define SKIP 4
#define LINE_LENGTH 6752U
#define IMAGE_BYTES 10368000U
#define BUFFER_TYPE V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE
static int call(int fd, unsigned long command, void *value)
{
    int rc;
    do rc = ioctl(fd, command, value); while (rc < 0 && errno == EINTR);
    return rc;
}
static int compare(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}
static int summarize(const double *time, unsigned fll, int hardware)
{
    double sorted[FRAMES - SKIP - 1];
    double sum = 0, mean, deviation = 0, span_mean;
    unsigned count = FRAMES - SKIP - 1;
    for (unsigned i = 0; i < count; ++i) {
        double delta = time[SKIP + i + 1] - time[SKIP + i];
        if (!isfinite(delta) || delta <= 0)
            return -1;
        sorted[i] = delta;
        sum += delta;
    }
    mean = sum / count;
    span_mean = (time[FRAMES - 1] - time[SKIP]) / count;
    for (unsigned i = 0; i < count; ++i)
        deviation += (sorted[i] - mean) * (sorted[i] - mean);
    deviation = sqrt(deviation / count);
    qsort(sorted, count, sizeof(sorted[0]), compare);
    printf("{\"status\":\"%s\","
           "\"frames\":%u,\"intervals\":%u,\"line_length\":%u,"
           "\"frame_length\":%u,\"mean_period_seconds\":%.12f,"
           "\"median_period_seconds\":%.12f,\"period_stddev_seconds\":%.12f,"
           "\"p10_period_seconds\":%.12f,\"p90_period_seconds\":%.12f,"
           "\"fps\":%.9f,\"inferred_array_rate_hz\":%.3f,"
           "\"pixels_mapped_or_read\":false,\"streamoff\":%s}\n",
           hardware ? "PASS_FRONT_RAW_TIMING_MEASUREMENT" : "PASS_SYNTHETIC_TIMING_MEASUREMENT",
           FRAMES, count, LINE_LENGTH, fll, span_mean, sorted[count / 2],
           deviation, sorted[count / 10], sorted[(count * 9) / 10],
           1.0 / span_mean, (double)LINE_LENGTH * fll / span_mean, hardware ? "true" : "false");
    return 0;
}
static int boot_allowed(void)
{
    char data[8192];
    FILE *file = fopen("/proc/cmdline", "r");
    if (!file)
        return 0;
    char *got = fgets(data, sizeof(data), file);
    fclose(file);
    return got && strstr(data, "sp11_camera_native_timing_20261007=1") &&
           strstr(data, "sp11_entry=7.1.5-sp11-camera-native-timing-20261007");
}
static int capture(const char *video, const char *sensor, unsigned fll)
{
    int fd = -1, sensorfd = -1, rc = -1, streaming = 0;
    enum v4l2_buf_type type = BUFFER_TYPE;
    struct stat st;
    struct v4l2_format format = { .type = BUFFER_TYPE };
    struct v4l2_requestbuffers request = {
        .count = 4, .type = BUFFER_TYPE, .memory = V4L2_MEMORY_MMAP,
    };
    struct v4l2_ext_control values[4] = {
        { .id = V4L2_CID_VBLANK, .value = (int)fll - 2160 },
        { .id = V4L2_CID_EXPOSURE, .value = 1000 },
        { .id = V4L2_CID_ANALOGUE_GAIN, .value = 0 },
        { .id = V4L2_CID_DIGITAL_GAIN, .value = 256 },
    };
    struct v4l2_ext_controls controls = {
        .count = 4, .controls = values,
        .which = V4L2_CTRL_WHICH_CUR_VAL,
    };
    double time[FRAMES];
    if (geteuid() || !boot_allowed() || (fll != 3554 && fll != 7116))
        return -1;
    sensorfd = open(sensor, O_RDWR | O_CLOEXEC | O_NOFOLLOW);
    if (sensorfd < 0 || fstat(sensorfd, &st) || !S_ISCHR(st.st_mode) ||
        call(sensorfd, VIDIOC_S_EXT_CTRLS, &controls))
        goto out;
    for (unsigned i = 0; i < 4; ++i)
        values[i].value = -1;
    if (call(sensorfd, VIDIOC_G_EXT_CTRLS, &controls) ||
        values[0].value != (int)fll - 2160 || values[1].value != 1000 ||
        values[2].value != 0 || values[3].value != 256)
        goto out;
    close(sensorfd);
    sensorfd = -1;

    fd = open(video, O_RDWR | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
    if (fd < 0 || fstat(fd, &st) || !S_ISCHR(st.st_mode) ||
        call(fd, VIDIOC_G_FMT, &format))
        goto out;
    const struct v4l2_pix_format_mplane *p = &format.fmt.pix_mp;
    if (p->width != 3840 || p->height != 2160 ||
        p->pixelformat != v4l2_fourcc('p', 'R', 'A', 'A') ||
        p->num_planes != 1 || p->plane_fmt[0].bytesperline != 4800 ||
        p->plane_fmt[0].sizeimage != IMAGE_BYTES ||
        call(fd, VIDIOC_REQBUFS, &request) || request.count != 4)
        goto out;
    for (unsigned i = 0; i < request.count; ++i) {
        struct v4l2_plane plane = { 0 };
        struct v4l2_buffer buffer = {
            .type = BUFFER_TYPE, .memory = V4L2_MEMORY_MMAP,
            .index = i, .length = 1, .m.planes = &plane,
        };
        if (call(fd, VIDIOC_QUERYBUF, &buffer) || plane.length < IMAGE_BYTES ||
            call(fd, VIDIOC_QBUF, &buffer))
            goto out;
    }
    /* Allocation exists in the kernel. No mmap, read or output pixel copy. */
    if (call(fd, VIDIOC_STREAMON, &type))
        goto out;
    streaming = 1;
    for (unsigned i = 0; i < FRAMES; ++i) {
        struct pollfd ready = { .fd = fd, .events = POLLIN };
        struct v4l2_plane plane = { 0 };
        struct v4l2_buffer buffer = {
            .type = BUFFER_TYPE, .memory = V4L2_MEMORY_MMAP,
            .length = 1, .m.planes = &plane,
        };
        int n;
        do n = poll(&ready, 1, 4000); while (n < 0 && errno == EINTR);
        if (n != 1 || (ready.revents & (POLLERR | POLLHUP | POLLNVAL)) ||
            !(ready.revents & POLLIN) || call(fd, VIDIOC_DQBUF, &buffer) ||
            buffer.sequence != i || buffer.index >= request.count ||
            buffer.length != 1 || plane.bytesused != IMAGE_BYTES ||
            plane.data_offset || (buffer.flags & V4L2_BUF_FLAG_ERROR) ||
            (buffer.flags & V4L2_BUF_FLAG_TIMESTAMP_MASK) !=
                V4L2_BUF_FLAG_TIMESTAMP_MONOTONIC)
            goto out;
        time[i] = (double)buffer.timestamp.tv_sec +
                  (double)buffer.timestamp.tv_usec / 1000000.0;
        if (i && time[i] <= time[i - 1])
            goto out;
        if (i + 1 < FRAMES && call(fd, VIDIOC_QBUF, &buffer))
            goto out;
    }
    if (call(fd, VIDIOC_STREAMOFF, &type))
        goto out;
    streaming = 0;
    request.count = 0;
    if (call(fd, VIDIOC_REQBUFS, &request))
        goto out;
    rc = summarize(time, fll, 1);
out:
    if (rc)
        fprintf(stderr, "FRONT_TIMING_FAILED errno=%d streaming=%d fll=%u\n",
                errno, streaming, fll);
    if (streaming && call(fd, VIDIOC_STREAMOFF, &type))
        fputs("FRONT_TIMING_STOP_FAILED_REBOOT_REQUIRED\n", stderr);
    if (fd >= 0)
        close(fd);
    if (sensorfd >= 0)
        close(sensorfd);
    return rc;
}
int main(int argc, char **argv)
{
    if (argc == 2 && !strcmp(argv[1], "--self-test")) {
        double sample[FRAMES];
        for (unsigned i = 0; i < FRAMES; ++i)
            sample[i] = 10.0 + i / 30.0;
        if (summarize(sample, 3554, 0))
            return 1;
        sample[FRAMES - 1] = sample[FRAMES - 2];
        if (!summarize(sample, 3554, 0))
            return 1;
        puts("PASS_SYNTHETIC_TIMING_AND_NONMONOTONIC_REJECTION_NO_DEVICE_ACCESS");
        return 0;
    }
    if (argc != 4 || (strcmp(argv[3], "3554") && strcmp(argv[3], "7116")))
        return 2;
    return capture(argv[1], argv[2], (unsigned)strtoul(argv[3], NULL, 10)) ? 1 : 0;
}
