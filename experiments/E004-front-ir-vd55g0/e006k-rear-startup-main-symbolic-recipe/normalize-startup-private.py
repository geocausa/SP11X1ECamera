#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct

D=Path(__file__).resolve().parent
R=D.parents[2]
DEC=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"
STRUCT=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/STRUCTURAL-DECODE.json"
REP={"startup1":0,"startup2":1,"startup3":2,"startup4":3}

def hx(v): return f"0x{v:x}"
def sha(b): return hashlib.sha256(b).hexdigest()

def dmi_source(reg,sel):
    return {
      0x3d08:"PDPC",
      0x4308:"LSC",
      0x4708:"LSC_GIC_ALIAS",
      0x4908:"BPC_ABF",
      0x5a08:"GTM_TMC",
      0x5f08:"GAMMA",
      0xa008:"DSX",
      0xa208:"DSX",
      0xb208:"BHIST16",
      0xbc08:"BFSTATS25",
    }.get(reg,"UNRESOLVED")

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
    assert j.get("schema")=="E006a-private-selected-representatives-v1"
    st=json.loads(STRUCT.read_text())
    dec=load_decoder()
    by={(int(x["n"]),int(x["idx"])):x for x in j["records"]}
    variants={}
    unresolved_dmi=set()

    for label,n in REP.items():
        r=by[(n,1)]
        data=bytes.fromhex(r["hex"])
        d=dec.decode(data)
        commands=[]
        reg_slots=dmi_count=0
        all_holes=set(d["dmi_fields"])

        for c in d["commands"]:
            if c["command"]=="REG_CONT":
                vals=[]
                for i in range(c["count"]):
                    reg=c["register_offset"]+4*i
                    field=c["offset"]+8+4*i
                    vals.append({
                      "register_offset":hx(reg),
                      "source":"STARTUP_REGISTER_PROVIDER"
                    })
                    all_holes.add(field)
                    reg_slots+=1
                commands.append({
                  "command":"REG_CONT",
                  "command_offset":hx(c["offset"]),
                  "register_offset":hx(c["register_offset"]),
                  "count":c["count"],
                  "values":vals,
                })
            elif c["command"] in ("DMI","DMI_32","DMI_64"):
                dm=next(x for x in d["dmis"] if x["offset"]==c["offset"])
                src=dmi_source(dm["dmi_register_offset"],dm["dmi_sel"])
                if src=="UNRESOLVED":
                    unresolved_dmi.add((dm["dmi_register_offset"],dm["dmi_sel"]))
                w0=struct.unpack_from("<I",data,c["offset"])[0]
                commands.append({
                  "command":c["command"],
                  "command_offset":hx(c["offset"]),
                  "header_middle_byte":(w0>>16)&0xff,
                  "address_field":hx(dm["address_field"]),
                  "dmi_register_offset":hx(dm["dmi_register_offset"]),
                  "selector":dm["dmi_sel"],
                  "payload_bytes":dm["payload_bytes"],
                  "address_source":src,
                })
                dmi_count+=1
            else:
                raise SystemExit(f"unexpected startup opcode {c['command']}")

        z=bytearray(data)
        for off in all_holes:
            z[off:off+4]=b"\0"*4

        sv=next(x for x in st["startup"] if x["capture_n"]==n)
        variants[label]={
          "capture_n":n,
          "logical_batch":sv["logical_batch"],
          "main_bytes":len(data),
          "command_count":len(commands),
          "register_slots":reg_slots,
          "dmi_slots":dmi_count,
          "all_symbolic_holes":[hx(x) for x in sorted(all_holes)],
          "all_symbolic_normalized_sha256":sha(z),
          "commands":commands,
        }

    out={
      "schema":"sp11-e006k-rear-startup-symbolic-recipe-v1",
      "source":{
        "private_selected_sha256":sha(private_bytes),
        "raw_bytes_committed":False,
        "captured_dmi_addresses_committed":False,
        "captured_register_values_committed":False,
      },
      "policy":{
        "startup_only":True,
        "all_register_values_symbolic":True,
        "all_dmi_addresses_symbolic":True,
        "linux_rtcdm_submission_authorized":False,
      },
      "representatives":REP,
      "unresolved_dmi_sources":[
        {"dmi_register_offset":hx(r),"selector":s}
        for r,s in sorted(unresolved_dmi)
      ],
      "variants":variants,
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("E006K_NORMALIZE_PASS")
    for k,v in variants.items():
        print(k,hex(v["main_bytes"]),"cmd",v["command_count"],
              "register_slots",v["register_slots"],"dmi",v["dmi_slots"])
    print("unresolved_dmi_sources",out["unresolved_dmi_sources"])

if __name__=="__main__":
    main()
