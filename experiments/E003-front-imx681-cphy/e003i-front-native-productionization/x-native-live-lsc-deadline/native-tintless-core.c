#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <math.h>

#define GW 32
#define GH 24
#define REGIONS (GW*GH)
#define CORE_BYTES 0x126e8u
#define STATS_BYTES 0x12c20u
#define MESH_N 221

static inline uint8_t r8(const uint8_t *p, size_t o){ return p[o]; }
static inline uint16_t r16(const uint8_t *p, size_t o){ uint16_t v; memcpy(&v,p+o,2); return v; }
static inline uint32_t r32(const uint8_t *p, size_t o){ uint32_t v; memcpy(&v,p+o,4); return v; }
static inline int32_t ri32(const uint8_t *p, size_t o){ int32_t v; memcpy(&v,p+o,4); return v; }
static inline uint64_t r64(const uint8_t *p, size_t o){ uint64_t v; memcpy(&v,p+o,8); return v; }
static inline float rf(const uint8_t *p, size_t o){ float v; memcpy(&v,p+o,4); return v; }
static inline void w8(uint8_t *p,size_t o,uint8_t v){ p[o]=v; }
static inline void w32(uint8_t *p,size_t o,uint32_t v){ memcpy(p+o,&v,4); }
static inline void wi32(uint8_t *p,size_t o,int32_t v){ memcpy(p+o,&v,4); }
static inline void wf(uint8_t *p,size_t o,float v){ memcpy(p+o,&v,4); }
static inline float bitsf(uint32_t u){ float v; memcpy(&v,&u,4); return v; }
static inline int32_t wrap32(int64_t v){ uint32_t u=(uint32_t)v; int32_t s; memcpy(&s,&u,4); return s; }

static void preprocess_stats(uint8_t *s,const uint8_t *raw){
    uint32_t area=(uint32_t)(r16(s,0x0a)>>1)*(uint32_t)(r16(s,0x08)>>1);
    uint32_t off=r32(s,0x70);
    uint16_t sr=r16(s,0x18), sgb=r16(s,0x1a), sb=r16(s,0x1c), sgr=r16(s,0x1e);
    uint32_t stride=(r32(raw,0)&2)?0x64:0x32;
    for(int i=0;i<REGIONS;i++){
        const uint8_t *rec=raw+(size_t)i*stride;
        const int ro[4]={0x20,0x28,0x30,0x38};
        const uint16_t sc[4]={sr,sgb,sb,sgr};
        uint64_t val[4];
        for(int k=0;k<4;k++){
            uint16_t cnt=r16(rec,0x48+(ro[k]-0x20)/4);
            uint32_t rem=(uint32_t)(area-cnt);
            uint64_t v=r64(rec,ro[k])+(uint64_t)rem*sc[k]+off;
            val[k]=v<2?1:v;
        }
        float inv=1.0f/(float)(val[3]+val[2]);
        wf(s,0x2e64+i*4,(float)((float)((float)val[0]+(float)val[0])*inv));
        wf(s,0x3a64+i*4,(float)((float)((float)val[1]+(float)val[1])*inv));
    }
}

static void ln_field(uint8_t *s,size_t src,size_t dst){ for(int i=0;i<REGIONS;i++) wf(s,dst+i*4,logf(rf(s,src+i*4))); }
static void accumulate(uint8_t *s,size_t a,size_t b,size_t da,size_t db){
    for(int i=0;i<REGIONS;i++){
        wf(s,a+i*4,rf(s,a+i*4)+rf(s,da+i*4));
        wf(s,b+i*4,rf(s,b+i*4)+rf(s,db+i*4));
    }
}
static void quant_q16(uint8_t *s,size_t src,size_t dst){
    for(int i=0;i<REGIONS;i++){
        float x=rf(s,src+i*4); float y=(x*131072.0f+1.0f)*0.5f; wi32(s,dst+i*4,(int32_t)y);
    }
}

static void pad_mesh(uint8_t *s,size_t src,size_t dst){
    int h=r8(s,0x20),w=r8(s,0x21),stride=w+3;
    float S[16][20],P[16][20]; memset(S,0,sizeof(S)); memset(P,0,sizeof(P));
    for(int y=0;y<h;y++)for(int x=0;x<w;x++)S[y][x]=rf(s,src+(y*w+x)*4);
    #define EXT(a,b) ((float)(((float)(a)+(float)(a))-(float)(b)))
    for(int y=0;y<h;y++)for(int x=0;x<w;x++)P[y+1][x+1]=S[y][x];
    for(int x=0;x<w;x++)P[0][x+1]=EXT(S[0][x],S[1][x]);
    for(int y=0;y<h;y++){P[y+1][0]=EXT(S[y][0],S[y][1]);P[y+1][w+1]=EXT(S[y][w-1],S[y][w-2]);}
    for(int x=0;x<w;x++)P[h+1][x+1]=EXT(S[h-1][x],S[h-2][x]);
    P[0][0]=EXT(P[1][1],P[2][2]); P[0][w+1]=EXT(P[1][w],P[2][w-1]);
    P[h+1][0]=EXT(P[h][1],P[h-1][2]); P[h+1][w+1]=EXT(P[h][w],P[h-1][w-1]);
    for(int y=0;y<h+2;y++)P[y][w+2]=EXT(P[y][w+1],P[y][w]);
    for(int x=0;x<w+2;x++)P[h+2][x]=EXT(P[h+1][x],P[h][x]);
    P[h+2][0]=EXT(P[h+1][1],P[h][2]); P[h+2][w+2]=EXT(P[h+1][w+1],P[h][w]);
    for(int y=0;y<h+3;y++)for(int x=0;x<stride;x++)wf(s,dst+(y*stride+x)*4,P[y][x]);
    #undef EXT
}

static void bicubic_row(uint8_t *s,double w0,double w1,double w2,double w3,size_t p0,size_t p1,size_t p2,size_t p3,size_t out,int segments,int substeps){
    int nseg=segments-1;if(nseg<=0)return;
    size_t ps[4]={p0,p1,p2,p3};
    for(int j=0;j<nseg;j++){
        float a[4][4];for(int q=0;q<4;q++)for(int k=0;k<4;k++)a[q][k]=rf(s,ps[q]+(j+k)*4);
        for(int k=0;k<substeps;k++){
            double t=(double)k/(double)substeps,t2=t*t,t3=t2*t;
            double hx0=((2.0*t2-t3)-t)*0.5,hx1=((3.0*t3-5.0*t2)+2.0)*0.5,hx2=((4.0*t2-3.0*t3)+t)*0.5,hx3=(t3-t2)*0.5;
            double rr[4];for(int q=0;q<4;q++)rr[q]=(double)a[q][0]*hx0+(double)a[q][1]*hx1+(double)a[q][2]*hx2+(double)a[q][3]*hx3;
            wf(s,out+(j*substeps+k)*4,(float)(rr[0]*w0+rr[1]*w1+rr[2]*w2+rr[3]*w3));
        }
    }
}

static void interpolate_mesh_to_stats(uint8_t *s,size_t src,size_t dst){
    int factor=r8(s,0x2a), sh=r8(s,0x20), sw=r8(s,0x21); size_t padded=0x121e8,temp=0x5e64;
    pad_mesh(s,src,padded); int tw=(sw-1)*factor+1, th=(sh-1)*factor+1,pstride=sw+3;
    for(int yy=0;yy<th-1;yy++){
        int iy=yy/factor; double fy=(double)yy/(double)factor-(double)iy,fy2=fy*fy,fy3=fy2*fy;
        double wy0=((2.0*fy2-fy3)-fy)*0.5,wy1=((3.0*fy3-5.0*fy2)+2.0)*0.5,wy2=((4.0*fy2-3.0*fy3)+fy)*0.5,wy3=(fy3-fy2)*0.5;
        size_t p0=padded+(iy+0)*pstride*4,p1=padded+(iy+1)*pstride*4,p2=padded+(iy+2)*pstride*4,p3=padded+(iy+3)*pstride*4;
        bicubic_row(s,wy0,wy1,wy2,wy3,p0,p1,p2,p3,temp+(size_t)yy*tw*4,sw,factor); wf(s,temp+((size_t)yy*tw+tw-1)*4,0.0f);
    }
    for(int x=0;x<tw;x++)wf(s,temp+((size_t)(th-1)*tw+x)*4,0.0f);
    int ow=r8(s,0x0c),oh=r8(s,0x0d);uint16_t cy=r16(s,0x0a),cx=r16(s,0x08),oy=r16(s,0x0e),ox=r16(s,0x10),ay=r16(s,0x24),ax=r16(s,0x22),dy=r16(s,0x26),dx=r16(s,0x28);
    for(int y=0;y<oh;y++){
        float py=(float)((float)((float)((float)(cy*y)+(float)(cy*0.5f))+(float)oy)+(float)ay);float yyf=py/(float)dy;int iy=(int)yyf;float fy=yyf-(float)iy;
        for(int x=0;x<ow;x++){
            float px=(float)((float)((float)((float)(cx*x)+(float)(cx*0.5f))+(float)ox)+(float)ax);float xxf=px/(float)dx;int ix=(int)xxf;float fx=xxf-(float)ix;size_t lo=(size_t)iy*tw+ix,hi=(size_t)(iy+1)*tw+ix;float omx=1.0f-fx,omy=1.0f-fy;
            float top=rf(s,temp+(hi+1)*4)*fx+rf(s,temp+hi*4)*omx;float bot=rf(s,temp+(lo+1)*4)*fx+rf(s,temp+lo*4)*omx;wf(s,dst+(y*ow+x)*4,top*fy+bot*omy);
        }
    }
}

static void fft_radix2(uint8_t *s,int n,size_t rp,size_t ip,size_t tw,size_t perm){
    if(n>1)for(int i=1;i<n;i++){int j=r8(s,perm+i);uint32_t a=r32(s,rp+i*4),b=r32(s,rp+j*4),c=r32(s,ip+i*4),d=r32(s,ip+j*4);w32(s,rp+i*4,b);w32(s,rp+j*4,a);w32(s,ip+i*4,d);w32(s,ip+j*4,c);}
    int levels=1;if(n>2)while((1<<levels)<n)levels++;int stride=1,half=n/2,butterflies=n;
    for(int l=0;l<levels;l++){
        int twstep=stride?half/stride:0;butterflies>>=1;
        for(int group=0;group<stride;group++){
            int ti=group*twstep*2;float wr=rf(s,tw+ti*4),wi=rf(s,tw+(ti+1)*4);int idx=group;
            for(int q=0;q<butterflies;q++){
                int j=idx+stride;float br=rf(s,rp+j*4),bi=rf(s,ip+j*4);float tr=br*wr-bi*wi,tii=bi*wr+br*wi;float ar=rf(s,rp+idx*4),ai=rf(s,ip+idx*4);wf(s,rp+j*4,ar-tr);wf(s,ip+j*4,ai-tii);wf(s,rp+idx*4,ar+tr);wf(s,ip+idx*4,ai+tii);idx+=stride*2;
            }
        }stride<<=1;
    }
}
static void transpose_u32(uint8_t *s,int rows,int cols,size_t src,size_t dst){for(int r=0;r<rows;r++)for(int c=0;c<cols;c++)w32(s,dst+((size_t)c*rows+r)*4,r32(s,src+((size_t)r*cols+c)*4));}
static void negate_bits(uint8_t *s,size_t p,int n){for(int i=0;i<n;i++)w32(s,p+i*4,r32(s,p+i*4)^0x80000000u);}
static void fft_forward(uint8_t *s,size_t rp,size_t ip,size_t tp,size_t tw32,size_t tw64,size_t p64,size_t p32){
    for(int off=0;off<0x800;off+=0x20)
        fft_radix2(s,0x20,rp+(size_t)off*4,ip+(size_t)off*4,tw32,p32);
    transpose_u32(s,0x40,0x20,rp,tp);
    transpose_u32(s,0x40,0x20,ip,rp);
    for(int off=0;off<0x800;off+=0x40)
        fft_radix2(s,0x40,tp+(size_t)off*4,rp+(size_t)off*4,tw64,p64);
    transpose_u32(s,0x20,0x40,rp,ip);
    transpose_u32(s,0x20,0x40,tp,rp);
}
static void fft_inverse(uint8_t *s,size_t rp,size_t ip,size_t tp,size_t tw32,size_t tw64,size_t p64,size_t p32){
    negate_bits(s,ip,0x800);for(int off=0;off<0x800;off+=0x20)fft_radix2(s,0x20,rp+(size_t)off*4,ip+(size_t)off*4,tw32,p32);transpose_u32(s,0x40,0x20,rp,tp);transpose_u32(s,0x40,0x20,ip,rp);for(int off=0;off<0x800;off+=0x40)fft_radix2(s,0x40,tp+(size_t)off*4,rp+(size_t)off*4,tw64,p64);transpose_u32(s,0x20,0x40,rp,ip);transpose_u32(s,0x20,0x40,tp,rp);negate_bits(s,ip,0x800);float sc=1.0f/2048.0f;for(int i=0;i<0x800;i++){wf(s,rp+i*4,rf(s,rp+i*4)*sc);wf(s,ip+i*4,rf(s,ip+i*4)*sc);}
}

static void periodic_grad(uint8_t *s,size_t src,size_t dx,size_t dy){
    float a[REGIONS];for(int i=0;i<REGIONS;i++)a[i]=rf(s,src+i*4);for(int y=0;y<GH;y++)for(int x=0;x<GW;x++){int i=y*GW+x,rx=y*GW+((x+1)%GW),ry=((y+1)%GH)*GW+x;wf(s,dx+i*4,a[rx]-a[i]);wf(s,dy+i*4,a[ry]-a[i]);}
}
static void spectral_threshold(uint8_t *s){
    float th[16];for(int i=0;i<16;i++){float q=rf(s,0x30+i*4)/100.0f;th[i]=q*q;}
    int cls[REGIONS];for(int i=0;i<REGIONS;i++)cls[i]=(int)rf(s,0x78+i*4);
    for(int y=0;y<GH;y++)for(int x=0;x<GW-1;x++){int i=y*GW+x;float re=rf(s,0x5e64+i*4),im=rf(s,0x6a64+i*4),mag=re*re+im*im;if(th[cls[i]]<mag){wf(s,0x5e64+i*4,0);wf(s,0x6a64+i*4,0);}}
    for(int y=0;y<GH-1;y++)for(int x=0;x<GW;x++){int i=y*GW+x;float re=rf(s,0x7664+i*4),im=rf(s,0x8264+i*4),mag=re*re+im*im;if(th[cls[i]]<mag){wf(s,0x7664+i*4,0);wf(s,0x8264+i*4,0);}}
}
static void proj_rows(uint8_t *s,size_t base){
    float v[REGIONS];for(int i=0;i<REGIONS;i++)v[i]=rf(s,base+i*4);float mv=bitsf(0x3d042108u);
    for(int y=0;y<GH;y++){int o=y*GW;float total=0;for(int x=0;x<GW-1;x++)total=total+v[o+x];float m16=total*mv,ms=total/31.0f;for(int x=0;x<16;x++)v[o+x]=v[o+x]-m16;for(int x=16;x<GW-1;x++)v[o+x]=v[o+x]-ms;v[o+GW-1]=0;}
    memcpy(s+base,v,sizeof(v));
}
static void proj_cols(uint8_t *s,size_t base){
    float v[REGIONS];for(int i=0;i<REGIONS;i++)v[i]=rf(s,base+i*4);for(int x=0;x<GW;x++){float total=0;for(int y=0;y<GH-1;y++)total=total+v[y*GW+x];float m=total/23.0f;for(int y=0;y<GH-1;y++)v[y*GW+x]=v[y*GW+x]-m;v[(GH-1)*GW+x]=0;}memcpy(s+base,v,sizeof(v));
}
static void divergence(uint8_t *s,size_t a,size_t b,size_t out){
    float av[REGIONS],bv[REGIONS],ov[REGIONS];for(int i=0;i<REGIONS;i++){av[i]=rf(s,a+i*4);bv[i]=rf(s,b+i*4);}for(int y=0;y<GH;y++)for(int x=0;x<GW;x++){int i=y*GW+x,left=y*GW+((x-1+GW)%GW),up=((y-1+GH)%GH)*GW+x;float da=av[left]-av[i],db=bv[up]-bv[i];ov[i]=da+db;}memcpy(s+out,ov,sizeof(ov));
}
static void solver_prepare(uint8_t *s,size_t b){memmove(s+b+0xc00,s+b,0x600);memset(s+b+0x1200,0,0x800);memmove(s+b+0x1a00,s+b+0x600,0x600);}
static void solver(uint8_t *s,size_t fa,size_t fb){
    periodic_grad(s,fa,0x5e64,0x7664);periodic_grad(s,fb,0x6a64,0x8264);spectral_threshold(s);proj_rows(s,0x5e64);proj_rows(s,0x6a64);proj_cols(s,0x7664);proj_cols(s,0x8264);divergence(s,0x5e64,0x7664,0x8e64);divergence(s,0x6a64,0x8264,0xae64);solver_prepare(s,0x8e64);solver_prepare(s,0xae64);fft_forward(s,0x8e64,0xae64,0x5e64,0xc84,0xd04,0xe24,0xe04);for(int i=0;i<0x800;i++){float w=rf(s,0xe64+i*4);wf(s,0x8e64+i*4,rf(s,0x8e64+i*4)*w);wf(s,0xae64+i*4,rf(s,0xae64+i*4)*w);}wf(s,0x8e64,0);wf(s,0xae64,0);fft_inverse(s,0x8e64,0xae64,0x5e64,0xc84,0xd04,0xe24,0xe04);
}

static void box3(uint8_t *s,size_t src,size_t dst){
    int32_t a[REGIONS],h[REGIONS],b[REGIONS],o[REGIONS];for(int i=0;i<REGIONS;i++)a[i]=ri32(s,src+i*4);
    for(int y=0;y<GH;y++)for(int x=0;x<GW;x++){int64_t v=(int64_t)a[y*GW+(x?x-1:0)]+a[y*GW+x]+a[y*GW+(x<GW-1?x+1:GW-1)];h[y*GW+x]=wrap32(v);}
    for(int y=0;y<GH;y++)for(int x=0;x<GW;x++){int idx=y*GW+x;if(y<2||y>=GH-2||x<2||x>=GW-2)b[idx]=wrap32((int64_t)a[idx]*9);else{int32_t v=0;for(int yy=y-1;yy<=y+1;yy++)for(int xx=x-1;xx<=x+1;xx++)v=wrap32((int64_t)v+a[yy*GW+xx]);b[idx]=v;}o[idx]=b[idx]/9;}
    memcpy(s+0x5e64,h,sizeof(h));memcpy(s+0x6a64,b,sizeof(b));memcpy(s+dst,o,sizeof(o));
}
static void exp_q16(uint8_t *s,size_t p){float inv=1.0f/65536.0f;for(int i=0;i<REGIONS;i++){int32_t x=ri32(s,p+i*4);float arg=-(float)x*inv;float ev=expf(arg);float y=(ev*131072.0f+1.0f)*0.5f;wi32(s,p+i*4,(int32_t)y);}}

static void map_corr(uint8_t *s,size_t src,float *dst){
    int32_t g[29][37];memset(g,0,sizeof(g));for(int y=0;y<24;y++)for(int x=0;x<32;x++)g[y+2][x+2]=ri32(s,src+(y*32+x)*4);
    #define W2(a,b) wrap32((int64_t)2*(a)-(b))
    for(int y=2;y<26;y++){g[y][1]=W2(g[y][2],g[y][3]);g[y][0]=W2(g[y][1],g[y][2]);g[y][34]=W2(g[y][33],g[y][32]);g[y][35]=W2(g[y][34],g[y][33]);g[y][36]=W2(g[y][35],g[y][34]);}
    for(int x=0;x<37;x++){g[1][x]=W2(g[2][x],g[3][x]);g[0][x]=W2(g[1][x],g[2][x]);g[26][x]=W2(g[25][x],g[24][x]);g[27][x]=W2(g[26][x],g[25][x]);g[28][x]=W2(g[27][x],g[26][x]);}
    g[1][1]=W2(g[2][2],g[3][3]);g[1][34]=W2(g[2][33],g[3][32]);g[0][1]=W2(g[1][1],g[2][1]);g[0][34]=W2(g[1][34],g[2][34]);g[1][0]=W2(g[1][1],g[1][2]);g[1][35]=W2(g[1][34],g[1][33]);g[0][0]=W2(g[1][1],g[2][2]);g[0][35]=W2(g[1][34],g[2][33]);g[0][36]=W2(g[0][35],g[0][34]);g[1][36]=W2(g[1][35],g[1][34]);
    g[26][1]=W2(g[25][2],g[24][3]);g[26][34]=W2(g[25][33],g[24][32]);g[26][0]=W2(g[26][1],g[26][2]);g[26][35]=W2(g[26][34],g[26][33]);g[26][36]=W2(g[26][35],g[26][34]);g[27][0]=W2(g[26][1],g[25][2]);g[27][1]=W2(g[26][1],g[25][1]);g[27][34]=W2(g[26][34],g[25][34]);g[27][35]=W2(g[26][34],g[25][33]);g[27][36]=W2(g[27][35],g[27][34]);g[28][0]=W2(g[27][0],g[26][0]);g[28][1]=W2(g[27][1],g[26][1]);g[28][34]=W2(g[27][34],g[26][34]);g[28][35]=W2(g[27][35],g[26][35]);g[28][36]=W2(g[27][35],g[26][34]);
    for(int y=0;y<29;y++)for(int x=0;x<37;x++)wi32(s,0x5e64+(y*37+x)*4,g[y][x]);
    uint16_t cx=r16(s,0x08),cy=r16(s,0x0a),oy=r16(s,0x0e),ox=r16(s,0x10),ax=r16(s,0x22),ay=r16(s,0x24),dy=r16(s,0x26),dx=r16(s,0x28);int mh=r8(s,0x20),mw=r8(s,0x21),factor=r8(s,0x2a);
    float sx=1.5f-(float)(ax+ox)/(float)cx;if(sx<0)sx=0;float sy=1.5f-(float)(ay+oy)/(float)cy;if(sy<0)sy=0;float stepx=(float)(dx*factor)/(float)cx,stepy=(float)(dy*factor)/(float)cy;
    for(int y=0;y<mh;y++){float yf=(float)y*stepy+sy;int iy=(int)yf;float fy=yf-(float)iy,omy=1.0f-fy;for(int x=0;x<mw;x++){float xf=(float)x*stepx+sx;int ix=(int)xf;float fx=xf-(float)ix,omx=1.0f-fx;float top=(float)g[iy][ix]*omx+(float)g[iy][ix+1]*fx;float bot=(float)g[iy+1][ix]*omx+(float)g[iy+1][ix+1]*fx;dst[y*mw+x]=top*omy+bot*fy;}}
    #undef W2
}

static int final_apply(uint8_t *s,const float *ref,float *out){
    int mh=r8(s,0x20),mw=r8(s,0x21),n=mh*mw;if(n!=MESH_N)return -8;
    if(r8(s,0x74)==0){size_t a=0x4664,b=0x5264;for(int i=0;i<n;i++){float den=ref[2*n+i]+ref[n+i];wf(s,a+i*4,(ref[i]+ref[i])/den);wf(s,b+i*4,(ref[3*n+i]+ref[3*n+i])/den);}interpolate_mesh_to_stats(s,a,a);interpolate_mesh_to_stats(s,b,b);ln_field(s,a,a);ln_field(s,b,b);w8(s,0x74,1);}
    accumulate(s,0x2e64,0x3a64,0x4664,0x5264);solver(s,0x2e64,0x3a64);quant_q16(s,0x8e64,0x8e64);quant_q16(s,0xae64,0xae64);box3(s,0x8e64,0x2e64);box3(s,0xae64,0x3a64);exp_q16(s,0x2e64);exp_q16(s,0x3a64);map_corr(s,0x2e64,out);map_corr(s,0x3a64,out+3*n);
    float q16=bitsf(0x37800000u),floorv=bitsf(0x3f8020c5u),minv=floorv;for(int i=0;i<n;i++){float v0=(ref[i]*q16)*out[i],v3=(ref[3*n+i]*q16)*out[3*n+i];out[i]=v0;out[3*n+i]=v3;out[n+i]=ref[n+i];out[2*n+i]=ref[2*n+i];if(v0<minv)minv=v0;if(v3<minv)minv=v3;}if(!(minv>0.0f))return -4;if(minv<floorv){float sc=floorv/minv;for(int p=0;p<4;p++)for(int i=0;i<n;i++)out[p*n+i]=out[p*n+i]*sc;}
    float strength=rf(s,0xc7c);for(int p=0;p<4;p++)for(int i=0;i<n;i++)out[p*n+i]=(out[p*n+i]-1.0f)*strength+1.0f;float ceilv=rf(s,0xc80)-bitsf(0x3a83126fu);for(int p=0;p<4;p++)for(int i=0;i<n;i++)if(ceilv<out[p*n+i])return -4;return 0;
}

static void smooth_map(uint8_t *s,size_t src,size_t dst){int32_t v[REGIONS];for(int i=0;i<REGIONS;i++)v[i]=ri32(s,src+i*4);for(int y=0;y<GH;y++)for(int x=0;x<GW;x++){int64_t sum=0;int ys[3]={y?y-1:0,y,y<GH-1?y+1:GH-1},xs[3]={x?x-1:0,x,x<GW-1?x+1:GW-1};for(int a=0;a<3;a++)for(int b=0;b<3;b++)sum+=v[ys[a]*GW+xs[b]];wi32(s,dst+(y*GW+x)*4,(int32_t)(sum/9));}}

static inline float fadd(float a,float b){ return (float)(a+b); }
static inline float fsub(float a,float b){ return (float)(a-b); }
static inline float fmul(float a,float b){ return (float)(a*b); }
static inline float fdivv(float a,float b){ return (float)(a/b); }

static void catmull(float t,float w[4]){
    t=(float)t;
    float t2=fmul(t,t),t3=fmul(t2,t);
    w[0]=fmul(fsub(fsub(fadd(t2,t2),t3),t),0.5f);
    w[1]=fmul(fadd(fsub(fmul(t3,3.0f),fmul(t2,5.0f)),2.0f),0.5f);
    w[2]=fmul(fadd(fsub(fmul(t2,4.0f),fmul(t3,3.0f)),t),0.5f);
    w[3]=fmul(fsub(t3,t2),0.5f);
}
static float h4f(const float *p,const float w[4]){
    float z=fadd(fmul(p[0],w[0]),fmul(p[1],w[1]));
    z=fadd(z,fmul(p[2],w[2]));
    z=fadd(z,fmul(p[3],w[3]));
    return z;
}

static void resample_channel_17x13(const float *src,float *out){
    float pad[15][19]; memset(pad,0,sizeof(pad));
    for(int r=0;r<13;r++)for(int c=0;c<17;c++)pad[r+1][c+1]=src[r*17+c];
    for(int r=1;r<14;r++){
        pad[r][0]=fsub(fadd(pad[r][1],pad[r][1]),pad[r][2]);
        pad[r][18]=fsub(fadd(pad[r][17],pad[r][17]),pad[r][16]);
    }
    for(int c=0;c<19;c++){
        pad[0][c]=fsub(fadd(pad[1][c],pad[1][c]),pad[2][c]);
        pad[14][c]=fsub(fadd(pad[13][c],pad[13][c]),pad[12][c]);
    }
    float spx=fdivv((float)(4048/2-1),16.0f);
    float spy=fdivv((float)(3152/2-1),12.0f);
    const int x0=104/2,y0=496/2-36;
    const float cmin=1.0f,cmax=15.99899959564209f;
    for(int iy=0;iy<13;iy++){
        float py=(float)(y0+iy*96);
        float v=fdivv(fadd(py,spy),spy);
        int iv=(int)floorf(v); float fy=fsub(v,(float)iv),wy[4]; catmull(fy,wy);
        for(int ix=0;ix<17;ix++){
            float px=(float)(x0+ix*120);
            float u=fdivv(fadd(px,spx),spx);
            int iu=(int)floorf(u); float fx=fsub(u,(float)iu),wx[4]; catmull(fx,wx);
            float z;
            if(iy==0||iy==12||ix==0||ix==16){
                float omx=fsub(1.0f,fx);
                float top=fadd(fmul(pad[iv][iu+1],fx),fmul(pad[iv][iu],omx));
                float omy=fsub(1.0f,fy);
                z=fmul(top,omy);
                float bot=fadd(fmul(pad[iv+1][iu+1],fx),fmul(pad[iv+1][iu],omx));
                z=fadd(z,fmul(bot,fy));
            }else{
                float hc=h4f(&pad[iv][iu-1],wx);
                float hp=h4f(&pad[iv-1][iu-1],wx);
                float hn=h4f(&pad[iv+1][iu-1],wx);
                float h2=h4f(&pad[iv+2][iu-1],wx);
                z=fmul(hc,wy[1]); z=fadd(z,fmul(hp,wy[0])); z=fadd(z,fmul(hn,wy[2])); z=fadd(z,fmul(h2,wy[3]));
            }
            if(z<cmin)z=cmin;
            if(z>cmax)z=cmax;
            out[iy*17+ix]=(float)z;
        }
    }
}

int lsc_resample_x23_native(const float *x23,float *out){
    if(!x23||!out)return -1;
    for(int ch=0;ch<4;ch++)resample_channel_17x13(x23+ch*221,out+ch*221);
    return 0;
}

int tintless_core_mode2_native(uint8_t *s,size_t slen,const uint8_t *raw,size_t rawlen,const float *ref,float *out){
    if(!s||!raw||!ref||!out||slen<CORE_BYTES||rawlen<STATS_BYTES)
        return -100;
    if(r16(s,0)!=2||r16(s,2)!=2||r8(s,0x12)!=0)
        return -101;
    if(r32(raw,4)!=REGIONS)
        return -3;
    int n=r8(s,0x20)*r8(s,0x21);
    if(n!=MESH_N)
        return -8;
    w8(s,0x74,0);preprocess_stats(s,raw);ln_field(s,0x2e64,0x2e64);ln_field(s,0x3a64,0x3a64);size_t t1=0x8e64,t2=0xae64;memcpy(s+t1,ref+2*n,n*4);memcpy(s+t2,ref+n,n*4);interpolate_mesh_to_stats(s,t1,t1);interpolate_mesh_to_stats(s,t2,t2);
    uint32_t area=(uint32_t)(r16(s,0x0a)>>1)*(uint32_t)(r16(s,0x08)>>1),off=r32(s,0x70);uint16_t sb=r16(s,0x1c),sgr=r16(s,0x1e);uint32_t stride=(r32(raw,0)&2)?0x64:0x32;uint32_t shift=r32(s,0x14)&0x1f,quant=(1u<<shift)/16u;float scale=(float)quant;
    int32_t uns[REGIONS];for(int i=0;i<REGIONS;i++){const uint8_t *rec=raw+(size_t)i*stride;uint64_t bv=r64(rec,0x30)+(uint64_t)(uint32_t)(area-r16(rec,0x4c))*sb+off,gr=r64(rec,0x38)+(uint64_t)(uint32_t)(area-r16(rec,0x4e))*sgr+off;if(bv<2)bv=1;if(gr<2)gr=1;float g2=rf(s,t1+i*4),g1=rf(s,t2+i*4);int64_t vb=(int64_t)(g1*(float)bv),vg=(int64_t)(g2*(float)gr);uint64_t half=((uint64_t)(vb+vg))>>1;float q=(float)half;q=q/(float)area;q=q/scale;uns[i]=q>15.0f?15:(int32_t)q;}memcpy(s+t1,uns,sizeof(uns));smooth_map(s,t1,0x78);return final_apply(s,ref,out);
}
