/* SPDX-License-Identifier: GPL-2.0-only */
/* Offline derived-equality audit; never print private profile or table bytes. */
#include <stdio.h>
#include <stdlib.h>
#include "native-front-params.h"
#define CAPSULE_BYTES 41088U
static void put(unsigned char *p, unsigned offset, uint64_t value, unsigned n)
{
 for (unsigned i=0;i<n;i++) p[offset+i] = value >> (8*i);
}
int main(int argc,char **argv)
{
 unsigned char seed[CAPSULE_BYTES], got[CAPSULE_BYTES], expected[CAPSULE_BYTES], p[64];
 uint32_t values[9][6];
 unsigned offset=0, checked=0;
 FILE *f=NULL, *pack=NULL;
 int rc=1;
 if (argc!=3) return 1;
 f=fopen(argv[1],"rb");pack=fopen(argv[2],"rb");
 if (!f || !pack || fread(seed,1,sizeof(seed),f)!=sizeof(seed) || fgetc(f)!=EOF)
  goto out;
 if (memcmp(seed,"E3HPIX01",8) || native_params_le64(seed+44)!=4 ||
     native_params_le32(seed+20)!=36) goto out;
 for (unsigned i=0;i<36;i++) {
  const unsigned char *d=seed+64+16*i;
  if (native_params_le32(d)==4 && native_params_le32(d+4)==0) {
   if (offset || native_params_le32(d+12)!=288) goto out;
   offset=native_params_le32(d+8);
  }
 }
 if (offset<1024 || offset>sizeof(seed)-288) goto out;
 if (fread(expected,1,sizeof(expected),pack)!=sizeof(expected) ||
     memcmp(expected,seed,sizeof(seed))) goto out;
 for (unsigned request=5;request<=96;request++) {
  memcpy(got,seed,sizeof(got));
  memset(p,0,sizeof(p));
  put(p,0,NATIVE_FRONT_PARAMS_MAGIC,4);put(p,4,1,2);put(p,6,64,2);put(p,8,request,8);
  for (unsigned i=0;i<9;i++)
   for (unsigned j=0;j<6;j++)
    values[i][j]=native_params_le32(seed+offset+32*i+4+4*j);
  if (native_front_params_apply(p,sizeof(p),values)) goto out;
  put(got,44,request,8);
  for (unsigned i=0;i<9;i++)
   for (unsigned j=0;j<6;j++)
    put(got,offset+32*i+4+4*j,values[i][j],4);
  if (fread(expected,1,sizeof(expected),pack)!=sizeof(expected) ||
      memcmp(got,expected,sizeof(got))) goto out;
  checked++;
 }
 if (fgetc(pack)!=EOF) goto out;
 printf("{\"status\":\"PASS_TYPED_KERNEL_PACKER_PRIVATE_FIXTURE_EQUALITY\","
        "\"requests_checked\":%u,\"raw_bytes_exported\":0}\n",checked);
 rc=0;
out:
 if (f) fclose(f);
 if (pack) fclose(pack);
 memset(seed,0,sizeof(seed));memset(got,0,sizeof(got));memset(expected,0,sizeof(expected));
 return rc;
}
