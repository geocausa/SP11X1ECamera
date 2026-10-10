#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile the actual staged kernel gamma/scalar bridge with hosted mocks."""
import argparse,json,pathlib,re,subprocess,hashlib
HERE=pathlib.Path(__file__).resolve().parent
def block(text,start,end):
    assert text.count(start)==1 and text.count(end)==1
    return text[text.index(start):text.index(end)]
ap=argparse.ArgumentParser()
ap.add_argument("--staged",type=pathlib.Path,required=True)
ap.add_argument("--out",type=pathlib.Path,required=True)
args=ap.parse_args();staged=args.staged.resolve();out=args.out.resolve()
if out.exists() or out.is_relative_to(HERE):raise RuntimeError("fresh outside source output required")
names=("native-front-params-kernel.inc","native-front-params.h","native-front-gamma-kernel.inc","native-front-gamma-kernel.h","native-front-gamma.h","native-front-isp-params.h","native-front-param-state.h")
profile_include='#include "native-front-profile-kernel.inc"\n\n'
profile_load=" ret = native_front_profile_load(video);\n if (ret)\n  goto out;\n"
for name in names:
    actual=(staged/name).read_text()
    if name=="native-front-params-kernel.inc":
        assert actual.count(profile_include)==1 and actual.count(profile_load)==1
        actual=actual.replace(profile_include,"",1).replace(profile_load,"",1)
    if actual!=(HERE/name).read_text():raise RuntimeError("staged source drift: "+name)
text=(staged/"camss.c").read_text()
generated=block(text,"enum camss_x1e_epoch0_iq_module {","struct camss_x1e_epoch0_iq_module_input {")
generated+="struct camss_x1e_epoch0_payload_desc { unsigned int module,payload,offset,size; };\n"
generated+=block(text,"static const struct camss_x1e_epoch0_payload_desc camss_x1e_epoch0_payloads[] = {","static const struct camss_x1e_epoch0_reg_patch camss_x1e_epoch0_reg_v0[] = {")
generated+=block(text,'#define CAMSS_X1E_PIX_CAPSULE_MAGIC',"struct camss_x1e_pix_capsule_inputs {")
generated+=block(text,"static int camss_x1e_pix_capsule_validate_sections(","static int camss_x1e_pix_capsule_parse(")
out.mkdir(parents=True,exist_ok=False)
(out/"front-capsule-sections.inc").write_text(generated)
(out/"hosted-front-params-kernel.inc").write_text((staged/"native-front-params-kernel.inc").read_text().replace(profile_include,"",1))
cmd=["gcc","-std=c11","-O1","-g","-Wall","-Wextra","-Werror",
     "-fsanitize=address,undefined","-fno-omit-frame-pointer","-I"+str(staged),
     "-I"+str(out),str(HERE/"test-front-gamma-kernel.c"),"-o",str(out/"test-front-gamma-kernel")]
r=subprocess.run(cmd,text=True,capture_output=True);(out/"BUILD.log").write_text(r.stdout+r.stderr)
if r.returncode:raise RuntimeError(r.stderr)
r=subprocess.run([str(out/"test-front-gamma-kernel")],text=True,capture_output=True)
(out/"RUN.log").write_text(r.stdout+r.stderr)
report={"status":"PASS_HOSTED_ACTUAL_KERNEL_GAMMA_BRIDGE" if not r.returncode else "FAIL",
        "stdout":r.stdout,"stderr":r.stderr,"exit":r.returncode,
        "hardware_access":False,"provider_enqueue":"mock; checks owned immutable copy and identity failure",
        "actual_section_validator_and_lookup":True,"actual_scalar_gamma_submit_and_cleanup":True,"profile_load":"hosted synthetic stub, error propagation checked",
        "ASAN":True,"UBSAN":True,"Werror":True,
        "staged_sources":{name:hashlib.sha256((staged/name).read_bytes()).hexdigest() for name in names}}
(out/"RESULT.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report))
if r.returncode:raise SystemExit(r.returncode)
