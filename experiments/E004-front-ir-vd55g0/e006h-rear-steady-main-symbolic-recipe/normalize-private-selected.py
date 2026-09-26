#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct

D=Path(__file__).resolve().parent
R=D.parents[2]
DEC=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"
STRUCT=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/STRUCTURAL-DECODE.json"

REP={"ac8":4,"8f0":10,"a98":25,"658":34}
MODULE={
  0x3b70:"DEMUX_BLS",0x3b74:"DEMUX_BLS",
  0x3d58:"PDPC",0x3d5c:"PDPC",0x3d7c:"PDPC",0x3d84:"PDPC",
  0x4358:"LSC",0x435c:"LSC",
  0x456c:"WB",
  0x4758:"GIC",0x475c:"GIC",
  0x4958:"BPC_ABF",0x495c:"BPC_ABF",
  0x49b8:"BPC_ABF",0x49bc:"BPC_ABF",
  0x5a58:"GTM",0x5a5c:"GTM",
  0x5f58:"GAMMA",0x5f5c:"GAMMA",
  0xa058:"DSX",0xa05c:"DSX",0xa258:"DSX",0xa25c:"DSX",
  0xbc58:"BFSTATS25",0xbc5c:"BFSTATS25",
}

def hx(v): return f"0x{v:x}"
def sha(b): return hashlib.sha256(b).hexdigest()

def dmi_source(reg,sel):
    if reg==0x4308 and sel in (1,2): return "LSC_TINTLESS"
    if reg==0x4708 and sel==1: return "LSC_GIC_ALIAS"
    if reg==0x5a08 and sel==1: return "GTM_TMC"
    if reg==0xbc08 and sel in (1,2): return "BFSTATS25"
    return "STABLE_PROVIDER"

def load_decoder():
    spec=importlib.util.spec_from_file_location("e006a_decoder",DEC)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--private",type=Path,required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()

    private_bytes=a.private.read_bytes()
    j=json.loads(private_bytes.decode("utf-8-sig"))
    if j.get("schema")!="E006a-private-selected-representatives-v1":
        raise SystemExit("private schema drift")
    st=json.loads(STRUCT.read_text())
    dyn={int(x,16) for x in st["steady"]["observed_dynamic_register_offsets_across_repeated_variants"]}
    dec=load_decoder()
    by={(int(x["n"]),int(x["idx"])):x for x in j["records"]}
    variants={}
    unresolved=set()

    for label,n in REP.items():
        r=by[(n,1)]
        data=bytes.fromhex(r["hex"])
        d=dec.decode(data)
        commands=[]
        stable_count=dynamic_count=dmi_count=0
        for c in d["commands"]:
            if c["command"]=="REG_CONT":
                vals=[]
                for i in range(c["count"]):
                    reg=c["register_offset"]+4*i
                    val=struct.unpack_from("<I",data,c["offset"]+8+4*i)[0]
                    if reg in dyn:
                        owner=MODULE.get(reg,"UNRESOLVED_DYNAMIC_REGISTER")
                        if owner.startswith("UNRESOLVED"): unresolved.add(reg)
                        vals.append({"register_offset":hx(reg),"source":"DYNAMIC_PROVIDER","producer":owner})
                        dynamic_count+=1
                    else:
                        vals.append({"register_offset":hx(reg),"source":"STABLE_OBSERVED","value":hx(val)})
                        stable_count+=1
                commands.append({
                    "command":"REG_CONT",
                    "command_offset":hx(c["offset"]),
                    "register_offset":hx(c["register_offset"]),
                    "count":c["count"],
                    "values":vals,
                })
            elif c["command"] in ("DMI","DMI_32","DMI_64"):
                dm=next(x for x in d["dmis"] if x["offset"]==c["offset"])
                w0=struct.unpack_from("<I",data,c["offset"])[0]
                commands.append({
                    "command":c["command"],
                    "command_offset":hx(c["offset"]),
                    "header_middle_byte":(w0 >> 16) & 0xff,
                    "address_field":hx(dm["address_field"]),
                    "dmi_register_offset":hx(dm["dmi_register_offset"]),
                    "selector":dm["dmi_sel"],
                    "payload_bytes":dm["payload_bytes"],
                    "address_source":dmi_source(dm["dmi_register_offset"],dm["dmi_sel"]),
                })
                dmi_count+=1
            else:
                raise SystemExit(f"unexpected steady MAIN opcode {c['command']}")

        sv=next(x for x in st["steady"]["main_variants"] if x["main_bytes"]==len(data))

        # Stronger E006h normalization: zero every DMI address plus every
        # register value whose register offset is known request-varying in
        # any repeated steady variant. This matches the symbolic producer
        # contract even when one particular variant happened to be stable
        # over its limited samples.
        global_holes=set(d["dmi_fields"])
        for field,reg in d["reg_fields"].items():
            if reg in dyn:
                global_holes.add(field)
        z=bytearray(data)
        for off in global_holes:
            z[off:off+4]=b"\0"*4

        variants[label]={
            "capture_n":n,
            "main_bytes":len(data),
            "command_count":len(commands),
            "stable_register_observations":stable_count,
            "dynamic_register_slots":dynamic_count,
            "dmi_slots":dmi_count,
            "e006a_normalized_sha256_if_converged":sv["normalized_sha256_if_converged"],
            "global_symbolic_holes":[hx(x) for x in sorted(global_holes)],
            "global_symbolic_normalized_sha256":sha(z),
            "commands":commands,
        }

    out={
      "schema":"sp11-e006h-rear-steady-symbolic-recipe-v1",
      "source":{
        "private_selected_sha256":sha(private_bytes),
        "raw_bytes_committed":False,
        "captured_dmi_addresses_committed":False,
        "observed_dynamic_register_values_committed":False,
        "stable_register_values_are_derived_register_observations":True,
      },
      "policy":{
        "steady_only":True,
        "startup_composer_authorized":False,
        "dmi_addresses_symbolic":True,
        "request_varying_registers_symbolic":True,
      },
      "representatives":REP,
      "dynamic_register_offsets":[hx(x) for x in sorted(dyn)],
      "unresolved_dynamic_register_owners":[hx(x) for x in sorted(unresolved)],
      "variants":variants,
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("E006H_NORMALIZE_PASS")
    for k,v in variants.items():
        print(k,hex(v["main_bytes"]),"cmd",v["command_count"],
              "stable",v["stable_register_observations"],
              "dyn",v["dynamic_register_slots"],"dmi",v["dmi_slots"])
    print("unresolved_dynamic_register_owners",out["unresolved_dynamic_register_owners"])

if __name__=="__main__":
    main()
