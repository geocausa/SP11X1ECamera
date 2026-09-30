#!/usr/bin/env python3
"""Verify immutable source boundaries for the E011AU live observer."""
import argparse,hashlib,pathlib
import pefile
ap=argparse.ArgumentParser();ap.add_argument("dll",type=pathlib.Path);a=ap.parse_args()
blob=a.dll.read_bytes()
assert hashlib.sha256(blob).hexdigest()=="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
pe=pefile.PE(data=blob)
checks={
 (0x681c40,128):"c1e16dde175a2d671deceb585fe41dee4e2d866ee68ce50f81544abcb8797097",
 (0x682214,24):"bc6742dbc7ad42cf2aadceeffbb80492ae9fa2dfbe55911982d414f1d9c1ab60",
 (0x686a50,256):"606c6955bc1fd50e0dad6668ac5c789c56a0984e3b725834178a169b7b54b54b",
 (0x687e48,80):"c076a90c21deeab1e383fd9c56b1ca3f4c5124b4a346d8ddec9753d421256aba",
 (0x688258,72):"61aabfe537be35ebfa5b9e82be916e1560467d30b85ca1365ad2237386f68285",
 (0x688434,16):"a850729ebf00777af9c71f13ef15a5a080e985371fa2b80a4cc2586feab808da"}
for (r,n),want in checks.items():assert hashlib.sha256(pe.get_data(r,n)).hexdigest()==want
assert pe.get_data(0x13760c0,16)==b"bgStatsConfigV1\0"
print("PASS_E011AU_STATIC_SOURCE_LOCK")
