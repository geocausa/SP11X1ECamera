#include <stdio.h>
#include <string.h>
#include "sp11-swasf-helpers.h"
static int fail;
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x); ++fail; } } while (0)
static void run_case(const int16_t rows[5][8], int16_t center, int16_t scale,
                     const int16_t want_pos[4], const int16_t want_neg[4], uint8_t want_c078)
{
    int16_t p[4], n[4];
    sp11_swasf_local_extrema_5x5(rows,p,n);
    CHECK(memcmp(p,want_pos,sizeof(p))==0);
    CHECK(memcmp(n,want_neg,sizeof(n))==0);
    CHECK(sp11_swasf_c078_activity(rows,center,scale)==want_c078);
}
int main(void)
{
    static const int16_t a[5][8]={{0,4,8,12,16,20,24,28},{2,6,10,14,18,22,26,30},{1,5,9,13,17,21,25,29},{3,7,11,15,19,23,27,31},{4,8,12,16,20,24,28,32}};
    static const int16_t ap[4]={7,7,7,7}, an[4]={5,5,5,5};
    static const int16_t b[5][8]={{400,300,200,100,0,100,200,300},{350,280,210,140,70,0,70,140},{320,240,160,80,0,80,160,240},{300,230,160,90,20,90,160,230},{280,220,160,100,40,100,160,220}};
    static const int16_t bp[4]={143,131,126,131}, bn[4]={96,48,0,48};
    static const int16_t c[5][8]={{1020,900,700,500,300,100,0,50},{900,800,650,500,350,200,100,0},{800,700,600,500,400,300,200,100},{700,650,600,550,500,450,400,350},{600,590,580,570,560,550,540,530}};
    static const int16_t cp[4]={251,239,179,161}, cn[4]={179,239,239,179};
    static const int16_t d[5][8]={{0,1023,0,1023,0,1023,0,1023},{1023,0,1023,0,1023,0,1023,0},{0,0,1023,1023,0,0,1023,1023},{1023,1023,0,0,1023,1023,0,0},{100,200,300,400,500,600,700,800}};
    static const int16_t dp[4]={0,0,611,611}, dn[4]={611,611,0,0};
    run_case(a,13,24,ap,an,0x0d);
    run_case(b,160,17,bp,bn,0x3d);
    run_case(c,500,31,cp,cn,0xff);
    run_case(d,512,8,dp,dn,0x41);
    {
        static const uint8_t k[5][5]={{1,4,6,4,1},{4,16,24,16,4},{6,24,36,24,6},{4,16,24,16,4},{1,4,6,4,1}};
        int16_t x[5][8]; int r,c0;
        for(r=0;r<5;r++)for(c0=0;c0<8;c0++)x[r][c0]=100;
        CHECK(sp11_swasf_c078_activity(x,100,253)==0);
        for(r=0;r<5;r++)for(c0=0;c0<5;c0++){
            x[r][c0]=164; CHECK(sp11_swasf_c078_activity(x,100,253)==k[r][c0]); x[r][c0]=100;
            x[r][c0]=36; CHECK(sp11_swasf_c078_activity(x,100,253)==k[r][c0]); x[r][c0]=100;
        }
        for(r=0;r<5;r++)for(c0=5;c0<8;c0++){
            x[r][c0]=164; CHECK(sp11_swasf_c078_activity(x,100,253)==0); x[r][c0]=100;
        }
    }
    if(fail)return 1;
    puts("E004dh SWASF helper vectors: PASS");
    return 0;
}
