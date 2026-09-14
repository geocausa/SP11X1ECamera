#include <stdint.h>
#include <stdio.h>
#include "sp11-swasf-c3e8.h"
int main(void)
{
    enum { W=16,H=16 }; int16_t src[W*H], med[H*8]; int32_t hp[H*8]; uint8_t lp[H*8]; int i;
    for(i=0;i<W*H;i++)src[i]=512;
    sp11_swasf_c3e8_tile(src,W,0,8,0,H,W,H,hp,lp,med);
    for(i=0;i<H*8;i++) if(med[i]!=512||hp[i]!=0||lp[i]!=128) { fprintf(stderr,"FAIL %d %d %d %u\n",i,med[i],hp[i],lp[i]); return 1; }
    puts("E004dh C3E8 scalar constant: PASS"); return 0;
}
