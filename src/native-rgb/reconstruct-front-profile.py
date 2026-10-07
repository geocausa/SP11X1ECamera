#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reconstruct fixed instruction topology and a private data-only tuning profile.

Original R4 input and the resulting tuning data stay on SP11. The generated GPL
schema contains command encodings/register locations, section topology and masks;
it contains no captured scalar tuning values, table bytes or device addresses.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

R4_SHA256 = "1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa"
HEADER_BYTES = 64
CAPSULE_BYTES = 41088

def reconstruct(capsule):
    if hashlib.sha256(capsule).hexdigest() != R4_SHA256:
        raise ValueError("unqualified private startup profile")
    u32 = lambda p: struct.unpack_from("<I", capsule, p)[0]
    if capsule[:8] != b"E3HPIX01" or [u32(p) for p in [8,12,16,20,40,52,56,60]] != [1,1024,CAPSULE_BYTES,36,0x958,0,0,0]:
        raise ValueError("capsule identity/layout")
    if struct.unpack_from("<Q", capsule, 44)[0] != 4:
        raise ValueError("startup request")
    rebuilt = bytearray(CAPSULE_BYTES)
    rebuilt[:8] = b"E3HPIX01"
    fixed, copies, body = [], [], bytearray()
    scalar_words = table_bytes = commands = 0
    sections = []

    def constant(pos, value):
        fixed.append((pos, value))
        struct.pack_into("<I", rebuilt, pos, value)

    def move(pos, size, table=False):
        nonlocal scalar_words, table_bytes
        if size % 4 or pos % 4:
            raise ValueError("unaligned semantic region")
        source = HEADER_BYTES + len(body)
        copies.append((pos, source, size))
        body.extend(capsule[pos:pos+size])
        rebuilt[pos:pos+size] = capsule[pos:pos+size]
        if table:
            table_bytes += size
        else:
            scalar_words += size // 4

    for pos,value in [(8,1),(12,1024),(16,CAPSULE_BYTES),(20,36),(40,0x958),(44,4)]:
        constant(pos,value)
    move(24,16) # Four source-qualified startup/priming logical period values.
    seen = set()
    spans = []
    for i in range(36):
        p = 64 + i*16
        kind,index,offset,size = struct.unpack_from("<4I", capsule, p)
        if (kind,index) in seen or kind not in range(1,6) or offset % 64 or not size or offset < 1024 or offset+size > len(capsule):
            raise ValueError("section admission")
        seen.add((kind,index))
        if any(offset < b and a < offset+size for a,b in spans):
            raise ValueError("overlapping section")
        spans.append((offset,offset+size))
        sections.append((kind,index,offset,size))
        for n,value in enumerate((kind,index,offset,size)):
            constant(p+n*4,value)
        if kind in (1,3):
            pos,end = offset,offset+size
            while pos < end:
                header = u32(pos)
                opcode,count = header >> 24, header & 0xffff
                if opcode == 1:
                    if pos+12 > end or u32(pos+4) != 0:
                        raise ValueError("DMI must have a zero address hole")
                    constant(pos,header)
                    constant(pos+8,u32(pos+8))
                    pos += 12
                elif opcode == 3:
                    reg = u32(pos+4)
                    if header & 0x00ff0000 or not count or pos+8+4*count > end or reg & 0xff000003:
                        raise ValueError("register command shape")
                    if any(0xc00 <= reg+4*n < 0x2e00 for n in range(count)):
                        raise ValueError("BUS programming is not tuning")
                    constant(pos,header)
                    constant(pos+4,reg)
                    move(pos+8,count*4)
                    pos += 8+count*4
                else:
                    raise ValueError("unsupported instruction topology")
                commands += 1
            if pos != end:
                raise ValueError("command span")
        elif kind == 4:
            if index != 0 or size != 9*32:
                raise ValueError("module record topology")
            for n in range(9):
                pos = offset+n*32
                if u32(pos) & 0xffff0000 or u32(pos+28):
                    raise ValueError("module reserved bits")
                constant(pos,u32(pos))
                move(pos+4,24)
        else:
            move(offset,size,table=True)
    wanted = {(1,n) for n in range(4)} | {(2,n) for n in range(16)} | {(3,0),(4,0)} | {(5,n) for n in range(14)}
    if seen != wanted or rebuilt != capsule:
        raise ValueError("reconstruction does not exactly match qualified input")
    header = struct.pack("<8s14I",b"QXTPRF01",1,HEADER_BYTES,HEADER_BYTES+len(body),0x80100,
                         2560,1440,3840,2160,0x3231564e,scalar_words,table_bytes,0,0,0)
    firmware = header + body
    digest = hashlib.sha256(firmware).digest()
    schema = [
        "/* SPDX-License-Identifier: GPL-2.0-only",
        " * Reconstructed front mode instruction topology. No tuning/table data.",
        " * CDM encoding: published Qualcomm camera-driver82ac3a6 cam_cdm_util.",
        " * Register locations/holes: retained reviewed E003h/Epoch0 source.",
        " * The fixed private qualification digest admits only this exact profile.",
        " */",
        "#ifndef NATIVE_FRONT_PROFILE_SCHEMA_H",
        "#define NATIVE_FRONT_PROFILE_SCHEMA_H",
        f"#define NATIVE_FRONT_PROFILE_BYTES {len(firmware)}U",
        f"#define NATIVE_FRONT_PROFILE_SCALAR_WORDS {scalar_words}U",
        f"#define NATIVE_FRONT_PROFILE_TABLE_BYTES {table_bytes}U",
        f"#define NATIVE_FRONT_PROFILE_CAPSULE_BYTES {CAPSULE_BYTES}U",
        f"#define NATIVE_FRONT_PROFILE_DEMUX_OFFSET {next(src for dst,src,n in copies if dst == next(off for kind,index,off,size in sections if kind == 4)+4)}U",
        "struct native_front_profile_fixed { u32 destination; u32 value; };",
        "struct native_front_profile_copy { u32 destination; u32 source; u32 bytes; };",
        "static const u8 native_front_profile_digest[32] = {",
        " " + ", ".join(f"0x{v:02x}" for v in digest) + " };",
        "static const struct native_front_profile_fixed native_front_profile_fixed[] = {",
        *[f" {{ 0x{p:x}, 0x{v:08x} }}," for p,v in fixed], "};",
        "static const struct native_front_profile_copy native_front_profile_copies[] = {",
        *[f" {{ 0x{p:x}, 0x{s:x}, 0x{b:x} }}," for p,s,b in copies], "};",
        "#endif", ""
    ]
    return firmware, "\n".join(schema), {"status":"RECONSTRUCTED_DATA_ONLY_FRONT_PROFILE",
        "qualified_original_sha256":R4_SHA256,"firmware_sha256":digest.hex(),
        "firmware_bytes":len(firmware),"scalar_words":scalar_words,"table_bytes":table_bytes,
        "instruction_count":commands,"fixed_structure_words":len(fixed),"semantic_copy_regions":len(copies),
        "command_words_in_firmware":False,"register_addresses_in_firmware":False,
        "device_addresses_in_firmware":False,"exact_internal_reconstruction":True}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qualified-r4",type=Path,required=True)
    parser.add_argument("--private-out",type=Path,required=True)
    parser.add_argument("--schema-out",type=Path,required=True)
    args = parser.parse_args()
    if args.private_out.exists() or args.schema_out.exists():
        parser.error("fresh outputs required")
    data,schema,result = reconstruct(args.qualified_r4.read_bytes())
    args.private_out.mkdir(parents=True,mode=0o700)
    firmware = args.private_out / "imx681-2560x1440-nv12-v1.bin"
    firmware.write_bytes(data)
    firmware.chmod(0o600)
    args.schema_out.write_text(schema)
    (args.private_out / "PROFILE-RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
