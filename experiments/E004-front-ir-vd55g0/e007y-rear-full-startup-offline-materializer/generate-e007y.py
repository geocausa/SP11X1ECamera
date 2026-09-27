#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, json, struct

D=Path(__file__).resolve().parent
R=D.parents[2]
RECIPE=R/"experiments/E004-front-ir-vd55g0/e006k-rear-startup-main-symbolic-recipe/STARTUP-SYMBOLIC-RECIPE.json"
OP={"DMI":1,"REG_CONT":3,"DMI_32":10,"DMI_64":11}

def u32(v): return int(v,16) if isinstance(v,str) else int(v)
def sha(b): return hashlib.sha256(b).hexdigest()

def skeleton(v):
    out=bytearray()
    for c in v["commands"]:
        typ=c["command"]
        if typ=="REG_CONT":
            n=int(c["count"])
            out += struct.pack("<II",(3<<24)|n,u32(c["register_offset"]))
            out += bytes(4*n)
        elif typ in ("DMI","DMI_32","DMI_64"):
            op=OP[typ]; n=int(c["payload_bytes"]); mid=int(c["header_middle_byte"])
            reg=u32(c["dmi_register_offset"]); sel=int(c["selector"])
            out += struct.pack("<III",(op<<24)|(mid<<16)|(n-1),0,(sel<<24)|reg)
        else:
            raise AssertionError(typ)
    assert len(out)==int(v["main_bytes"])
    assert sha(out)==v["all_symbolic_normalized_sha256"], (v["capture_n"],sha(out),v["all_symbolic_normalized_sha256"])
    return bytes(out)

def cbytes(name,b):
    lines=[f"static const u8 {name}[] = {{"]
    for i in range(0,len(b),16):
        lines.append(chr(9)+", ".join(f"0x{x:02x}" for x in b[i:i+16])+",")
    lines.append("};")
    return chr(10).join(lines)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("-o","--output",type=Path,required=True)
    ap.add_argument("--safe",type=Path,required=True)
    a=ap.parse_args()
    j=json.loads(RECIPE.read_text())
    vs=sorted(j["variants"].items(),key=lambda kv:int(kv[1]["capture_n"]))
    assert [int(v["capture_n"]) for _,v in vs]==[0,1,2,3]
    arrays=[]; meta=[]; union=set()
    for label,v in vs:
        b=skeleton(v); dmis=[]
        for c in v["commands"]:
            if c["command"] in ("DMI","DMI_32","DMI_64"):
                ident=(u32(c["dmi_register_offset"]),int(c["selector"]),int(c["payload_bytes"]))
                dmis.append(ident); union.add(ident)
        arrays.append(cbytes(f"e007y_startup_skeleton_{int(v['capture_n'])}",b))
        meta.append((len(b),len(dmis),f"e007y_startup_skeleton_{int(v['capture_n'])}",v["all_symbolic_normalized_sha256"],label))
    expected_union={
      (0x3d08,1,512),(0x4308,1,884),(0x4308,2,884),(0x4308,3,884),
      (0x4708,1,512),(0x4908,1,256),(0x5a08,1,2048),
      (0x5f08,1,1024),(0x5f08,2,1024),(0x5f08,3,1024),
      (0xa008,1,768),(0xa008,2,768),(0xa208,1,384),(0xa208,2,384),
      (0xb208,1,4096),(0xb208,2,80),(0xbc08,1,300),(0xbc08,2,128),
    }
    assert union==expected_union,(union^expected_union)

    pre=r'''/* SPDX-License-Identifier: MIT */
/*
 * E007y complete rear startup OFFLINE materializer.
 *
 * Structure authority: E006k symbolic rear startup MAIN recipes plus the E005z/
 * E006a rear block-list topology. Register values flow only through E007d/E007w.
 * DMI payloads flow only through E007v plus E007x for the startup-only BHist
 * zero pair. DMI addresses and BL addresses are caller-supplied Linux-owned
 * 32-bit IOVAs.
 *
 * This include allocates nothing and submits nothing. It contains no probe,
 * module-init, stream, MMIO, FIFO, RT-CDM submit or firmware path.
 */

#define E007Y_STARTUP_PACKETS 4
#define E007Y_MAX_BL 6
#define E007Y_WRAPPER_BYTES 0x100
#define E007Y_WRAPPER_VFE_OFF 0x00
#define E007Y_WRAPPER_EXTRA_OFF 0x20
#define E007Y_WRAPPER_CSID_OFF 0x40
#define E007Y_WRAPPER_COMPANION_OFF 0x80
#define E007Y_WRAPPER_IRQ_OFF 0xc0

#define E007Y_CDM_CHANGE_VFE1 0x0800f000U
#define E007Y_CDM_CHANGE_CSID1 0x08057000U
#define E007Y_CDM_REG_CONT_1 0x03000001U
#define E007Y_CDM_REG_CONT_2 0x03000002U
#define E007Y_CDM_REG_RANDOM_1 0x04000001U
#define E007Y_CDM_GEN_IRQ 0x06000000U

#define E007Y_REAR_WM16_IMAGE_CFG0 0x00190004U
#define E007Y_REAR_IPP_PARITY_ZERO1 0x02000000U
#define E007Y_REAR_IPP_IRQ_PATTERN 0x00000001U
#define E007Y_REAR_IPP_IRQ_PERIOD 0x00000000U
#define E007Y_REAR_IPP_HCROP 0x0fdf0000U
#define E007Y_REAR_IPP_VCROP 0x08ed0000U
#define E007Y_REAR_IPP_FORMAT_CFG0 0x0000001fU
#define E007Y_REAR_IPP_FORMAT_CFG1 0x08ee0fe0U
#define E007Y_REAR_RUP_AUP_VALUE 0x01f501f5U

#define E007Y_OPCODE_DMI 1
#define E007Y_OPCODE_REG_CONT 3
#define E007Y_OPCODE_DMI_32 10
#define E007Y_OPCODE_DMI_64 11

struct e007y_rear_dmi_target {
	u8 *cpu;
	size_t bytes;
	u32 dma;
};

struct e007y_rear_bl_ref {
	u32 dma;
	u16 bytes;
};

struct e007y_rear_startup_output {
	u8 *main;
	size_t main_bytes;
	u32 main_dma;
	struct e007y_rear_dmi_target *dmi;
	size_t dmi_count;
	struct e006g_rear_dynamic_payloads *dynamic;
	u8 *wrapper;
	size_t wrapper_bytes;
	u32 wrapper_dma;
	struct e007y_rear_bl_ref bl[E007Y_MAX_BL];
	u8 bl_count;
};

struct e007y_rear_startup_variant {
	u16 main_bytes;
	u8 dmi_count;
	const u8 *skeleton;
};
'''
    table=["static const struct e007y_rear_startup_variant e007y_startup_variants[] = {"]
    for mb,dc,n,h,label in meta:
        table.append(chr(9)+f'{{ .main_bytes = 0x{mb:x}, .dmi_count = {dc}, .skeleton = {n} }},')
    table.append("};")
    table.append("static_assert(ARRAY_SIZE(e007y_startup_variants) == E007Y_STARTUP_PACKETS);")

    post=r'''
static int
e007y_rear_slot(u16 reg, u8 selector, u16 bytes,
		struct e006g_rear_dmi_slot *slot, bool *bhist_startup)
{
	u8 kind;

	if (!slot || !bhist_startup)
		return -EINVAL;
	*bhist_startup = false;

	switch (reg) {
	case 0x3d08:
		if (selector != 1 || bytes != 512) return -EINVAL;
		kind = E006G_PAYLOAD_STABLE; break;
	case 0x4308:
		if (bytes != 884 || selector < 1 || selector > 3) return -EINVAL;
		kind = selector == 3 ? E006G_PAYLOAD_STABLE : E006G_PAYLOAD_LSC; break;
	case 0x4708:
		if (selector != 1 || bytes != 512) return -EINVAL;
		kind = E006G_PAYLOAD_LSC_GIC_ALIAS; break;
	case 0x4908:
		if (selector != 1 || bytes != 256) return -EINVAL;
		kind = E006G_PAYLOAD_STABLE; break;
	case 0x5a08:
		if (selector != 1 || bytes != 2048) return -EINVAL;
		kind = E006G_PAYLOAD_GTM; break;
	case 0x5f08:
		if (bytes != 1024 || selector < 1 || selector > 3) return -EINVAL;
		kind = E006G_PAYLOAD_STABLE; break;
	case 0xa008:
		if (bytes != 768 || selector < 1 || selector > 2) return -EINVAL;
		kind = E006G_PAYLOAD_STABLE; break;
	case 0xa208:
		if (bytes != 384 || selector < 1 || selector > 2) return -EINVAL;
		kind = E006G_PAYLOAD_STABLE; break;
	case 0xb208:
		if ((selector == 1 && bytes != 4096) ||
		    (selector == 2 && bytes != 80) ||
		    (selector != 1 && selector != 2))
			return -EINVAL;
		*bhist_startup = true;
		kind = E006G_PAYLOAD_STABLE;
		break;
	case 0xbc08:
		if (selector == 1 && bytes == 300)
			kind = E006G_PAYLOAD_BF_ROI;
		else if (selector == 2 && bytes == 128)
			kind = E006G_PAYLOAD_BF_GAMMA;
		else return -EINVAL;
		break;
	default:
		return -ENOENT;
	}
	slot->dmi_reg = reg;
	slot->selector = selector;
	slot->payload_bytes = bytes;
	slot->kind = kind;
	return 0;
}

static void e007y_rear_clear_output(struct e007y_rear_startup_output *out)
{
	size_t i;
	if (!out) return;
	if (out->main && out->main_bytes) memzero_explicit(out->main, out->main_bytes);
	if (out->wrapper && out->wrapper_bytes) memzero_explicit(out->wrapper, out->wrapper_bytes);
	if (out->dynamic) memzero_explicit(out->dynamic, sizeof(*out->dynamic));
	if (out->dmi)
		for (i = 0; i < out->dmi_count; i++)
			if (out->dmi[i].cpu && out->dmi[i].bytes)
				memzero_explicit(out->dmi[i].cpu, out->dmi[i].bytes);
	memset(out->bl, 0, sizeof(out->bl));
	out->bl_count = 0;
}

static int e007y_rear_wrapper(u8 packet, struct e007y_rear_startup_output *out)
{
	u8 *w;
	u32 dma;
	if (!out || packet >= E007Y_STARTUP_PACKETS ||
	    !out->wrapper || out->wrapper_bytes < E007Y_WRAPPER_BYTES ||
	    !out->wrapper_dma || (out->wrapper_dma & 3) ||
	    !out->main_dma || (out->main_dma & 3))
		return -EINVAL;
	w = out->wrapper; dma = out->wrapper_dma;
	memset(w, 0, E007Y_WRAPPER_BYTES);
	put_unaligned_le32(E007Y_CDM_CHANGE_VFE1, w + E007Y_WRAPPER_VFE_OFF);
	put_unaligned_le32(E007Y_CDM_CHANGE_CSID1, w + E007Y_WRAPPER_CSID_OFF);
	out->bl[0].dma = dma + E007Y_WRAPPER_VFE_OFF; out->bl[0].bytes = 4;
	out->bl[1].dma = out->main_dma; out->bl[1].bytes = out->main_bytes;

	if (!packet) {
		u8 *p = w + E007Y_WRAPPER_COMPANION_OFF;
		put_unaligned_le32(E007Y_CDM_REG_CONT_1, p + 0x00);
		put_unaligned_le32(0x00000330, p + 0x04);
		put_unaligned_le32(E007Y_REAR_IPP_PARITY_ZERO1, p + 0x08);
		put_unaligned_le32(E007Y_CDM_REG_CONT_2, p + 0x0c);
		put_unaligned_le32(0x0000037c, p + 0x10);
		put_unaligned_le32(E007Y_REAR_IPP_IRQ_PATTERN, p + 0x14);
		put_unaligned_le32(E007Y_REAR_IPP_IRQ_PERIOD, p + 0x18);
		put_unaligned_le32(E007Y_CDM_REG_CONT_2, p + 0x1c);
		put_unaligned_le32(0x0000035c, p + 0x20);
		put_unaligned_le32(E007Y_REAR_IPP_HCROP, p + 0x24);
		put_unaligned_le32(E007Y_REAR_IPP_VCROP, p + 0x28);
		put_unaligned_le32(E007Y_CDM_REG_CONT_2, p + 0x2c);
		put_unaligned_le32(0x00000384, p + 0x30);
		put_unaligned_le32(E007Y_REAR_IPP_FORMAT_CFG0, p + 0x34);
		put_unaligned_le32(E007Y_REAR_IPP_FORMAT_CFG1, p + 0x38);
		out->bl[2].dma = dma + E007Y_WRAPPER_CSID_OFF; out->bl[2].bytes = 4;
		out->bl[3].dma = dma + E007Y_WRAPPER_COMPANION_OFF; out->bl[3].bytes = 0x3c;
		out->bl_count = 4;
		return 0;
	}

	put_unaligned_le32(E007Y_CDM_REG_RANDOM_1, w + E007Y_WRAPPER_EXTRA_OFF + 0x0);
	put_unaligned_le32(0x00001e0c, w + E007Y_WRAPPER_EXTRA_OFF + 0x4);
	put_unaligned_le32(E007Y_REAR_WM16_IMAGE_CFG0, w + E007Y_WRAPPER_EXTRA_OFF + 0x8);
	put_unaligned_le32(E007Y_CDM_REG_CONT_2, w + E007Y_WRAPPER_COMPANION_OFF + 0x0);
	put_unaligned_le32(0x0000035c, w + E007Y_WRAPPER_COMPANION_OFF + 0x4);
	put_unaligned_le32(E007Y_REAR_IPP_HCROP, w + E007Y_WRAPPER_COMPANION_OFF + 0x8);
	put_unaligned_le32(E007Y_REAR_IPP_VCROP, w + E007Y_WRAPPER_COMPANION_OFF + 0xc);
	put_unaligned_le32(E007Y_CDM_REG_RANDOM_1, w + E007Y_WRAPPER_IRQ_OFF + 0x0);
	put_unaligned_le32(0x00000018, w + E007Y_WRAPPER_IRQ_OFF + 0x4);
	put_unaligned_le32(E007Y_REAR_RUP_AUP_VALUE, w + E007Y_WRAPPER_IRQ_OFF + 0x8);
	put_unaligned_le32(E007Y_CDM_GEN_IRQ, w + E007Y_WRAPPER_IRQ_OFF + 0xc);
	put_unaligned_le32(packet, w + E007Y_WRAPPER_IRQ_OFF + 0x10);
	out->bl[2].dma = dma + E007Y_WRAPPER_EXTRA_OFF; out->bl[2].bytes = 0x0c;
	out->bl[3].dma = dma + E007Y_WRAPPER_CSID_OFF; out->bl[3].bytes = 4;
	out->bl[4].dma = dma + E007Y_WRAPPER_COMPANION_OFF; out->bl[4].bytes = 0x10;
	out->bl[5].dma = dma + E007Y_WRAPPER_IRQ_OFF; out->bl[5].bytes = 0x14;
	out->bl_count = 6;
	return 0;
}

static int
e007y_rear_materialize(struct e007d_rear_register_state *regs,
		       struct e007v_rear_dmi_state *dmi_state,
		       u64 request_id, u8 packet,
		       struct e007y_rear_startup_output *out)
{
	const struct e007y_rear_startup_variant *variant;
	struct e006g_rear_dynamic_payloads *dyn;
	size_t off = 0, dmi_index = 0;
	int ret;

	if (!regs || !dmi_state || !out || packet >= E007Y_STARTUP_PACKETS)
		return -EINVAL;
	variant = &e007y_startup_variants[packet];
	if (!out->main || out->main_bytes != variant->main_bytes ||
	    !out->main_dma || (out->main_dma & 3) ||
	    !out->dmi || out->dmi_count != variant->dmi_count ||
	    !out->dynamic ||
	    !out->wrapper || out->wrapper_bytes < E007Y_WRAPPER_BYTES ||
	    !out->wrapper_dma || (out->wrapper_dma & 3))
		return -EINVAL;

	ret = e007d_rear_validate_register_integration();
	if (ret) return ret;
	dyn = out->dynamic;
	memset(dyn, 0, sizeof(*dyn));
	ret = e007v_rear_prepare_dynamic(dmi_state, request_id, dyn);
	if (ret) return ret;
	memcpy(out->main, variant->skeleton, variant->main_bytes);
	memset(out->bl, 0, sizeof(out->bl)); out->bl_count = 0;

	while (off < variant->main_bytes) {
		u32 header; u8 opcode;
		if (variant->main_bytes - off < sizeof(u32)) { ret = -EPROTO; goto fail; }
		header = get_unaligned_le32(out->main + off); opcode = header >> 24;
		if (opcode == E007Y_OPCODE_REG_CONT) {
			u16 count = header & 0xffff; u32 reg; unsigned int i;
			size_t bytes = 8 + (size_t)count * sizeof(u32);
			if (!count || bytes > variant->main_bytes - off) { ret = -EPROTO; goto fail; }
			reg = get_unaligned_le32(out->main + off + 4);
			if (reg > 0xffff) { ret = -EPROTO; goto fail; }
			for (i = 0; i < count; i++) {
				u32 value;
				ret = e007d_rear_fill_startup(regs, packet, (u16)(reg + 4 * i), &value);
				if (ret) goto fail;
				put_unaligned_le32(value, out->main + off + 8 + 4 * i);
			}
			off += bytes; continue;
		}
		if (opcode == E007Y_OPCODE_DMI || opcode == E007Y_OPCODE_DMI_32 || opcode == E007Y_OPCODE_DMI_64) {
			struct e006g_rear_dmi_slot slot;
			struct e006g_rear_slot_buffer target;
			struct e007y_rear_dmi_target *caller;
			u16 payload_bytes = (header & 0xffff) + 1;
			u32 control; u16 reg; u8 selector; bool bhist_startup;
			if (variant->main_bytes - off < 12 || dmi_index >= out->dmi_count) { ret = -EPROTO; goto fail; }
			control = get_unaligned_le32(out->main + off + 8);
			reg = control & 0xffff; selector = control >> 24;
			caller = &out->dmi[dmi_index];
			if (!caller->cpu || caller->bytes != payload_bytes || !caller->dma || (caller->dma & 3)) { ret = -EINVAL; goto fail; }
			ret = e007y_rear_slot(reg, selector, payload_bytes, &slot, &bhist_startup);
			if (ret) goto fail;
			target.cpu = caller->cpu; target.bytes = caller->bytes;
			if (bhist_startup)
				ret = e007x_bhist16_startup_dmi(packet, reg, selector, target.cpu, target.bytes);
			else
				ret = e007v_rear_fill_slot(dmi_state, request_id, dyn, &slot, &target);
			if (ret) goto fail;
			put_unaligned_le32(caller->dma, out->main + off + 4);
			dmi_index++; off += 12; continue;
		}
		ret = -EPROTO; goto fail;
	}
	if (off != variant->main_bytes || dmi_index != out->dmi_count) { ret = -EPROTO; goto fail; }
	ret = e007y_rear_wrapper(packet, out);
	if (ret) goto fail;
	memzero_explicit(dyn, sizeof(*dyn));
	return 0;
fail:
	memzero_explicit(dyn, sizeof(*dyn));
	e007y_rear_clear_output(out);
	return ret;
}

struct e007y_rear_startup_ops {
	int (*materialize)(struct e007d_rear_register_state *regs,
			   struct e007v_rear_dmi_state *dmi_state,
			   u64 request_id, u8 packet,
			   struct e007y_rear_startup_output *out);
};
static const struct e007y_rear_startup_ops e007y_rear_startup_recipe __used = {
	.materialize = e007y_rear_materialize,
};
'''
    out=pre+chr(10).join(arrays)+chr(10)*2+chr(10).join(table)+chr(10)+post
    a.output.write_text(out)
    safe={
      "schema":"E007y-safe-structure-v1","classification":"OFFLINE_GENERATED_NO_WINDOWS_BYTES",
      "recipe":str(RECIPE.relative_to(R)),
      "variants":{label:{"packet":int(v["capture_n"]),"main_bytes":int(v["main_bytes"]),
        "command_count":int(v["command_count"]),"register_write_count":int(v["register_slots"]),
        "dmi_count":sum(1 for c in v["commands"] if c["command"] in ("DMI","DMI_32","DMI_64")),
        "normalized_skeleton_sha256":v["all_symbolic_normalized_sha256"]} for label,v in vs},
      "dmi_identity_union":[{"reg":f"0x{r:04x}","selector":s,"bytes":n} for r,s,n in sorted(union)],
      "wrapper_lengths":[[4,0xf1c,4,0x3c],[4,0xebc,0xc,4,0x10,0x14],
                         [4,0xa00,0xc,4,0x10,0x14],[4,0x658,0xc,4,0x10,0x14]],
      "runtime_submission":False}
    a.safe.write_text(json.dumps(safe,indent=2,sort_keys=True)+chr(10))
    print("E007Y_GENERATE_PASS",len(out),sha(out.encode()))

if __name__=="__main__": main()
