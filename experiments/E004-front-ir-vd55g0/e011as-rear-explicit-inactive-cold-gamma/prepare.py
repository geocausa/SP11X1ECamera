#!/usr/bin/env python3
"""One-use additive derivatives of clean Linux providers; no originals changed."""
from pathlib import Path
import hashlib,json,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
PARENT="e73c4ff38221a28b4bf7995581e756a1f607a9a1"
def replace(s,a,b):
    assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def main():
    subprocess.run(["bash","tools/camera-overlap-guard.sh","--require-golden",
        "--require-no-camera-process","--expect-head",PARENT,"--expect-origin",PARENT],cwd=ROOT,check=True)
    names=("camss-e006g-rear-materializer.inc","camss-e007e-bfstats25-dmi.inc",
        "camss-e007f-dmi-integration.inc","camss-vfe-e008o-rear-semantic-state.inc")
    # Locate by exact source filename, never by a stale experiment directory.
    inputs=[]
    for name in names:
        found=list(EX.glob("*/"+name));assert len(found)==1,(name,found);inputs.append(found[0])
    assert not (HERE/"PROVIDERS.json").exists(),"consumed preparer; do not overwrite"
    sources=[p.read_text() for p in inputs]
    g,e,f,o=sources
    g=replace(g,"\tbool materialized;","\tbool bf_gamma_materialized;\n\tbool materialized;")
    g=replace(g,"static int e006g_rear_prepare_dynamic(","static int e011as_rear_prepare_dynamic_selected(")
    g=replace(g,"\t\t\t\t      struct e006g_rear_dynamic_payloads *out)","\t\t\t\t      struct e006g_rear_dynamic_payloads *out,\n\t\t\t\t      bool gamma_active)")
    g=replace(g,"\tret = ops->lsc(ctx, 1, out->lsc1, sizeof(out->lsc1));\n\tif (ret)\n\t\treturn ret;",
        "\tmemset(out, 0, sizeof(*out));\n\tret = ops->lsc(ctx, 1, out->lsc1, sizeof(out->lsc1));\n\tif (ret)\n\t\tgoto err_zero;")
    g=replace(g,"\tret = ops->bfstats(ctx, 2, out->bf_gamma, sizeof(out->bf_gamma));\n\tif (ret)\n\t\tgoto err_zero;",
        "\tif (gamma_active) {\n\t\tret = ops->bfstats(ctx, 2, out->bf_gamma, sizeof(out->bf_gamma));\n\t\tif (ret)\n\t\t\tgoto err_zero;\n\t\tout->bf_gamma_materialized = true;\n\t}")
    marker="static int e006g_rear_fill_slot("
    wrapper="""/* Legacy generic callers still require an active gamma provider. */
static int e006g_rear_prepare_dynamic(const struct e006g_rear_producer_ops *ops,
				      void *ctx,
				      struct e006g_rear_dynamic_payloads *out)
{
	return e011as_rear_prepare_dynamic_selected(ops, ctx, out, true);
}

"""
    g=replace(g,marker,wrapper+marker)
    g=replace(g,"\tcase E006G_PAYLOAD_BF_GAMMA:\n\t\tsrc = dyn->bf_gamma;",
        "\tcase E006G_PAYLOAD_BF_GAMMA:\n\t\tif (!dyn->bf_gamma_materialized)\n\t\t\treturn -EOPNOTSUPP;\n\t\tsrc = dyn->bf_gamma;")
    e=replace(e,"\tbool gamma_valid;","\tbool gamma_valid;\n\tbool gamma_inactive; /* explicit absence, never a dummy table */")
    e=replace(e,"\tif (!s->gamma_valid)","\tif (s->gamma_inactive || !s->gamma_valid)")
    f=replace(f,"\tif (!s->bfstats25.gamma_valid)\n\t\treturn -EOPNOTSUPP;",
        """	if (s->bfstats25.gamma_inactive) {
		unsigned int i;

		if (s->bfstats25.gamma_valid)
			return -EINVAL;
		for (i = 0; i < E007E_BF_GAMMA_COUNT; i++)
			if (s->bfstats25.gamma[i])
				return -EINVAL;
	} else if (!s->bfstats25.gamma_valid) {
		return -EOPNOTSUPP;
	}""")
    f=replace(f,"return e006g_rear_prepare_dynamic(&e007f_rear_dmi_ops, s, out);",
        "return e011as_rear_prepare_dynamic_selected(&e007f_rear_dmi_ops, s,\n\t\t\t\t\t\t   out, !s->bfstats25.gamma_inactive);")
    o=replace(o,"\tint ret;\n\n\tif (!s || packet", "\tstruct e007e_bf_dmi_state *bf;\n\tint ret;\n\n\tif (!s || packet")
    o=replace(o,"\tif (s->request_id < 4)\n\t\treturn -EINVAL;",
        """	if (s->request_id < 4)
		return -EINVAL;
	bf = &s->dmi.dmi.dmi.dmi.dmi.dmi.dmi.bfstats25;
	/* Source-locked startup policy: cold inactive, normal active. */
	if (!packet) {
		if (s->regs.bfstats.gamma_lut_enable ||
		    !bf->gamma_inactive || bf->gamma_valid)
			return -EPROTO;
	} else if (s->regs.bfstats.gamma_lut_enable != 1 ||
		   bf->gamma_inactive || !bf->gamma_valid) {
		return -EPROTO;
	}""")
    manifest=[]
    for p,s in zip(inputs,(g,e,f,o)):
        name="camss-e011as-"+p.name.removeprefix("camss-")
        dst=HERE/name;assert not dst.exists(),"partial prepared identity; audit"
        s="/* E011AS additive inactive-gamma derivative; see PROVIDERS.json. */\n"+s
        dst.write_text(s)
        manifest.append({"parent_path":str(p.relative_to(ROOT)),"parent_sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
            "path":str(dst.relative_to(ROOT)),"sha256":hashlib.sha256(dst.read_bytes()).hexdigest(),"old_name":p.name,"new_name":name})
    (HERE/"PROVIDERS.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print("E011AS four explicit-inactive derivatives prepared; no hardware actions")
if __name__=="__main__":main()
