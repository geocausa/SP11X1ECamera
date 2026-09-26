/* SPDX-License-Identifier: MIT */
/*
 * E007p clean rear TMC141 family-2 producer.
 *
 * Source locked to the pinned same-SP11 QcDeviceMFT8380.dll TMC141 path:
 *   CalculateAnchorKneePoints 0x1809255f0
 *   seven-point generator     0x180926570
 *   cubic coefficient helper  0x1809276e8
 *
 * The small pow helper below is a clean translation of the normal,
 * positive-finite ARM64 math path used by that solver.  The lookup and
 * polynomial constants are math implementation constants, not camera
 * captures or request payload values.
 */
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define E007P_MODE_REAR_4K 0x00060800u
#define E007P_TUNE_FLOATS_MIN 0x46u
#define E007P_OK 0
#define E007P_EINVAL (-22)
#define E007P_ENOTSUP (-95)

struct e007p_tmc141_input {
    float runtime_0c;
    float runtime_18;
    float runtime_480;
    float runtime_488;
    float runtime_48c;
    float common_64;
    uint32_t mode;
    uint32_t curve_order;
    uint32_t ctrl_8234;
    uint32_t ctrl_8238;
    uint32_t ctrl_8244;
    uint32_t ctrl_8254;
    uint32_t face_count;
};

static const uint64_t e007p_exp_tab[32] = {
    0x3ff0000000000000ULL,0x3fefd9b0d3158574ULL,0x3fefb5586cf9890fULL,0x3fef9301d0125b51ULL,0x3fef72b83c7d517bULL,0x3fef54873168b9aaULL,0x3fef387a6e756238ULL,0x3fef1e9df51fdee1ULL,0x3fef06fe0a31b715ULL,0x3feef1a7373aa9cbULL,0x3feedea64c123422ULL,0x3feece086061892dULL,0x3feebfdad5362a27ULL,0x3feeb42b569d4f82ULL,0x3feeab07dd485429ULL,0x3feea47eb03a5585ULL,0x3feea09e667f3bcdULL,0x3fee9f75e8ec5f74ULL,0x3feea11473eb0187ULL,0x3feea589994cce13ULL,0x3feeace5422aa0dbULL,0x3feeb737b0cdc5e5ULL,0x3feec49182a3f090ULL,0x3feed503b23e255dULL,0x3feee89f995ad3adULL,0x3feeff76f2fb5e47ULL,0x3fef199bdd85529cULL,0x3fef3720dcef9069ULL,0x3fef5818dcfba487ULL,0x3fef7c97337b9b5fULL,0x3fefa4afa2a490daULL,0x3fefd0765b6e4540ULL
};

static const double e007p_log_tab[16][2] = {
    {1.398907162146528,-15.497607099612695},{1.3403141896637998,-13.522279346942305},{1.286432210124115,-11.62801391255538},{1.2367150214269895,-9.808419061569785},{1.1906977166711752,-8.057830451372043},{1.1479821020556429,-6.37120478201426},{1.1082251448272158,-4.744032199450117},{1.0711297413057381,-3.1722636183418853},{1.036437278977283,-1.652250015284142},{1.0,0.0},{0.9492859795739057,2.4027302201417613},{0.8951049428609004,5.115880313828194},{0.8476821620351103,7.6289493258165795},{0.8050314851692001,10.012252353876242},{0.7664671008843108,12.27853525006502},{0.731428603316328,14.43875356594608}
};

static const double e007p_log_poly[5] = {
    9.230642595494848,-11.549633993508213,15.388751407122465,-23.08311896002013,46.16624130807789
};

static const double e007p_exp_poly[3] = {
    1.6938359250920212e-06,0.00023459809789509004,0.021660849396613134
};

static uint32_t e007p_float_bits(float x)
{
    uint32_t u;
    memcpy(&u, &x, sizeof(u));
    return u;
}

static float e007p_bits_float(uint32_t u)
{
    float x;
    memcpy(&x, &u, sizeof(x));
    return x;
}

static double e007p_bits_double(uint64_t u)
{
    double x;
    memcpy(&x, &u, sizeof(x));
    return x;
}

static float e007p_const(uint32_t u)
{
    return e007p_bits_float(u);
}

/* Positive, normal finite domain used by TMC141. */
static float e007p_powf_pos(float x, float y)
{
    uint32_t xb = e007p_float_bits(x);
    uint32_t z = xb - 0x3f330000u;
    uint32_t ew = z & 0xff800000u;
    unsigned k = (z >> 19) & 15u;
    uint32_t mb = xb - ew;
    float mf = e007p_bits_float(mb);
    double r = fma(e007p_log_tab[k][0], (double)mf, -1.0);
    int32_t es = ((int32_t)ew) >> 18;
    double r2 = r * r;
    double lg = fma(e007p_log_poly[4], r,
                    e007p_log_tab[k][1] + (double)es);
    double q = fma(e007p_log_poly[2], r, e007p_log_poly[3]);
    lg = fma(q, r2, lg);
    q = fma(e007p_log_poly[0], r, e007p_log_poly[1]);
    lg = fma(q, r2 * r2, lg);

    double v = lg * (double)y;
    double rn = round(v); /* ARM64 FRINTA semantics for finite TMC inputs. */
    int32_t n = (int32_t)rn;
    double fr = v - rn;
    uint64_t eb = e007p_exp_tab[((uint32_t)n) & 31u] +
                  (((uint64_t)(int64_t)n) << 47);
    double poly = fma(fr, e007p_exp_poly[2], 1.0);
    poly = fma(fma(fr, e007p_exp_poly[0], e007p_exp_poly[1]),
               fr * fr, poly);
    return (float)(e007p_bits_double(eb) * poly);
}

static float e007p_min(float a, float b) { return a <= b ? a : b; }
static float e007p_max(float a, float b) { return a > b ? a : b; }

static unsigned e007p_scale_index(float runtime_0c)
{
    const float step = e007p_const(0x3f83d70au);
    float q = logf(runtime_0c) / logf(step);
    float z = roundf(q); /* source-locked FRINTA then FCVTZU */
    unsigned i = z <= 0.0f ? 0u : (unsigned)z;
    return i > 235u ? 235u : i;
}

static void e007p_base(float exponent, float scale, float maxv,
                       const float *p, float src[7], float dst[7])
{
    const float eps = e007p_const(0x38d1b717u);
    const float caps[5] = {
        e007p_const(0x3f7fdf3bu), e007p_const(0x3f7fe5c9u),
        e007p_const(0x3f7fec57u), e007p_const(0x3f7ff2e5u),
        e007p_const(0x3f7ff972u)
    };

    src[0] = 0.0f;
    src[1] = e007p_max(eps, e007p_min(p[0] / maxv, caps[0]));
    src[2] = e007p_max(src[1] + eps,
                       e007p_min(p[1] / scale, caps[1]));
    for (int i = 2; i < 5; ++i)
        src[i + 1] = e007p_max(src[i] + eps,
                               e007p_min(p[i], caps[i]));
    src[6] = 1.0f;

    dst[0] = 0.0f;
    dst[1] = e007p_max(eps,
              e007p_min(e007p_powf_pos(maxv, exponent) * src[1], caps[0]));
    dst[2] = e007p_max(dst[1] + eps,
              e007p_min(e007p_powf_pos(scale, exponent) * src[2], caps[1]));
    for (int i = 3; i < 6; ++i)
        dst[i] = e007p_max(dst[i - 1] + eps,
                           e007p_min(src[i], caps[i - 1]));
    dst[6] = 1.0f;
}

static void e007p_global_src(const float *t, float runtime_480,
                             float runtime_48c, float src[7])
{
    const float one = 1.0f;
    const float eps = e007p_const(0x38d1b717u);
    const float cap1 = e007p_const(0x3f7fdf3bu);
    const float cap2 = e007p_const(0x3f7fe5c9u);

    float alpha = t[0x2d] + t[0x2c];
    alpha = e007p_min(one, e007p_max(0.0f, alpha));

    float ratio = t[0x29] / runtime_48c;
    float limited = e007p_min(ratio, t[0x2a]);
    float base = one;
    if (one < ratio)
        base = limited;

    float mixed = base * (one - t[0x2b]);
    mixed = mixed + t[0x2b] * one;

    float p = e007p_powf_pos(mixed, t[2]);
    float factor = (one / p) * alpha;
    factor = factor + (one - alpha);

    float v1 = e007p_min(factor * src[1], cap1);
    v1 = e007p_max(src[0] + eps, v1);
    float v2 = e007p_min(factor * src[2], cap2);
    v2 = e007p_max(v1 + eps, v2);

    float inv = one / e007p_powf_pos(runtime_480, t[3]);
    v1 = e007p_min(inv * v1, cap1);
    v1 = e007p_max(src[0] + eps, v1);
    v2 = e007p_min(inv * v2, cap2);
    v2 = e007p_max(v1 + eps, v2);

    src[1] = v1;
    src[2] = v2;
}

static void e007p_rear_mode_src(float runtime_488, float tune_a0,
                                float tune_0c, float src[7])
{
    const float one = 1.0f;
    const float eps = e007p_const(0x38d1b717u);
    const float cap1 = e007p_const(0x3f7fdf3bu);
    const float cap2 = e007p_const(0x3f7fe5c9u);

    /* In the exercised global path fVar51 carries cap2 into this branch. */
    float blend = runtime_488 * tune_a0;
    blend = blend + (one - tune_a0) * cap2;
    blend = e007p_min(8.0f, e007p_max(one, blend));

    float inv = one / e007p_powf_pos(blend, tune_0c);
    float v1 = e007p_min(inv * src[1], cap1);
    v1 = e007p_max(src[0] + eps, v1);
    float v2 = e007p_min(inv * src[2], cap2);
    v2 = e007p_max(v1 + eps, v2);
    src[1] = v1;
    src[2] = v2;
}

static int e007p_coeff(const float x[7], const float y[7], float out[15])
{
    float dx[6], sec[6], m[6];

    for (int i = 0; i < 6; ++i) {
        dx[i] = x[i + 1] - x[i];
        sec[i] = (y[i + 1] - y[i]) / dx[i];
    }

    float c = ((dx[0] + dx[0] + dx[1]) * sec[0] -
               dx[0] * sec[1]) / (dx[0] + dx[1]);
    float z = 0.0f;
    if (((sec[0] * sec[1] >= 0.0f) ||
         (fabsf(c) <= fabsf(sec[0] * 3.0f))) &&
        sec[0] * c >= 0.0f)
        z = c;
    m[0] = z;

    for (int i = 1; i < 5; ++i) {
        float a = dx[i - 1] + dx[i - 1] + dx[i];
        float b = dx[i] + dx[i] + dx[i - 1];
        m[i] = (a + b) / (a / sec[i] + b / sec[i - 1]);
    }

    c = ((dx[5] + dx[5] + dx[4]) * sec[5] -
         dx[5] * sec[4]) / (dx[5] + dx[4]);
    z = 0.0f;
    if (((sec[5] * sec[4] >= 0.0f) ||
         (fabsf(c) <= fabsf(sec[5] * 3.0f))) &&
        sec[5] * c >= 0.0f)
        z = c;
    m[5] = z;

    int o = 0;
    for (int i = 1; i < 6; ++i) {
        float h = dx[i], s = sec[i], mi = m[i];
        float mj = i < 5 ? m[i + 1] : m[5];
        out[o++] = mi;
        out[o++] = ((s * 3.0f - (mi + mi)) - mj) / h;
        out[o++] = (((mi - (s + s)) + mj) / h) / h;
    }
    return E007P_OK;
}

int e007p_tmc141_solve(const float *tune, size_t tune_floats,
                       const struct e007p_tmc141_input *in,
                       float src[7], float dst[7], float coeff[15],
                       unsigned *scale_index)
{
    if (!tune || !in || !src || !dst || !coeff ||
        tune_floats < E007P_TUNE_FLOATS_MIN)
        return E007P_EINVAL;

    if (in->mode != E007P_MODE_REAR_4K ||
        in->curve_order != 5u ||
        in->ctrl_8234 != 0u ||
        in->ctrl_8238 != 0u ||
        in->ctrl_8254 != 0u ||
        in->ctrl_8244 > 1u ||
        in->face_count != 0u)
        return E007P_ENOTSUP;

    for (unsigned i = 0x3f; i <= 0x45; ++i)
        if (tune[i] != 0.0f)
            return E007P_ENOTSUP;

    if (!(in->runtime_0c > 0.0f) ||
        !(in->runtime_480 > 0.0f) ||
        !isfinite(in->runtime_48c) || in->runtime_48c < 0.0f ||
        !(in->common_64 > 0.0f))
        return E007P_EINVAL;

    unsigned idx = e007p_scale_index(in->runtime_0c);
    float scale = e007p_powf_pos(e007p_const(0x3f83d70au), (float)idx);
    float maxv = (in->runtime_18 - 1.0f) * tune[9];
    maxv = maxv + 1.0f;
    maxv = maxv + tune[10];
    maxv = e007p_min(1023.0f, e007p_max(1.0f, maxv));
    maxv = maxv * scale;
    if (in->common_64 <= maxv)
        maxv = in->common_64;

    e007p_base(tune[0], scale, maxv, tune + 27, src, dst);
    e007p_global_src(tune, in->runtime_480, in->runtime_48c, src);
    if (in->ctrl_8244 == 1u)
        e007p_rear_mode_src(in->runtime_488, tune[0x28], tune[3], src);

    e007p_coeff(src, dst, coeff);
    if (scale_index)
        *scale_index = idx;
    return E007P_OK;
}
