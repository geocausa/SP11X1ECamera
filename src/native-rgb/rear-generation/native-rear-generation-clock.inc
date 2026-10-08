/* SPDX-License-Identifier: GPL-2.0-only */
/* Candidate-only NoC floor through CCF. Rear owner and PM are held.
 * RT/NRT share the source: validate both handles/rates before setting either.
 * Caller has completed packet0, WMs remain disabled and sensor is stopped.
 * Higher existing rates are preserved; no direct clock or imaging CSR writes.
 */
static int native_rear_generation_noc_floor(struct vfe_device *vfe)
{
 struct clk *rt = NULL, *nrt = NULL;
 unsigned long rt_rate, nrt_rate;
 long rt_round, nrt_round;
 int i;
 int ret;

 if (!vfe680_e004nt_rear_4k_target(vfe) || !vfe->base ||
     !vfe->clock || vfe->nclocks <= 0)
  return -EINVAL;
 for (i = 0; i < vfe->nclocks; i++) {
  struct camss_clock *c = &vfe->clock[i];

  if (!c->name)
   return -EINVAL;
  if (!strcmp(c->name, "camnoc_rt_axi")) {
   if (rt || IS_ERR_OR_NULL(c->clk))
    return -EINVAL;
   rt = c->clk;
  } else if (!strcmp(c->name, "camnoc_nrt_axi")) {
   if (nrt || IS_ERR_OR_NULL(c->clk))
    return -EINVAL;
   nrt = c->clk;
  }
 }
 if (!rt || !nrt)
  return -EINVAL;
 rt_rate = clk_get_rate(rt);
 nrt_rate = clk_get_rate(nrt);
 if (rt_rate != nrt_rate)
  return -EPROTO;
 if (rt_rate >= 240000000UL)
  return 0;
 rt_round = clk_round_rate(rt, 240000000UL);
 nrt_round = clk_round_rate(nrt, 240000000UL);
 if (rt_round < 0)
  return rt_round;
 if (nrt_round < 0)
  return nrt_round;
 if (rt_round != 240000000L || nrt_round != 240000000L)
  return -EPROTO;
 ret = clk_set_rate(rt, 240000000UL);
 if (ret)
  return ret;
 rt_rate = clk_get_rate(rt);
 nrt_rate = clk_get_rate(nrt);
 if (rt_rate != 240000000UL || nrt_rate != rt_rate)
  return -EIO;
 dev_info(vfe->camss->dev,
          "NATIVE_REAR_GENERATION_NOC rt=%lu nrt=%lu floor=240000000\n",
          rt_rate, nrt_rate);
 return 0;
}
