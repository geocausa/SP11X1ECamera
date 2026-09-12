#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json

D = Path(__file__).resolve().parent
REPO = D.parents[2]
SRC = REPO / "src/front-ir-vd55g0/st-vd55g0"


def need(value, message):
    if not value:
        raise AssertionError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


st = json.load(open(D / "ST-UPSTREAM.json"))
need(st["authority_role"] == "REFERENCE_ONLY", "ST must be reference-only")
need(st["commit"] == "a05627b0f6d8775aa54b6fa306e91f425f2cbf9e", "ST commit")
need(sha(SRC / "vd55g0.c") == st["vd55g0_c_sha256"], "vd55g0.c hash")
need(sha(SRC / "vd55g0_patches.h") == st["vd55g0_patches_h_sha256"], "patch header hash")
need(st["used_to_derive_windows_transport"] is False, "ST not transport authority")
need(st["used_to_authorize_surface_patch"] is False, "ST not patch authority")

build = json.load(open(D / "BUILD-RESULT.json"))
need(build["status"] == "PASS_OFFLINE_PRISTINE_ST_DRIVER_BUILD", "reference build status")
need(build["byte_reproducible_two_builds"] is True, "reference build reproducibility")
need(build["module_sha256_build_a"] == build["module_sha256_build_b"] == "cdf54ebd3429330af845aa8561f0004f06ec36ec28ee09f2e86d997582d48554", "reference module hash")
need(build["module_vermagic"].startswith("7.1.5-sp11-render-parity-v4+"), "reference vermagic")
need(build["module_loaded"] is False and build["sensor_probed"] is False, "reference build remained offline")

print("E004A_REFERENCE_VERIFY=PASS ROLE=REFERENCE_ONLY COMMIT=" + st["commit"])
print("E004A_REFERENCE_BUILD=PASS MODULE_SHA256=" + build["module_sha256_build_a"])
