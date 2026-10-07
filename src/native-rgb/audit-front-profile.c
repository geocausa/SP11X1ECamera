/* SPDX-License-Identifier: GPL-2.0-only
 * Private on-target comparison; reports only derived counts, never profile data.
 */
#include <stdio.h>
#include <stdlib.h>
#include <openssl/sha.h>
#include "native-front-profile.h"
static unsigned checks;
static void need(int condition) { checks++; if (!condition) abort(); }
static void read_exact(const char *name, u8 *data, size_t size)
{
 FILE *f = fopen(name, "rb"); need(f != NULL);
 need(fread(data,1,size,f)==size); need(fgetc(f)==EOF); need(fclose(f)==0);
}
int main(int argc, char **argv)
{
 u8 *fw = malloc(NATIVE_FRONT_PROFILE_BYTES);
 u8 *original = malloc(NATIVE_FRONT_PROFILE_CAPSULE_BYTES);
 u8 *out = malloc(NATIVE_FRONT_PROFILE_CAPSULE_BYTES);
 u8 digest[32], good_digest[32];
 need(argc==3 && fw && original && out);
 read_exact(argv[1],fw,NATIVE_FRONT_PROFILE_BYTES);
 read_exact(argv[2],original,NATIVE_FRONT_PROFILE_CAPSULE_BYTES);
 need(SHA256(fw,NATIVE_FRONT_PROFILE_BYTES,digest)!=NULL);
 memcpy(good_digest,digest,32);
 need(native_front_profile_materialize(fw,NATIVE_FRONT_PROFILE_BYTES,digest,
       out,NATIVE_FRONT_PROFILE_CAPSULE_BYTES)==0);
 need(memcmp(out,original,NATIVE_FRONT_PROFILE_CAPSULE_BYTES)==0);
 /* Corrupt every fixed identity field, representative scalars and the entire
  * table region boundary. The fresh hash must fail before output mutation.
  */
 for (size_t i=0;i<NATIVE_FRONT_PROFILE_BYTES;i+=137) {
  fw[i]^=1; memset(out,0xa7,NATIVE_FRONT_PROFILE_CAPSULE_BYTES);
  need(SHA256(fw,NATIVE_FRONT_PROFILE_BYTES,digest)!=NULL);
  need(native_front_profile_materialize(fw,NATIVE_FRONT_PROFILE_BYTES,digest,
        out,NATIVE_FRONT_PROFILE_CAPSULE_BYTES)==-EKEYREJECTED);
  for (size_t n=0;n<NATIVE_FRONT_PROFILE_CAPSULE_BYTES;n++)
   need(out[n]==0xa7);
  fw[i]^=1;
 }
 memset(out,0xa7,NATIVE_FRONT_PROFILE_CAPSULE_BYTES);
 need(native_front_profile_materialize(fw,NATIVE_FRONT_PROFILE_BYTES-1,good_digest,
       out,NATIVE_FRONT_PROFILE_CAPSULE_BYTES)==-EINVAL);
 need(native_front_profile_materialize(fw,NATIVE_FRONT_PROFILE_BYTES,good_digest,
       out,NATIVE_FRONT_PROFILE_CAPSULE_BYTES-1)==-EINVAL);
 need(native_front_profile_materialize(fw,NATIVE_FRONT_PROFILE_BYTES,NULL,
       out,NATIVE_FRONT_PROFILE_CAPSULE_BYTES)==-EINVAL);
 need(native_front_profile_materialize(fw,NATIVE_FRONT_PROFILE_BYTES,good_digest,
       fw,NATIVE_FRONT_PROFILE_CAPSULE_BYTES)==-EINVAL);
 for (size_t n=0;n<NATIVE_FRONT_PROFILE_CAPSULE_BYTES;n++) need(out[n]==0xa7);
 /* Even a mistakenly reused digest cannot bypass structural admission. */
 for (size_t p=0;p<64;p++) {
  fw[p]^=1;
  need(native_front_profile_validate(fw,NATIVE_FRONT_PROFILE_BYTES,good_digest)==-EINVAL);
  fw[p]^=1;
 }
 printf("PASS_DATA_ONLY_PROFILE_RECONSTRUCTION checks=%u corruption_cases=%u exact_original_match=1\n",
        checks,(unsigned)((NATIVE_FRONT_PROFILE_BYTES+136)/137));
 free(out); free(original); free(fw); return 0;
}
