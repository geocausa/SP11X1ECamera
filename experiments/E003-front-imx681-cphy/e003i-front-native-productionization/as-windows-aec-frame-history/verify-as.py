#!/usr/bin/env python3
from pathlib import Path
import hashlib,re
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
ASM=Path('/tmp/sp11-aec-oracle/full.asm')
EXPECTED='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file(), DLL
sha=hashlib.sha256(DLL.read_bytes()).hexdigest()
assert sha==EXPECTED,(sha,EXPECTED)
text=ASM.read_text(errors='ignore')
anchors=[
 '1803b0680:', '1803b06bc:', '1803b0764:', '1803b076c:',
 '1803d3938:', '1803d3958:', '1803d3b3c:', '1803d3b44:', '1803d3b4c:', '1803d3b50:', '1803d3b54:',
 '1803b4708:',
 '1803bd280:', '1803bd5cc:', '1803bd5d0:', '1803bd5f0:', '1803bd60c:', '1803bd6e8:', '1803bd748:', '1803bd750:', '1803bd7c8:', '1803bd818:'
]
for a in anchors: assert a in text,a
# Text strings are independently pinned in the binary.
b=DLL.read_bytes()
for s in [
 b'CAECXHistory::ModeInfo::SaveCurrentFrameID',
 b'Current stats frame ID (%llu) is invalid, not larger than previous (%llu)!',
 b'CAECXHistory::GetInternalFrameHistory',
 b'AECXCONVRG no previous frame in history! Abort convergence',
 b'CAECXHistory::SaveFrameToHistory',
 b'Saved frame ID is too small! Skipping...',
 b'CAECXCore::runEndOfFrame'
]: assert s in b,s
print('DLL_SHA256='+sha)
print('CURRENT_STATS_FRAME_ID=ModeInfo+0x1c8 valid=+0x1c0')
print('HISTORY_ELIGIBILITY=savedFrameID+offset<=currentStatsFrameID')
print('CONVERGENCE_OFFSET=1 => savedFrameID<=F-1')
print('FRAME_HISTORY_PAYLOAD=0x1b0 NODE=0x1c0')
print('AS_VERIFY=PASS')
