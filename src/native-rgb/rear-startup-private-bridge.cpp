#include "camss_x1e_helpers.h"
#include <cstdint>
extern "C" int sp11_generate_rear_scalar_envelope(
 const e012k_rear_scalar_input *in,const uint64_t *ids,
 native_rear_startup_scalars *out)
{
 return libcamera::ipa::camssX1ERearStartupScalars({in,4},{ids,4},out);
}
extern "C" int sp11_generate_rear_af(float zoom,uint16_t *out)
{
 using namespace libcamera;using namespace libcamera::ipa;
 CamssX1ERearAfInput input{Size(4064,2286),0.25f,0.25f,1.0f,zoom,1.0f,1.0f,false,false,false};
 Rectangle pending;
 int ret=camssX1ERearAfRectangle(input,&pending);
 if(ret)return ret;
 out[0]=pending.x;out[1]=pending.y;out[2]=pending.width;out[3]=pending.height;return 0;
}
extern "C" int sp11_generate_rear_weights(const float *in,bool quad,uint8_t *out)
{
 libcamera::ipa::CamssX1ERearBgControls pending{};
 int ret=libcamera::ipa::camssX1ERearBgWeights({in,3},quad,&pending);
 if(ret)return ret;
 for(unsigned i=0;i<3;i++)out[i]=pending.aecWeightQ4[i];
 out[3]=pending.awbQuad;return 0;
}
