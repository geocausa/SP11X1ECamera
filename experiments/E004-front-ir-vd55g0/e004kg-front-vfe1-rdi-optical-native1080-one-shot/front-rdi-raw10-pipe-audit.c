/* SPDX-License-Identifier: MIT
 * E004kg: bounded raw 4K NV12 pipe forwarder with byte-exact non-image audit.
 * No camera, V4L2, kernel module, persistent pixel file, or IR APIs.
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <inttypes.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

enum { FRAME_BYTES=3840*2160*5/4, MAX_FRAMES=8, CHUNK=65536 };
static int64_t clock_ns(void) {
    struct timespec t;
    if (clock_gettime(CLOCK_MONOTONIC,&t)) return -1;
    return (int64_t)t.tv_sec*1000000000LL+t.tv_nsec;
}
static int write_exact(const unsigned char *data,size_t length,uint64_t *out) {
    while (length) {
        ssize_t done=write(STDOUT_FILENO,data,length);
        if (done<0 && errno==EINTR) continue;
        if (done<=0) return -1;
        data+=(size_t)done; length-=(size_t)done; *out+=(uint64_t)done;
    }
    return 0;
}
int main(int argc,char **argv) {
    if (argc!=5 || strcmp(argv[1],"--frames") ||
        strcmp(argv[3],"--idle-ms")) {
        fputs("E004KG_RAW_USAGE --frames 1..8 --idle-ms 100..15000\n",stderr);
        return 2;
    }
    char *end=NULL;
    errno=0;
    long frames=strtol(argv[2],&end,10);
    if (errno || !end || *end || end==argv[2] || frames<1 || frames>MAX_FRAMES) {
        fputs("E004KG_RAW_INVALID_FRAME_BOUND\n",stderr);return 2;
    }
    errno=0; end=NULL;
    long idle_ms=strtol(argv[4],&end,10);
    if (errno || !end || *end || end==argv[4] || idle_ms<100 || idle_ms>15000) {
        fputs("E004KG_RAW_INVALID_IDLE_BOUND\n",stderr);return 2;
    }
    if (isatty(STDIN_FILENO) || isatty(STDOUT_FILENO)) {
        fputs("E004KG_RAW_NO_TERMINAL_PIXEL_STREAM\n",stderr);return 2;
    }
    if (signal(SIGPIPE,SIG_IGN)==SIG_ERR) {
        fputs("E004KG_RAW_SIGPIPE_INIT_ERROR\n",stderr);return 2;
    }
    unsigned char *chunk=malloc(CHUNK);
    if (!chunk) { fputs("E004KG_RAW_ALLOCATION_ERROR\n",stderr);return 2; }
    const uint64_t limit=(uint64_t)frames*FRAME_BYTES;
    uint64_t bytes_in=0, bytes_out=0, completed=0;
    int64_t first_ns=-1,last_ns=-1;
    const char *reason="EOF";
    int rc=1;
    for (;;) {
        struct pollfd fds={.fd=STDIN_FILENO,.events=POLLIN | POLLHUP};
        int ready=poll(&fds,1,(int)idle_ms);
        if (ready<0 && errno==EINTR) continue;
        if (ready<0) { reason="POLL_ERROR";break; }
        if (ready==0) { reason="INPUT_IDLE";break; }
        ssize_t got=read(STDIN_FILENO,chunk,CHUNK);
        if (got<0 && errno==EINTR) continue;
        if (got<0) { reason="READ_ERROR";break; }
        if (got==0) { reason="EOF";break; }
        if (bytes_in+(uint64_t)got>limit) {
            reason="FRAME_BOUND_EXCEEDED";break;
        }
        bytes_in+=(uint64_t)got;
        if (write_exact(chunk,(size_t)got,&bytes_out)) {
            reason="OUTPUT_CLOSED_OR_WRITE_ERROR";break;
        }
        uint64_t current=bytes_out/FRAME_BYTES;
        if (current>completed) {
            int64_t now=clock_ns();
            if (now<0) { reason="CLOCK_ERROR";break; }
            if (first_ns<0) first_ns=now;
            last_ns=now; completed=current;
            if (completed%10==0) {
                fprintf(stderr,"E004KG_RAW_PROGRESS FULL_FRONT_RAW_FRAMES=%" PRIu64
                    " BYTES_OUT=%" PRIu64 "\n",completed,bytes_out);
                fflush(stderr);
            }
        }
    }
    const uint64_t complete_out=bytes_out/FRAME_BYTES;
    const uint64_t tail=bytes_out%FRAME_BYTES;
    double boundary_fps=0.0;
    if (complete_out>1 && last_ns>first_ns)
        boundary_fps=(double)(complete_out-1)*1e9/(double)(last_ns-first_ns);
    const int full=(bytes_in==limit && bytes_out==limit && tail==0 &&
                    strcmp(reason,"EOF")==0);
    fprintf(stderr,"E004KG_RAW_FRONT_RAW_PIPE=%s REQUESTED_FRAMES=%ld FULL_FRAMES=%" PRIu64
        " BYTES_IN=%" PRIu64 " BYTES_OUT=%" PRIu64
        " INCOMPLETE_TAIL_BYTES=%" PRIu64 " TERMINATION=%s"
        " PIPE_FULL_FRAME_BOUNDARY_FPS=%.4f SYNTHETIC_PTS_USED=NO"
        " REAL_FRONT_CAMERA_PROVEN_BY_THIS_TOOL=NO PIXELS_SAVED=NO\n",
        full?"PASS":"PARTIAL",frames,complete_out,
        bytes_in,bytes_out,tail,reason,boundary_fps);
    if (full) rc=0;
    free(chunk);
    return rc;
}
