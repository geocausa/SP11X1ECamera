// SPDX-License-Identifier: GPL-2.0-only
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define AEC_BYTES 0x14000u
#define AWB_BYTES 0x3c000u
#define AWB_STRIDE 0x50u
#define AWB_REGIONS 3072u
#define MASK34 ((1ULL << 34) - 1ULL)

struct e003i_trigger_result {
    float measured_luma;
    float lux;
    float agw_x;
    float agw_y;
    float fresh_cct;
    float sum_weight;
    uint32_t p01;
    uint32_t valid;
};

static uint16_t rd16(const uint8_t *p) { return (uint16_t)p[0] | ((uint16_t)p[1] << 8); }
static uint32_t rd32(const uint8_t *p) { return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24); }
static uint64_t rd64(const uint8_t *p) { return (uint64_t)rd32(p) | ((uint64_t)rd32(p + 4) << 32); }
static float rfloat(const uint8_t *p) { float v; memcpy(&v, p, 4); return v; }
static float fbits(uint32_t u) { float v; memcpy(&v, &u, 4); return v; }
static float fadd(float a, float b) { return a + b; }
static float fsub(float a, float b) { return a - b; }
static float fmul(float a, float b) { return a * b; }
static float fdiv(float a, float b) { return a / b; }
static float fsqrt_clean(float a) { return a >= 0.0f ? (float)sqrt((double)a) : NAN; }

static int measured_luma(const uint8_t *raw, size_t raw_len, float *out)
{
    float bins[256] = {0};
    uint8_t counts[256] = {0};
    const float rc = fbits(0x3e991687), gc = fbits(0x3f1645a2), bc = fbits(0x3de978d5);
    const float scale = fbits(0x3504655e);
    float weighted = 0.0f, weight_sum = 0.0f;
    unsigned i;
    if (!raw || !out || raw_len != AEC_BYTES) return -1;
    for (i = 0; i < 1024; ++i) {
        const uint8_t *r = raw + i * 0x50;
        uint64_t rs = rd64(r) & MASK34;
        uint64_t gr = rd64(r + 8) & MASK34;
        uint64_t gb = rd64(r + 0x10) & MASK34;
        uint64_t bs = rd64(r + 0x18) & MASK34;
        unsigned cr = rd16(r + 0x06), cb = rd16(r + 0x1e), cgr = rd16(r + 0x0e), cgb = rd16(r + 0x16);
        unsigned row = i / 32, col = i % 32, oi;
        double v;
        float l, old, delta, step;
        if (cr != 1980 || cb != 1980 || cgr != 1980 || cgb != 1980) return -2;
        v = (double)gc * (double)(gr + gb) * 0.5;
        v = v + (double)rc * (double)rs;
        v = v + (double)bc * (double)bs;
        v = v * (double)scale;
        l = (float)v;
        if (((row + col) & 1u) != 0) continue;
        oi = (row / 2) * 16 + (col / 2);
        counts[oi]++;
        old = bins[oi];
        delta = fsub(l, old);
        step = fdiv(delta, (float)counts[oi]);
        bins[oi] = fadd(old, step);
    }
    for (i = 0; i < 256; ++i) {
        float w = 1.0f, prod;
        if (counts[i] != 2) return -3;
        weight_sum = fadd(weight_sum, w);
        prod = fmul(w, bins[i]);
        weighted = fadd(weighted, prod);
    }
    *out = fdiv(weighted, weight_sum);
    return 0;
}

static float lux001(float measured, float baseline)
{
    const float target = fbits(0x42480000), k = fbits(0x429bcc0c), tiny = fbits(0x33d6bf95);
    float den = measured > tiny ? measured : tiny;
    float num = target > tiny ? target : tiny;
    float ratio = fdiv(num, den), delta = 0.0f, candidate;
    if (ratio > 0.0f) delta = (float)(log10((double)ratio) * (double)k);
    candidate = fadd(baseline, delta);
    return candidate > 0.0f ? candidate : 0.0f;
}

static void anchor(const uint8_t *a, unsigned i, float *x, float *y) { *x = rfloat(a + 8*i); *y = rfloat(a + 8*i + 4); }
static void line_rec(const uint8_t *e, unsigned i, float *A, float *B, float *C, float *flag) { const uint8_t *p=e+0x90+16*i; *A=rfloat(p);*B=rfloat(p+4);*C=rfloat(p+8);*flag=rfloat(p+12); }
static void geom_rec(const uint8_t *e, unsigned i, float *A, float *B, float *C, float *flag) { const uint8_t *p=e+16*(i+1); *A=rfloat(p);*B=rfloat(p+4);*C=rfloat(p+8);*flag=rfloat(p+12); }

static int p03_classify(const uint8_t *e, float x, float y)
{
    int idx=4, prev=0;
    for (;;) {
        float A,B,C,flag,v;
        if (idx == 8) return 8;
        line_rec(e,(unsigned)idx,&A,&B,&C,&flag);
        v=fadd(fmul(B,y),fmul(A,x)); v=fadd(v,C);
        if (fabs((double)flag-1.0)<1e-12) v=-v;
        if (v < 0.0f) { if (prev==2) return idx; prev=1; --idx; if (idx==-1) return -1; }
        else if (v > 0.0f) { if (prev==1) return idx; prev=2; ++idx; }
        else return idx;
    }
}

static void p03_primary(const uint8_t *e,const uint8_t *an,float x,float y,unsigned ai,unsigned bi,unsigned gi,float *ratio,float *metric)
{
    float ax,ay,bx,by,A,B,C,flag,line,ya,xa,dA,yb,xb,dB,L2,r,t,perp2,perp,signv,sign;
    anchor(an,ai,&ax,&ay); anchor(an,bi,&bx,&by); geom_rec(e,gi,&A,&B,&C,&flag);
    line=fadd(fmul(B,y),fmul(A,x)); line=fadd(line,C); line=fmul(line,A);
    ya=fsub(y,ay); xa=fsub(x,ax); dA=fadd(fmul(ya,ya),fmul(xa,xa));
    yb=fsub(y,by); xb=fsub(x,bx); dB=fadd(fmul(yb,yb),fmul(xb,xb));
    L2=rfloat(e+0x110+4*gi);
    if (line != 0.0f) r=fdiv(fmul(fadd(fsub(dA,dB),L2),0.5f),L2); else r=fsqrt_clean(fdiv(dA,L2));
    t=fadd(r,r); t=fmul(t,r); t=fsub(t,fadd(r,r)); t=fadd(t,1.0f); t=fmul(t,L2);
    perp2=fmul(fsub(fadd(dB,dA),t),0.5f); perp=fsqrt_clean(perp2);
    if (r < 0.0f) { r=0.0f; perp=fsqrt_clean(dA); }
    signv=line;
    if (fabs((double)line)<1e-12) signv=fsub(y,C); else if (fabs((double)flag-1.0)<1e-12) signv=-line;
    sign=signv>0.0f?1.0f:-1.0f; *metric=fmul(sign,perp); if (isnan(*metric)) *metric=0.0f; *ratio=r;
}

static float p03_secondary(const uint8_t *e,float x,float y,unsigned ai,unsigned bi)
{
    float aA,aB,aC,af,bA,bB,bC,bf,vb,vb2,va,nb,na,q;
    line_rec(e,ai,&aA,&aB,&aC,&af); line_rec(e,bi,&bA,&bB,&bC,&bf);
    (void)af; (void)bf;
    vb=fadd(fadd(fmul(x,bA),bC),fmul(y,bB)); vb2=fmul(vb,vb);
    va=fadd(fadd(fmul(x,aA),aC),fmul(y,aB));
    nb=fadd(fmul(bB,bB),fmul(bA,bA)); na=fadd(fmul(aB,aB),fmul(aA,aA));
    q=fdiv(fdiv(vb2,nb),fdiv(fmul(va,va),na)); q=fsqrt_clean(q); return fdiv(1.0f,fadd(q,1.0f));
}

static float p03_blend(const uint8_t *e,float r,int idx)
{
    float raw=r, rr, k0,k1;
    (void)raw;
    rr=r>1.0f?1.0f:r; rr=rr<0.0f?0.0f:rr;
    if (idx==8) return (float)rd32(e+0x150);
    if (idx==9) return (float)rd32(e+0x1c4);
    k0=(float)rd32(e+0x150+16*idx); k1=(float)rd32(e+0x154+16*idx);
    return fadd(fmul(k0,fsub(1.0f,rr)),fmul(k1,rr));
}

static int p03(const uint8_t *e,size_t elen,const uint8_t *an,size_t alen,float x,float y,float *metric,float *cct)
{
    int cls; float r,m,fr,ax,ay,dx,dy;
    if (!e||!an||elen<0x240||alen<80||!metric||!cct) return -1;
    cls=p03_classify(e,x,y);
    if (cls==-1) { anchor(an,0,&ax,&ay);dx=fsub(x,ax);dy=fsub(y,ay);*metric=fsqrt_clean(fadd(fmul(dx,dx),fmul(dy,dy)));*cct=(float)rd32(e+0x150);return cls; }
    if (cls==8) { anchor(an,9,&ax,&ay);dx=fsub(x,ax);dy=fsub(y,ay);*metric=fsqrt_clean(fadd(fmul(dx,dx),fmul(dy,dy)));*cct=(float)rd32(e+0x1c4);return cls; }
    if (cls==0) { p03_primary(e,an,x,y,0,1,0,&r,&m);fr=r; }
    else if (cls==1) { p03_primary(e,an,x,y,1,2,1,&r,&m);fr=r; }
    else if (cls==2) { p03_primary(e,an,x,y,2,3,2,&r,&m);fr=r; }
    else if (cls==3) { p03_primary(e,an,x,y,3,5,3,&r,&m);fr=p03_secondary(e,x,y,3,4); }
    else if (cls==4) { p03_primary(e,an,x,y,3,5,3,&r,&m);fr=r; }
    else if (cls==5) { p03_primary(e,an,x,y,5,7,5,&r,&m);fr=p03_secondary(e,x,y,4,5); }
    else if (cls==6) { p03_primary(e,an,x,y,7,8,6,&r,&m);fr=r; }
    else if (cls==7) { p03_primary(e,an,x,y,8,9,7,&r,&m);fr=r; }
    else return -2;
    *metric=m; *cct=p03_blend(e,fr,cls==4?3:cls); return cls;
}

static float gap_s0(float x,float pe,float ns) { float alpha=fdiv(fsub(x,pe),fsub(ns,pe)); return fsub(1.0f,alpha); }
static float vmix(float prev,float next,float s0) { float a2=fsub(1.0f,s0); float a=fmul(a2,next),b=fmul(s0,prev); return fadd(a,b); }
static float leaf(const float *c,unsigned n,float x)
{
    unsigned i; const float *prev=c;
    if (x < c[0]) return c[2];
    if (x >= c[(n - 1) * 3 + 1]) return c[(n - 1) * 3 + 2];
    for (i=0;i<n;++i) { const float *r=c+i*3; if (x<r[0]) return vmix(prev[2],r[2],gap_s0(x,prev[1],r[0])); if (x<r[1]) return r[2]; prev=r; }
    return c[(n-1)*3+2];
}
static float p04_boundary(const float *c,float metric) { return metric<0.0f?c[4]:c[12]; }
static float p04_child(const float *nodes,const float *rows,unsigned ci,float cct,float metric)
{
    unsigned i; const float *n=nodes+ci*12; const float *rs=rows+ci*6*15; const float *prev=n;
    if (cct < n[0]) return leaf(rs, 5, metric);
    if (cct >= n[11]) return leaf(rs + 5 * 15, 5, metric);
    for (i=0;i<6;++i) { const float *nr=n+i*2; const float *cr=rs+i*15; if (cct<nr[0]) { const float *pr=rs+(i-1)*15; float w=gap_s0(cct,prev[1],nr[0]); float bp=p04_boundary(pr,metric),bn=p04_boundary(cr,metric),bi=vmix(bp,bn,w),scale=fdiv(metric,bi); return vmix(leaf(pr,5,fmul(scale,bp)),leaf(cr,5,fmul(scale,bn)),w); } if (cct<nr[1]) return leaf(cr,5,metric); prev=nr; }
    return leaf(rs+5*15,5,metric);
}
static float p04(const float *nodes,const float *rows,float lux,float cct,float metric)
{
    static const float roots[6]={0,91,160,180,305,859}; unsigned i; const float *prev=roots;
    if (lux < roots[0]) return p04_child(nodes, rows, 0, cct, metric);
    if (lux >= roots[5]) return p04_child(nodes, rows, 2, cct, metric);
    for (i=0;i<3;++i) { const float *r=roots+i*2; if (lux<r[0]) return vmix(p04_child(nodes,rows,i-1,cct,metric),p04_child(nodes,rows,i,cct,metric),gap_s0(lux,prev[1],r[0])); if (lux<r[1]) return p04_child(nodes,rows,i,cct,metric); prev=r; }
    return p04_child(nodes,rows,2,cct,metric);
}
static float p05(const float *rows,float lux,float cct)
{
    static const float roots[20]={0,69,82,91,96,110,120,140,170,190,197,207,225,260,270,290,300,350,360,450}; unsigned i; const float *prev=roots;
    if (lux < roots[0]) return leaf(rows, 10, cct);
    if (lux >= roots[19]) return leaf(rows + 9 * 30, 10, cct);
    for (i=0;i<10;++i) { const float *r=roots+i*2; if (lux<r[0]) return vmix(leaf(rows+(i-1)*30,10,cct),leaf(rows+i*30,10,cct),gap_s0(lux,prev[1],r[0])); if (lux<r[1]) return leaf(rows+i*30,10,cct); prev=r; }
    return leaf(rows+9*30,10,cct);
}

int e003i_trigger_native(const uint8_t *aec,size_t aec_len,const uint8_t *awb,size_t awb_len,float baseline,
                         const uint8_t *engine,size_t engine_len,const uint8_t *anchors,size_t anchors_len,
                         const float *p04_nodes,const float *p04_rows,const float *p05_rows,
                         struct e003i_trigger_result *out)
{
    float meas,lux,sw=0.0f,sx=0.0f,sy=0.0f; unsigned i,p01=0,valid=0; int rc;
    if (!out||!awb||awb_len!=AWB_BYTES||!p04_nodes||!p04_rows||!p05_rows) return -10;
    rc=measured_luma(aec,aec_len,&meas); if (rc) return rc; lux=lux001(meas,baseline);
    for (i=0;i<AWB_REGIONS;++i) {
        const uint8_t *r=awb+i*AWB_STRIDE; uint64_t s0=rd64(r)&MASK34,s1=rd64(r+0x18)&MASK34,sg=(rd64(r+8)&MASK34)+(rd64(r+0x10)&MASK34);
        unsigned c0=rd16(r+0x06),c1=rd16(r+0x1e),cg=rd16(r+0x0e)+rd16(r+0x16); int badn; float m0,mg,m1,x,y,bad,metric,cct,w40,w44,w;
        if (!c0||!c1||!cg) continue;
        m0=fdiv((float)s0,(float)(c0<<10)); mg=fdiv((float)sg,(float)(cg<<10)); m1=fdiv((float)s1,(float)(c1<<10));
        x=mg!=0.0f?fdiv(m0,mg):0.0f; y=mg!=0.0f?fdiv(m1,mg):0.0f; badn=2640-(int)(c0+c1+cg); bad=fdiv(fmul((float)badn,100.0f),2640.0f);
        if (!(m0 > 1.0f && mg > 1.0f && m1 > 1.0f && bad < 80.0f)) continue;
        ++p01;
        if (p03(engine,engine_len,anchors,anchors_len,x,y,&metric,&cct)<-1) return -20;
        w40=p04(p04_nodes,p04_rows,lux,cct,metric); w44=p05(p05_rows,lux,cct); if (w40==0.0f||w44==0.0f) continue;
        ++valid; w=fmul(w40,w44); sw=fadd(sw,w); sx=fadd(sx,fmul(x,w)); sy=fadd(sy,fmul(y,w));
    }
    if (sw==0.0f) return -30;
    out->measured_luma=meas; out->lux=lux; out->agw_x=fdiv(sx,sw); out->agw_y=fdiv(sy,sw); out->sum_weight=sw; out->p01=p01; out->valid=valid;
    { float metric; if (p03(engine,engine_len,anchors,anchors_len,out->agw_x,out->agw_y,&metric,&out->fresh_cct)<-1) return -31; }
    return 0;
}
