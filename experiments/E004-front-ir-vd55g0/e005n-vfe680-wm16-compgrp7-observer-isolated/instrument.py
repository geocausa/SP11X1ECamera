#!/usr/bin/env python3
from pathlib import Path
import sys

b=Path(sys.argv[1])

def inject(fn, old, new):
    p=b/fn
    s=p.read_text()
    if s.count(old) != 1:
        raise SystemExit(f"E005N_INSTRUMENT_FAIL {fn} anchor-count={s.count(old)}")
    p.write_text(s.replace(old,new,1))

inject("camss.c",
       "static int camss_x1e_pix_runner_validate(struct camss *camss,",
       '#include "camss-e004nr-rear-profile.inc"\n\nstatic int camss_x1e_pix_runner_validate(struct camss *camss,')
inject("camss-csid-680.c",
       "static void __csid_configure_top(struct csid_device *csid)",
       '#include "camss-csid-e004ns-rear-ipp.inc"\n\nstatic void __csid_configure_top(struct csid_device *csid)')
inject("camss-vfe-680.c",
       "static int vfe680_x1e_group_from_event(u32 event_id)",
       '#include "camss-vfe-e004nt-rear-4k-buffer.inc"\n'
       '#include "camss-vfe-e004nu-rear-ten-wm.inc"\n'
       '#include "camss-vfe-e004nv-rear-six-group.inc"\n\n'
       "static int vfe680_x1e_group_from_event(u32 event_id)")

inject("camss-vfe.h",
       "#include <linux/clk.h>\n",
       "#include <linux/atomic.h>\n#include <linux/clk.h>\n")
inject("camss-vfe.h",
       "\tstruct device_link *genpd_link;\n",
       "\tstruct device_link *genpd_link;\n"
       "\t/* E005n telemetry only: never a software-buffer retirement token. */\n"
       "\tatomic64_t x1e_e005n_wm16_comp7_count;\n"
       "\tu32 x1e_e005n_wm16_last_bus0;\n"
       "\tu32 x1e_e005n_wm16_last_consumed;\n")
inject("camss-vfe.c",
       "\tspin_lock_init(&vfe->output_lock);\n",
       "\tspin_lock_init(&vfe->output_lock);\n"
       "\tatomic64_set(&vfe->x1e_e005n_wm16_comp7_count, 0);\n"
       "\tWRITE_ONCE(vfe->x1e_e005n_wm16_last_bus0, 0);\n"
       "\tWRITE_ONCE(vfe->x1e_e005n_wm16_last_consumed, 0);\n")
inject("camss-vfe-680.c",
       "/*\n * vfe_isr - VFE module interrupt handler\n",
       '#include "camss-vfe-e005n-wm16-observer.inc"\n\n'
       "/*\n * vfe_isr - VFE module interrupt handler\n")

old="""static irqreturn_t vfe_isr(int irq, void *dev)
{
	return IRQ_HANDLED;
}
"""
new="""static irqreturn_t vfe_isr(int irq, void *dev)
{
	struct vfe_device *vfe = dev;
	u32 top0, top1, bus0, bus1;

	top0 = readl_relaxed(vfe->base + VFE_TOP_IRQn_STATUS(vfe, 0));
	top1 = readl_relaxed(vfe->base + VFE_TOP_IRQn_STATUS(vfe, 1));
	bus0 = readl_relaxed(vfe->base + VFE_BUS_IRQn_STATUS(vfe, 0));
	bus1 = readl_relaxed(vfe->base + VFE_BUS_IRQn_STATUS(vfe, 1));

	vfe680_e005n_observe_wm16(vfe, bus0);
	vfe680_e005n_ack_snapshot(vfe, top0, top1, bus0, bus1);

	return IRQ_HANDLED;
}
"""
inject("camss-vfe-680.c", old, new)
print("E005N_FIX1_ISOLATED_COPY_INSTRUMENTED")
