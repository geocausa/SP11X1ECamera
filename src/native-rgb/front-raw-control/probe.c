/* SPDX-License-Identifier: GPL-2.0-only
 * Development-only RAW control metrology. No image conversion or pixel export.
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
#include <stdint.h>
#include <sys/mman.h>
#include <time.h>
#include "../../../experiments/E004-front-ir-vd55g0/e004mg-private-optical-rgb-visual-one-shot/iq/raw10_unpack.h"

#define FRAMES 320
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
           "\"sparse_pixel_metrology\":true,\"pixel_export\":false,\"streamoff\":%s}\n",
           hardware ? "PASS_FRONT_RAW_CONTROL_CAPTURE" : "PASS_SYNTHETIC_TIMING_MEASUREMENT",
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
    if (!got)
        return 0;
    int token = 0, entry = 0;
    for (char *v = strtok(data, " \n"); v; v = strtok(NULL, " \n")) {
        token |= !strcmp(v, "sp11_camera_native_raw_control_20261007_01=1");
        entry |= !strcmp(v, "sp11_entry=7.1.5-sp11-camera-native-raw-control-20261007-01");
    }
    return token && entry;
}
static int front_metadata(int fd)
{
    const unsigned ids[] = { V4L2_CID_HBLANK, V4L2_CID_PIXEL_RATE, V4L2_CID_LINK_FREQ };
    const unsigned types[] = { V4L2_CTRL_TYPE_INTEGER, V4L2_CTRL_TYPE_INTEGER64,
                               V4L2_CTRL_TYPE_INTEGER_MENU };
    const long long expected[] = { 2912, 720000000, 0 };
    for (unsigned i = 0; i < 3; ++i) {
        struct v4l2_query_ext_ctrl query = { .id = ids[i] };
        struct v4l2_ext_control value = { .id = ids[i] };
        struct v4l2_ext_controls control = { .count = 1, .controls = &value };
        if (call(fd, VIDIOC_QUERY_EXT_CTRL, &query) || query.type != types[i] ||
            !(query.flags & V4L2_CTRL_FLAG_READ_ONLY) ||
            (query.flags & V4L2_CTRL_FLAG_DISABLED) ||
            query.minimum != expected[i] || query.maximum != expected[i] ||
            call(fd, VIDIOC_G_EXT_CTRLS, &control) ||
            (i == 1 ? value.value64 : value.value) != expected[i])
            return -1;
    }
    struct v4l2_querymenu menu = { .id = V4L2_CID_LINK_FREQ, .index = 0 };
    if (call(fd, VIDIOC_QUERYMENU, &menu) || menu.value != 1200000000LL)
        return -1;
    return 0;
}
static unsigned long long monotonic_ns(void)
{
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC, &t))
        return 0;
    return (unsigned long long)t.tv_sec * 1000000000ULL + t.tv_nsec;
}
static int set_step(int fd, unsigned step, unsigned sequence)
{
    struct v4l2_ext_control v[4] = {
        { .id = V4L2_CID_VBLANK, .value = 1394 },
        { .id = V4L2_CID_EXPOSURE, .value = 1000 },
        { .id = V4L2_CID_ANALOGUE_GAIN, .value = 0 },
        { .id = V4L2_CID_DIGITAL_GAIN, .value = 256 },
    };
    if (step % 2) {
        if (step <= 6) v[1].value = 2000;
        else if (step <= 12) v[2].value = 512;
        else v[3].value = 512;
    }
    int expected[4];
    for (unsigned i = 0; i < 4; ++i) expected[i] = v[i].value;
    struct v4l2_ext_controls c = {
        .which = V4L2_CTRL_WHICH_CUR_VAL, .count = 4, .controls = v,
    };
    unsigned long long before = monotonic_ns();
    if (!before || call(fd, VIDIOC_S_EXT_CTRLS, &c))
        return -1;
    unsigned long long after = monotonic_ns();
    if (!after || after < before || call(fd, VIDIOC_G_EXT_CTRLS, &c))
        return -1;
    for (unsigned i = 0; i < 4; ++i)
        if (v[i].value != expected[i])
            return -1;
    printf("{\"kind\":\"command\",\"step\":%u,\"after_completion_sequence\":%u,"
           "\"start_ns\":%llu,\"end_ns\":%llu,\"fll\":3554,\"exposure\":%d,"
           "\"again\":%d,\"dgain\":%d,\"cached_controls_match\":true}\n",
           step, sequence, before, after, v[1].value, v[2].value, v[3].value);
    return 0;
}
static unsigned percentile(const unsigned *hist, unsigned count, unsigned p)
{
    unsigned total = 0, target = (count * p + 99) / 100;
    for (unsigned i = 0; i < 1024; ++i) {
        total += hist[i];
        if (total >= target)
            return i;
    }
    return 1023;
}
/* Fixed 16-pixel grid: all four Bayer phases in each sampled 2x2 block.
 * Aggregate source code values only; no demosaic, black subtraction, or images.
 * No interpretation as calibrated light level. */
static int profile(const uint8_t *image, size_t bytes, unsigned sequence,
                   unsigned long long timestamp, unsigned long long dequeue)
{
    unsigned hist[4][1024] = {{0}}, count[4] = {0};
    uint64_t sum[4] = {0}, squares[4] = {0};
    if (!image || bytes != IMAGE_BYTES)
        return -1;
    for (unsigned y = 16; y < 2144; y += 16)
        for (unsigned x = 16; x < 3824; x += 16)
            for (unsigned ch = 0; ch < 4; ++ch) {
                uint16_t value;
                const uint8_t *row = image + (y + ch / 2) * 4800U;
                if (sp11_raw10_pixel(row, 4800, 3840, x + ch % 2, &value))
                    return -1;
                hist[ch][value]++;
                count[ch]++;
                sum[ch] += value;
                squares[ch] += (uint64_t)value * value;
            }
    printf("{\"kind\":\"frame\",\"sequence\":%u,\"completion_timestamp_ns\":%llu,"
           "\"dequeue_monotonic_ns\":%llu,\"channels\":[", sequence, timestamp, dequeue);
    for (unsigned ch = 0; ch < 4; ++ch) {
        double mean = (double)sum[ch] / count[ch];
        printf("%s{\"phase\":%u,\"samples\":%u,\"mean\":%.9f,\"variance\":%.9f,"
               "\"p01\":%u,\"p50\":%u,\"p95\":%u,\"p99\":%u,"
               "\"zero_fraction\":%.9f,\"storage_saturation_fraction\":%.9f}",
               ch ? "," : "", ch, count[ch], mean,
               (double)squares[ch]/count[ch] - mean * mean,
               percentile(hist[ch], count[ch], 1), percentile(hist[ch], count[ch], 50),
               percentile(hist[ch], count[ch], 95), percentile(hist[ch], count[ch], 99),
               (double)hist[ch][0]/count[ch], (double)hist[ch][1023]/count[ch]);
    }
    puts("]}");
    return 0;
}
static int capture(const char *video, const char *sensor, unsigned fll)
{
    int fd = -1, sensorfd = -1, rc = -1, streaming = 0;
    void *maps[4] = {0};
    size_t lengths[4] = {0};
    enum v4l2_buf_type type = BUFFER_TYPE;
    struct stat st;
    struct v4l2_format format = { .type = BUFFER_TYPE };
    struct v4l2_requestbuffers request = {
        .count = 4, .type = BUFFER_TYPE, .memory = V4L2_MEMORY_MMAP,
    };
    double time[FRAMES];
    if (geteuid() || !boot_allowed() || fll != 3554)
        return -1;
    sensorfd = open(sensor, O_RDWR | O_CLOEXEC | O_NOFOLLOW);
    if (sensorfd < 0 || fstat(sensorfd, &st) || !S_ISCHR(st.st_mode) ||
        front_metadata(sensorfd) || set_step(sensorfd, 0, 0))
        goto out;
    fd = open(video, O_RDWR | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK);
    if (fd < 0 || fstat(fd, &st) || !S_ISCHR(st.st_mode) ||
        call(fd, VIDIOC_G_FMT, &format))
        goto out;
    const struct v4l2_pix_format_mplane *p = &format.fmt.pix_mp;
    if (p->width != 3840U || p->height != 2160U ||
        p->pixelformat != v4l2_fourcc('p', 'R', 'A', 'A') ||
        p->num_planes != 1 || p->plane_fmt[0].bytesperline != 4800U ||
        p->plane_fmt[0].sizeimage != IMAGE_BYTES ||
        call(fd, VIDIOC_REQBUFS, &request) || request.count != 4)
        goto out;
    for (unsigned i = 0; i < request.count; ++i) {
        struct v4l2_plane plane = { 0 };
        struct v4l2_buffer buffer = {
            .type = BUFFER_TYPE, .memory = V4L2_MEMORY_MMAP,
            .index = i, .length = 1, .m.planes = &plane,
        };
        if (call(fd, VIDIOC_QUERYBUF, &buffer) || plane.length < IMAGE_BYTES)
            goto out;
        lengths[i] = plane.length;
        maps[i] = mmap(NULL, plane.length, PROT_READ, MAP_SHARED, fd, plane.m.mem_offset);
        if (maps[i] == MAP_FAILED) {
            maps[i] = NULL;
            goto out;
        }
        if (call(fd, VIDIOC_QBUF, &buffer))
            goto out;
    }
    /* The diagnostic samples read-only RAW memory. Nothing is converted/exported. */
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
        unsigned long long completion = (unsigned long long)buffer.timestamp.tv_sec *
            1000000000ULL + (unsigned long long)buffer.timestamp.tv_usec * 1000ULL;
        if (profile(maps[buffer.index], plane.bytesused, i, completion, monotonic_ns()))
            goto out;
        if (i + 1 < FRAMES && call(fd, VIDIOC_QBUF, &buffer))
            goto out;
        if ((i + 1) % 16 == 0 && i + 1 <= 288 &&
            set_step(sensorfd, (i + 1) / 16, i))
            goto out;
    }
    if (set_step(sensorfd, 0, FRAMES - 1))
        goto out;
    if (call(fd, VIDIOC_STREAMOFF, &type))
        goto out;
    streaming = 0;
    for (unsigned i = 0; i < 4; ++i)
        if (maps[i]) {
            if (munmap(maps[i], lengths[i]))
                goto out;
            maps[i] = NULL;
        }
    request.count = 0;
    if (call(fd, VIDIOC_REQBUFS, &request))
        goto out;
    rc = summarize(time, fll, 1);
out:
    if (rc)
        fprintf(stderr, "FRONT_TIMING_FAILED errno=%d streaming=%d fll=%u\n",
                errno, streaming, fll);
    if (streaming && sensorfd >= 0 && set_step(sensorfd, 0, FRAMES - 1))
        fputs("RAW_CONTROL_RESTORE_FAILED_REBOOT_REQUIRED\n", stderr);
    if (streaming && call(fd, VIDIOC_STREAMOFF, &type))
        fputs("FRONT_TIMING_STOP_FAILED_REBOOT_REQUIRED\n", stderr);
    for (unsigned i = 0; i < 4; ++i)
        if (maps[i]) munmap(maps[i], lengths[i]);
    if (fd >= 0)
        close(fd);
    if (sensorfd >= 0)
        close(sensorfd);
    return rc;
}
int main(int argc, char **argv)
{
    if (argc == 2 && !strcmp(argv[1], "--self-test-profile")) {
        uint8_t *image = malloc(IMAGE_BYTES);
        if (!image)
            return 1;
        const uint8_t group[] = {0x10,0x20,0x30,0x40,0xe4};
        for (unsigned i = 0; i < IMAGE_BYTES; i += 5)
            memcpy(image + i, group, 5);
        int rc = profile(image, IMAGE_BYTES, 0, 1, 2);
        if (!profile(image, IMAGE_BYTES - 1, 0, 1, 2))
            rc = -1;
        free(image);
        return rc ? 1 : 0;
    }
    if (argc == 2 && !strcmp(argv[1], "--self-test")) {
        const uint8_t packed[] = {0x00,0x55,0xaa,0xff,0xe4};
        const uint16_t expected[] = {0,341,682,1023};
        uint16_t decoded;
        for (unsigned i = 0; i < 4; ++i)
            if (sp11_raw10_pixel(packed, 5, 4, i, &decoded) || decoded != expected[i])
                return 1;
        if (!sp11_raw10_pixel(packed, 4, 4, 0, &decoded) ||
            !sp11_raw10_pixel(packed, 5, 3, 0, &decoded) ||
            !sp11_raw10_pixel(packed, 5, 4, 4, &decoded))
            return 1;
        double sample[FRAMES];
        for (unsigned i = 0; i < FRAMES; ++i)
            sample[i] = 10.0 + i / 30.0;
        if (summarize(sample, 3554, 0))
            return 1;
        sample[FRAMES - 1] = sample[FRAMES - 2];
        if (!summarize(sample, 3554, 0))
            return 1;
        puts("PASS_RAW10_UNPACK_BOUNDS_TIMING_NONMONOTONIC_NO_DEVICE_ACCESS");
        return 0;
    }
    if (argc != 3)
        return 2;
    return capture(argv[1], argv[2], 3554) ? 1 : 0;
}
