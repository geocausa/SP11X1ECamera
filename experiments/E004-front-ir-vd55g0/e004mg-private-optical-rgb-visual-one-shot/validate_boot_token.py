#!/usr/bin/env python3
"""Camera-free source+ELF fresh-token gate for both distinct publishers.

Asserts each fresh candidate C source explicitly defines exactly one
literal token (rather than trusting `gcc -D` shell quoting) and the
compiled ELF contains the exact live key. Caller MUST separately run
camera-free token_allowed tests with both candidate sources.
"""
import argparse
from pathlib import Path
import re
import subprocess

def verify(candidate:str,source:Path,binary:Path)->None:
    expected="sp11_camera_"+candidate+"_rgb_session=1"
    text=source.read_text()
    definitions=re.findall(r'^#define SP11_CAMERA_BOOT_TOKEN "([^"\n]*)"$',text,re.M)
    if definitions!=[expected,'']:
        raise ValueError("UNEXPECTED_EXPLICIT_SOURCE_AND_GUARDED_EMPTY_FALLBACK_TOKEN")
    if text.index('#define SP11_CAMERA_BOOT_TOKEN "'+expected+'"')>text.index('#ifndef SP11_CAMERA_BOOT_TOKEN'):
        raise ValueError("CANDIDATE_TOKEN_DEFINED_AFTER_DEFAULT_FALLBACK")
    if not binary.is_file() or binary.is_symlink() or binary.stat().st_size<10000:
        raise ValueError("MISSING_UNTRUSTED_OR_EMPTY_PUBLISHER_ELF")
    strings=subprocess.run(('strings','-a',str(binary)),capture_output=True,
                          text=True,check=True,timeout=8).stdout.splitlines()
    if strings.count(expected)!=1:
        raise ValueError("EXACT_ACTIVE_BOOT_TOKEN_NOT_PRESENT_AS_ELF_STRING")
    if any(x.startswith('sp11_camera_e004me_rgb_session') for x in strings):
        raise ValueError("CONSUMED_IDENTITY_FOUND_IN_NEW_PUBLISHER")
    if not any('SP11_RGB_RAW10_PROFILE camera=' in x for x in strings):
        raise ValueError("FULL10_PHYSICAL_PROFILE_NOT_COMPILED")

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--candidate',required=True)
    for camera in ('front','rear'):
        p.add_argument('--'+camera+'-source',type=Path,required=True)
        p.add_argument('--'+camera+'-elf',type=Path,required=True)
    a=p.parse_args()
    if a.candidate!='e004mg':raise SystemExit('UNEXPECTED_UNIQUE_CANDIDATE')
    for camera in ('front','rear'):
        verify(a.candidate,getattr(a,camera+'_source'),getattr(a,camera+'_elf'))
    print('E004MG_SOURCE_AND_ELF_BOOT_TOKEN_CONTRACT=PASS BOTH_PUBLISHERS CAMERA_ACCESS=NONE')

if __name__=='__main__':main()
