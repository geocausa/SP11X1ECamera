#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct

D=Path(__file__).resolve().parent
R=D.parents[2]
DEC=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"
STRUCT=R/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/STRUCTURAL-DECODE.json"

def sha(b): return hashlib.sha256(b).hexdigest()
def u32(v): return int(v,16) if isinstance(v,str) else int(v)

def load_decoder():
    spec=importlib.util.spec_from_file_location("e006a_decoder",DEC)
    m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def reg_value(reg):
    return (0x6b000000 ^ ((reg*0x45d9f3b)&0xffffffff))&0xffffffff

def dmi_addr(reg,sel):
    return (0x88000000 + ((reg&0xffff)<<4)+(sel<<2))&0xffffffff

def emit(v):
    out=bytearray()
    for c in v["commands"]:
        if c["command"]=="REG_CONT":
            count=int(c["count"])
            out+=struct.pack("<II",(3<<24)|count,u32(c["register_offset"]))
            for x in c["values"]:
                out+=struct.pack("<I",reg_value(u32(x["register_offset"])))
        elif c["command"] in ("DMI","DMI_32","DMI_64"):
            op={"DMI":1,"DMI_32":10,"DMI_64":11}[c["command"]]
            n=int(c["payload_bytes"]); reg=u32(c["dmi_register_offset"]); sel=int(c["selector"])
            mid=int(c["header_middle_byte"])
            out+=struct.pack("<III",(op<<24)|(mid<<16)|(n-1),
                             dmi_addr(reg,sel),(sel<<24)|reg)
        else:
            raise AssertionError(c["command"])
    return bytes(out)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--recipe",type=Path,required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    r=json.loads(a.recipe.read_text())
    st=json.loads(STRUCT.read_text())
    dec=load_decoder()
    results={}

    for label,v in r["variants"].items():
        b1=emit(v); b2=emit(v)
        assert b1==b2
        assert len(b1)==v["main_bytes"],(label,len(b1),v["main_bytes"])
        d=dec.decode(b1)
        sv=next(x for x in st["startup"] if x["capture_n"]==v["capture_n"])
        assert len(d["commands"])==sv["command_count"]
        assert len(d["writes"])==sv["register_write_count"]
        assert len(d["dmis"])==sv["dmi_count"]
        got=[{
          "field":f"0x{x['address_field']:x}",
          "dmi_register_offset":f"0x{x['dmi_register_offset']:x}",
          "selector":x["dmi_sel"],
          "payload_bytes":x["payload_bytes"],
        } for x in d["dmis"]]
        assert got==sv["dmi_shape"],(label,got,sv["dmi_shape"])

        z=bytearray(b1)
        for off in [int(x,16) for x in v["all_symbolic_holes"]]:
            z[off:off+4]=b"\0"*4
        match=sha(z)==v["all_symbolic_normalized_sha256"]
        assert match,(label,sha(z),v["all_symbolic_normalized_sha256"])

        results[label]={
          "bytes":len(b1),
          "synthetic_sha256":sha(b1),
          "deterministic_two_run":True,
          "command_count":len(d["commands"]),
          "register_write_count":len(d["writes"]),
          "dmi_count":len(d["dmis"]),
          "all_symbolic_normalized_sha256_match_private":match,
        }

    out={
      "schema":"sp11-e006k-rear-startup-offline-compose-v1",
      "classification":"OFFLINE_FULLY_SYMBOLIC_STARTUP_COMPOSE_PASS",
      "synthetic_register_values_only":True,
      "synthetic_dmi_addresses_only":True,
      "raw_windows_bytes_used_at_compose_time":False,
      "variants":results,
      "linux_rtcdm_submission_authorized":False,
      "native_rear_linux_isp_authorized":False,
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("E006K_OFFLINE_COMPOSE_PASS")
    for k,v in results.items(): print(k,v)

if __name__=="__main__":
    main()
