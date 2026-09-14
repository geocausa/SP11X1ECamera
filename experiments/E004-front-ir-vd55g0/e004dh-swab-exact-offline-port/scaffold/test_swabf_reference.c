#include <stdio.h>
#include <string.h>
#include "sp11-swabf-reference.h"
static int fail;
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x); fail++; } } while (0)
static void vector(const uint8_t *in,const uint8_t *want,unsigned w,unsigned h)
{
    uint8_t out[64]; size_t n=(size_t)w*h;
    memset(out,0xcc,sizeof(out));
    CHECK(sp11_swabf_reference(out,sizeof(out),in,n,w,h,&sp11_swabf_windows_oracle_tuning)==0);
    CHECK(memcmp(out,want,n)==0);
}
int main(void)
{
    static const uint8_t a[16]={0,16,32,48,64,80,96,112,128,144,160,176,192,208,224,240};
    static const uint8_t aw[16]={3,17,33,48,65,80,96,110,129,144,160,174,191,206,222,236};
    static const uint8_t b[9]={0,0,0,0,100,0,0,0,0};
    static const uint8_t bw[9]={0,0,0,0,94,0,0,0,0};
    static const uint8_t c[4]={10,20,30,40};
    static const uint8_t cw[4]={14,23,26,35};
    static const uint8_t d[9]={250,1,2,3,4,5,6,7,8};
    static const uint8_t dw[9]={250,4,4,4,4,4,4,4,4};
    vector(a,aw,4,4); vector(b,bw,3,3); vector(c,cw,2,2); vector(d,dw,3,3);
    CHECK(sp11_swabf_reference(NULL,1,a,sizeof(a),4,4,&sp11_swabf_windows_oracle_tuning)==-1);
    if (fail) return 1;
    puts("E004dh SWABF scalar vectors: PASS");
    return 0;
}
