#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "sp11-parity-worker.h"

#define W 644u
#define H 604u

static int read_exact(const char *path, uint8_t *p, size_t n)
{
    FILE *f=fopen(path,"rb"); size_t got;
    if (!f) return -1;
    got=fread(p,1,n,f); fclose(f);
    return got==n ? 0 : -1;
}

int main(int argc, char **argv)
{
    const size_t y=(size_t)W*H, frame=y+y/2;
    const size_t raw_off=(y+1u)&~(size_t)1u;
    const size_t work_need=raw_off+4u*y;
    uint8_t *src, *win, *dst, *work;
    struct sp11_worker_request r={0};
    size_t i, luma_diff=0, tail_diff=0;
    int ret;
    FILE *f;

    if (argc < 3 || argc > 4) return 2;
    src=malloc(frame); win=malloc(frame); dst=malloc(frame); work=malloc(work_need);
    if (!src || !win || !dst || !work) return 3;
    if (read_exact(argv[1],src,frame) || read_exact(argv[2],win,frame)) return 4;
    memset(dst,0xa5,frame);

    r.dst_base=dst; r.dst_extent=frame; r.src=src; r.src_extent=frame;
    r.width=W; r.height=H; r.request_id=10;
    r.captured_extent=frame; r.serialized_extent=frame;
    r.work_base=work; r.work_extent=work_need;
    ret=sp11_parity_worker_run(&r);
    if (ret) { fprintf(stderr,"worker ret=%d\n",ret); return 5; }

    for (i=0;i<y;i++) if (dst[i]!=win[i]) luma_diff++;
    /* E004dg worker contract explicitly neutralizes the NV12 tail after SWASF. */
    for (i=y;i<frame;i++) if (dst[i]!=0x80) tail_diff++;
    printf("WORKER_FULL_LUMA_DIFF=%zu\n",luma_diff);
    printf("WORKER_NEUTRAL_TAIL_DIFF=%zu\n",tail_diff);

    if (argc==4) {
        f=fopen(argv[3],"wb"); if(!f) return 6;
        if(fwrite(dst,1,frame,f)!=frame){fclose(f);return 7;} fclose(f);
    }
    return (luma_diff||tail_diff)?1:0;
}
