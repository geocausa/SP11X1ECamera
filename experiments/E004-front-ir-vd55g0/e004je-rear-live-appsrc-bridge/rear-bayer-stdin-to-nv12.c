/* SPDX-License-Identifier: MIT
 * E004je bounded stdin->stdout Bayer10 to NV12 adapter.
 * Intentionally reuses E004iu's exact, already independently tested
 * Bayer GRBG10 unpacker and pixel-to-colour proxy in the SAME translation
 * unit. This file never opens V4L2 devices, touches boot files or IR.
 */
#define main e004iu_original_offline_main
#include "../e004iu-rear-fast-nv12-offline/rear_fast.c"
#undef main

int main(int argc, char **argv) {
    if (argc != 3 || strcmp(argv[1], "--frames")) {
        fputs("E004JE_USAGE: rear-bayer-stdin-to-nv12 --frames 1..27\n",stderr);
        return 2;
    }
    errno=0;
    char *end=NULL;
    long requested=strtol(argv[2],&end,10);
    if (errno || end==argv[2] || *end || requested<1 || requested>27) {
        fputs("E004JE_INVALID_FRAME_BOUND\n",stderr);return 2;
    }
    if (isatty(STDIN_FILENO) || isatty(STDOUT_FILENO)) {
        fputs("E004JE_REFUSE_TERMINAL_RAW_OPTICAL_IO\n",stderr);return 2;
    }
    input=malloc(IN_SIZE);
    output=malloc(OUT_SIZE);
    if (!input || !output || plan()) {
        fputs("E004JE_PLAN_OR_ALLOCATION_FAILURE\n",stderr);
        free(input);free(output);return 1;
    }
    int rc=1;
    double convert_ms=0.0;
    for (long i=0;i<requested;i++) {
        if (read_exact(STDIN_FILENO,input,IN_SIZE)) {
            fputs("E004JE_TRUNCATED_INPUT\n",stderr);goto done;
        }
        const double started=monotonic_ms();
        convert_frame();
        convert_ms+=monotonic_ms()-started;
        if (write_entire(STDOUT_FILENO,output,OUT_SIZE)) {
            fputs("E004JE_SHORT_OUTPUT\n",stderr);goto done;
        }
    }
    /* The parent v4l2-ctl is required to stop after the exact
     * requested number of frames. Reject a longer or partial stream.
     * The shell caller uses pipefail: no successful "camera" status
     * if either producer or receiver stops early. */
    unsigned char unexpected=0;
    ssize_t extra;
    do { extra=read(STDIN_FILENO,&unexpected,1); } while (extra<0 && errno==EINTR);
    if (extra != 0) {
        fputs("E004JE_EXTRA_INPUT_OR_IO_FAILURE\n",stderr);goto done;
    }
    fprintf(stderr,"E004JE_BAYER10_STREAM_NV12=PASS FRAMES=%ld "
                   "SOURCE=pgAA_4076x2806 OUTPUT=NV12_1920x1080 "
                   "AVERAGE_CONVERSION_MS=%.4f CALIBRATED=NO "
                   "LIVE_CAMERA_PROVEN=NO\n",requested,convert_ms/requested);
    rc=0;
done:
    free(input);free(output);input=NULL;output=NULL;
    return rc;
}
