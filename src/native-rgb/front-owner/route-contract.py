#!/usr/bin/python3
# SPDX-License-Identifier: GPL-2.0-only
# Strict 119-edge parser retained from the accepted camera session contract.
import re
def complete_graph(text: str) -> set[tuple[str,int,str,int]]:
    """Validate all 119 links, both directions, against accepted topology.

    Sensor I2C bus numbers and entity/device numbers are boot-dependent.
    Only sensor names are normalized; pads and graph edges remain exact.
    """
    def canonical(name):
        for sensor,addr in (("imx681","0010"),("ov13858","0010"),
                            ("sp11-vd55g0","0060")):
            if re.fullmatch(rf"{sensor} [0-9]+-{addr}",name):
                return sensor
        return name
    pads={f"msm_csiphy{i}":2 for i in (0,1,2,4)}
    pads.update({f"msm_csid{i}":5 for i in range(5)})
    expected={}
    def edge(a,ap,b,bp,immutable=False):
        expected[(a,ap,b,bp)]=immutable
    for phy in (0,1,2,4):
        for csid in range(5):
            edge(f"msm_csiphy{phy}",1,f"msm_csid{csid}",0)
    for vfe in range(4):
        for port in range(4):
            suffix="pix" if vfe<2 and port==3 else f"rdi{port}"
            capture=f"msm_vfe{vfe}_{suffix}"
            video=f"msm_vfe{vfe}_video{port}"
            pads[capture]=2; pads[video]=1
            edge(capture,1,video,0,True)
            for csid in range(5):
                edge(f"msm_csid{csid}",port+1,capture,0)
    for sensor,phy in (("sp11-vd55g0",0),("ov13858",1),("imx681",2)):
        pads[sensor]=1; edge(sensor,0,f"msm_csiphy{phy}",0,True)
    outgoing={}; incoming={}; entities=set(); ids=set(); devices=set()
    source=None; pad=None; seen_pads=set(); declared_links={}; counts={}
    for line in text.splitlines():
        if line.startswith("- entity "):
            if source is not None and seen_pads!=set(range(pads[source])):
                raise ValueError("INCOMPLETE_ENTITY_PADS")
            m=re.fullmatch(r"- entity (\d+): (.*?) \((\d+) pads?, (\d+) links?(?:, (\d+) routes?)?\)",line)
            if not m: raise ValueError("MALFORMED_ENTITY")
            ident,name,np,nl,nr=m.groups(); source=canonical(name); pad=None
            if ident in ids or source in entities or source not in pads:
                raise ValueError("DUPLICATE_OR_UNEXPECTED_ENTITY")
            if int(np)!=pads[source] or (nr is not None and nr!="0"):
                raise ValueError("UNEXPECTED_PAD_OR_ROUTE_COUNT")
            ids.add(ident); entities.add(source); seen_pads=set()
            declared_links[source]=int(nl); counts[source]=0
        elif "device node name" in line:
            m=re.fullmatch(r"\s*device node name (/dev/(?:v4l-subdev|video)\d+)",line)
            if not m or source is None or m[1] in devices:
                raise ValueError("INVALID_OR_DUPLICATE_DEVICE_NODE")
            devices.add(m[1])
        elif re.match(r"\s*pad\d+:",line):
            m=re.fullmatch(r"\s*pad(\d+): (SINK|SOURCE)",line)
            if not m or source is None: raise ValueError("MALFORMED_PAD")
            pad=int(m[1])
            if pad in seen_pads or pad not in range(pads[source]):
                raise ValueError("DUPLICATE_OR_INVALID_PAD")
            expected_direction="SOURCE" if source in ("imx681","ov13858","sp11-vd55g0") or pad>0 else "SINK"
            if m[2]!=expected_direction: raise ValueError("WRONG_PAD_DIRECTION")
            seen_pads.add(pad)
        elif "->" in line or "<-" in line:
            m=re.fullmatch(r'\s*(->|<-) "([^"]+)":(\d+) \[([^\]]*)\]',line)
            if not m or source is None or pad is None:
                raise ValueError("MALFORMED_LINK")
            arrow,target,tp,raw=m.groups(); target=canonical(target); tp=int(tp)
            tokens=[] if not raw else raw.split(",")
            if len(tokens)!=len(set(tokens)) or set(tokens)-{"ENABLED","IMMUTABLE"}:
                raise ValueError("UNEXPECTED_LINK_FLAGS")
            flags=frozenset(tokens)
            key=(source,pad,target,tp) if arrow=="->" else (target,tp,source,pad)
            table=outgoing if arrow=="->" else incoming
            if key in table: raise ValueError("DUPLICATE_LINK")
            table[key]=flags; counts[source]+=1
    if source is None or seen_pads!=set(range(pads[source])):
        raise ValueError("INCOMPLETE_ENTITY_PADS")
    if entities!=set(pads) or len(devices)!=44 or declared_links!=counts:
        raise ValueError("INCOMPLETE_GRAPH_ENTITIES_DEVICES_OR_LINK_COUNTS")
    if outgoing!=incoming or set(outgoing)!=set(expected):
        raise ValueError("INCOMPLETE_OR_ASYMMETRIC_GRAPH_LINKS")
    enabled=set()
    for key,immutable in expected.items():
        flags=outgoing[key]
        if immutable:
            if flags!={"ENABLED","IMMUTABLE"}:
                raise ValueError("IMMUTABLE_LINK_DRIFT")
        else:
            if "IMMUTABLE" in flags: raise ValueError("MUTABLE_LINK_FALSIFIED")
            if "ENABLED" in flags: enabled.add(key)
    allowed={
        "neutral":set(),
        "front-pix-only":{("msm_csiphy2",1,"msm_csid1",0),
                          ("msm_csid1",4,"msm_vfe1_pix",0)},
        "rear-only":{("msm_csiphy1",1,"msm_csid0",0),
                     ("msm_csid0",1,"msm_vfe0_rdi0",0)},
    }
    if enabled not in allowed.values():
        raise ValueError("UNAUTHORIZED_ENABLED_ROUTE_IN_COMPLETE_GRAPH")
    return enabled


def classify(text):
    enabled = complete_graph(text)
    phases = {
        frozenset(): "neutral",
        frozenset({("msm_csiphy1",1,"msm_csid0",0),
                   ("msm_csid0",1,"msm_vfe0_rdi0",0)}): "rear-only",
        frozenset({("msm_csiphy2",1,"msm_csid1",0),
                   ("msm_csid1",4,"msm_vfe1_pix",0)}): "front-pix-only",
    }
    return phases[frozenset(enabled)], {}
