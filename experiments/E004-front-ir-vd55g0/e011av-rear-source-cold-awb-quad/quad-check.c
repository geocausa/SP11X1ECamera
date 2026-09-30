/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "cold-quad-source.h"
#define CHECK(x) do { if (!(x)) abort(); } while (0)
int main(void)
{
    uint8_t wire[93] = {0};
    uint32_t out = 0xa5a5a5a5U;
    CHECK(e011av_decode_cold_quad(NULL,93,1,0,&out)==-EINVAL);
    CHECK(out==0xa5a5a5a5U);
    CHECK(e011av_decode_cold_quad(wire,93,1,0,NULL)==-EINVAL);
    for (size_t n=0;n<100;n++) if(n!=93) {
        CHECK(e011av_decode_cold_quad(wire,n,1,0,&out)==-EINVAL);
        CHECK(out==0xa5a5a5a5U);
    }
    CHECK(e011av_decode_cold_quad(wire,93,0,0,&out)==-EINVAL);
    CHECK(e011av_decode_cold_quad(wire,93,1,1,&out)==-EINVAL);
    CHECK(out==0xa5a5a5a5U);
    while (fread(wire,1,93,stdin)==93) {
        int ret=e011av_decode_cold_quad(wire,93,1,0,&out);
        if(ret) CHECK(out==0xa5a5a5a5U);
        int32_t record[2]={ret,(int32_t)out};
        CHECK(fwrite(record,sizeof(record),1,stdout)==1);
        out=0xa5a5a5a5U;
    }
    CHECK(feof(stdin));
    return 0;
}
