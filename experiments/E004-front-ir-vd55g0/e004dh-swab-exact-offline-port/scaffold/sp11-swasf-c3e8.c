/* SPDX-License-Identifier: MIT */
/* Scalar form of Windows QcISPTrustlet8380.dll FUN_18001c3e8 for one 8-pixel tile. */
#include "sp11-swasf-c3e8.h"
#include "sp11-swasf-c230.h"

static int clampi(int v, int lo, int hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}
static int16_t px(const int16_t *src, int stride, int width, int height, int y, int x)
{
    y=clampi(y,0,height-1); x=clampi(x,0,width-1);
    return src[y*stride+x];
}
static void sort2(int16_t *a, int16_t *b)
{
    if (*a>*b) { int16_t t=*a; *a=*b; *b=t; }
}
static int16_t median5(int16_t a,int16_t b,int16_t c,int16_t d,int16_t e)
{
    /* fixed sorting network; return lane 2 */
    sort2(&a,&b); sort2(&d,&e); sort2(&a,&c); sort2(&b,&c);
    sort2(&a,&d); sort2(&c,&d); sort2(&b,&e); sort2(&b,&c);
    return c;
}
void sp11_swasf_c3e8_tile(const int16_t *src, int stride,
                          int x0, int x1, int y0, int y1,
                          int width, int height,
                          int32_t *out_hp, uint8_t *out_lp, int16_t *out_cross5)
{
    int tile=x1-x0, y, lx;
    if (tile<=0) return;
    for (y=y0; y<y1; ++y) {
        int row=(y-y0)*tile;
        for (lx=0; lx<tile; ++lx) {
            int x=x0+lx;
            out_cross5[row+lx]=median5(px(src,stride,width,height,y,x),
                                       px(src,stride,width,height,y,x-1),
                                       px(src,stride,width,height,y,x+1),
                                       px(src,stride,width,height,y-1,x),
                                       px(src,stride,width,height,y+1,x));
        }
        for (lx=0; lx<tile; lx+=2) {
            int16_t rows[7][8], tail[2]; int32_t o4[2]; uint8_t o2[2];
            int r,c,x=x0+lx;
            for (r=0;r<7;r++) for (c=0;c<8;c++)
                rows[r][c]=px(src,stride,width,height,y+r-3,x+c-3);
            tail[0]=out_cross5[row+lx];
            tail[1]=out_cross5[row+lx+1];
            sp11_swasf_c230(rows,tail,o4,o2);
            out_hp[row+lx]=o4[0]; out_hp[row+lx+1]=o4[1];
            out_lp[row+lx]=o2[0]; out_lp[row+lx+1]=o2[1];
        }
    }
}
