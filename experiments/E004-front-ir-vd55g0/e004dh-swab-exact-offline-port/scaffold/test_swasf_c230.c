#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "sp11-swasf-c230.h"

static int fail;
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x); ++fail; } } while (0)

static void flat(int16_t a[7][8], int16_t v)
{
    int r,c; for(r=0;r<7;r++) for(c=0;c<8;c++) a[r][c]=v;
}

static void one(int r, int c, int16_t delta, int32_t e0, int32_t e1, uint8_t b0, uint8_t b1)
{
    int16_t a[7][8], t[2]={0,0}; int32_t o4[2]; uint8_t o2[2];
    flat(a,0); a[r][c]=delta; sp11_swasf_c230(a,t,o4,o2);
    CHECK(o4[0]==e0); CHECK(o4[1]==e1); CHECK(o2[0]==b0); CHECK(o2[1]==b1);
}

int main(void)
{
    int16_t a[7][8], t[2]; int32_t o4[2]; uint8_t o2[2];
    flat(a,512); t[0]=t[1]=512; sp11_swasf_c230(a,t,o4,o2);
    CHECK(o4[0]==0 && o4[1]==0); CHECK(o2[0]==128 && o2[1]==128);
    one(0,0,4096,-112,0,0,0);
    one(1,1,4096,-1168,-368,9,0);
    one(2,3,4096,3872,1424,82,60);
    one(3,3,4096,0,3872,0,82);
    one(4,4,4096,1424,3872,60,82);
    one(6,7,4096,0,-112,0,0);
    one(2,3,-4096,-3872,-1424,174,196);
    flat(a,0); t[0]=4096; t[1]=0; sp11_swasf_c230(a,t,o4,o2);
    CHECK(o4[0]==8128 && o4[1]==0); CHECK(o2[0]==112 && o2[1]==0);
    flat(a,0); t[0]=0; t[1]=-4096; sp11_swasf_c230(a,t,o4,o2);
    CHECK(o4[0]==0 && o4[1]==-8128); CHECK(o2[0]==0 && o2[1]==144);
    if(fail) return 1;
    puts("E004dh C230 scalar vectors: PASS");
    return 0;
}
