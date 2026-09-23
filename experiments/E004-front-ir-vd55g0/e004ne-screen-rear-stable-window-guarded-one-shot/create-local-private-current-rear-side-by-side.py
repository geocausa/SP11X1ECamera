#!/usr/bin/python3
"""Produce optional PRIVATE on-device Windows-vs-Linux rear optical panel.

Read original SP11 Windows E004wq OEM rear native 4K Color WinRT
derived private RGB960 (provisional BT709 matrix) only through RO
NTFS under enclosing root0700; compare with distinct time E004ne
Linux original rear private 4K RGB decimated4x to960.
Write final user-owner0600 image ONLY SP11 ~/Pictures private0700.
Do NOT show/return pixels, image arrays, hash, thumbnails or
private screen content via Fabric, chat, Git or another host.
"""
from pathlib import Path
import stat,os
import numpy as np
from PIL import Image,ImageDraw
WIN=Path('/run/sp11-e004ne-private/win-ro/Users/Geoca/Documents/SP11-Camera-E004wq-Screen-Oracle/REAR-WINDOWS-PRIVATE-COLOR-960x540.png')
LI=Path('/home/geoca/Pictures/SP11-Camera-Private-E004ne')
INPUT=LI/'rear-gain-private.png'
OUTPUT=LI/'PRIVATE-SP11-REAR-E004WQ-OEM-WINDOWS-vs-E004NE-LINUX.png'

def run():
    if (WIN.is_symlink() or not WIN.is_file()
        or INPUT.is_symlink() or not INPUT.is_file()
        or LI.stat().st_uid!=1000 or
        stat.S_IMODE(LI.stat().st_mode)!=0o700 or
        INPUT.stat().st_uid!=1000 or
        stat.S_IMODE(INPUT.stat().st_mode)!=0o600 or
        not WIN.parents[4].is_dir()):
        raise RuntimeError('ONLY_PRIVATE_ORIGINALS_ON_SAME_SP11')
    if OUTPUT.exists():raise FileExistsError('NEVER_OVERWRITE_PRIVATE_COMPARISON')
    if (WIN.parents[6].stat().st_uid!=0):
        raise RuntimeError('WINDOWS_ORIGINAL_NOT_MOUNTED_UNDER_PRIVATE_ROOT')
    with Image.open(WIN) as src:
        if src.format!='PNG' or src.mode!='RGB' or src.size!=(960,540):
            raise RuntimeError('WINDOWS_COLOR_ORIGINAL_FORMAT_CHANGED')
        windows=np.asarray(src,dtype=np.uint8).copy()
    with Image.open(INPUT) as src:
        if src.format!='PNG' or src.mode!='RGB' or src.size!=(3840,2160):
            raise RuntimeError('LINUX_REAR_NATIVE_FULL4K_FORMAT_CHANGED')
        linux=np.asarray(src,dtype=np.uint8)[::4,::4,:].copy()
    if windows.shape!=linux.shape!=(540,960,3):
        raise RuntimeError('MATCHED_ORIGINAL_SPATIAL_SAMPLING_MISMATCH')
    panel=Image.new('RGB',(1920,566),(0,0,0))
    panel.paste(Image.fromarray(windows,mode='RGB'),(0,26))
    panel.paste(Image.fromarray(linux,mode='RGB'),(960,26))
    d=ImageDraw.Draw(panel)
    d.text((7,7),'OEM WINDOWS E004wq (prior boot, provisional BT709 preview)',fill=(255,255,255))
    d.text((969,7),'LINUX E004ne (later boot, opt-in BT601, fixed rear gain)',fill=(255,255,255))
    # PIL SAVE only in USER PRIVATE SP11 directory, not to stdout,
    # Git, any connector, /tmp, or another host.
    fd=os.open(OUTPUT,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,'wb') as f:panel.save(f,format='PNG')
    except Exception:
        OUTPUT.unlink(missing_ok=True);raise
    os.chown(OUTPUT,1000,1000)
    assert OUTPUT.stat().st_uid==1000 and stat.S_IMODE(OUTPUT.stat().st_mode)==0o600
    return OUTPUT

if __name__=='__main__':
    print('E004NE_SAME_SP11_USER_PRIVATE_SIDE_BY_SIDE_CREATED_LOCAL_ONLY_NO_PIXEL_EXPORT=YES')
    run()
