#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "sp11-swasf-reference.h"
#define W 644u
#define H 604u
int main(int argc,char **argv)
{
    const size_t n=(size_t)W*H;
    FILE *f; uint8_t *src,*dst,*win; int16_t *raw,*sm; size_t i,d=0; int ret;
    if(argc!=3)return 2;
    src=malloc(n); dst=malloc(n); win=malloc(n); raw=malloc(n*sizeof(*raw)); sm=malloc(n*sizeof(*sm));
    if(!src||!dst||!win||!raw||!sm)return 3;
    f=fopen(argv[1],"rb"); if(!f||fread(src,1,n,f)!=n)return 4; fclose(f);
    f=fopen(argv[2],"rb"); if(!f||fread(win,1,n,f)!=n)return 5; fclose(f);
    ret=sp11_swasf_reference(dst,n,src,n,W,H,raw,n,sm,n,
                             sp11_swasf_windows_oracle_tuning,
                             SP11_SWASF_WINDOWS_ACTIVITY_SCALE);
    if(ret)return 6;
    for(i=0;i<n;i++)if(dst[i]!=win[i])d++;
    printf("SWASF_FULL_LUMA_DIFF=%zu\n",d);
    return d?1:0;
}
