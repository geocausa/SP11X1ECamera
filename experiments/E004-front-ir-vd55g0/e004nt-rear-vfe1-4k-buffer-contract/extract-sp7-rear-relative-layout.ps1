# SPDX-License-Identifier: MIT
# E004nt: derive ONLY relative VFE1 rear WM0 Y / WM1 C buffer offsets from
# original SAME SP11 Windows physical KD dd /p captures kept PRIVATE on SP7.
# Never output/export/commit absolute Windows image DMA addresses or pixels.
$ErrorActionPreference='Stop'
$root='C:\Users\SurfacePro7\Documents\KDNET\Codex\E004NQ-REAR-PHYSICAL-20260923'
$out=Join-Path $root 'E004NT-REAR-4K-WM0-WM1-RELATIVE-LAYOUT.json'
if(Test-Path -LiteralPath $out){throw 'E004NT_RELATIVE_LAYOUT_RESULT_ALREADY_CREATED'}
function LocalReg([string]$text,[long]$addr){
 $row=$addr-($addr%16)
 $m=[regex]::Match($text,'(?im)^00000000\x60'+('{0:x8}' -f $row)+'[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})')
 if(-not $m.Success){throw 'E004NT_PRIVATE_RAW_KD_REGISTER_MISSING'}
 return [long][Convert]::ToUInt32($m.Groups[[int](($addr-$row)/4)+1].Value,16)
}
$phases=@()
foreach($phase in @('LIVE1','LIVE2')){
 $raw=[IO.File]::ReadAllText((Join-Path $root ('E004NQ_'+$phase+'.log')),[Text.Encoding]::Unicode)
 if(-not $raw.Contains('===E004NQ_'+$phase+'_VFE1_END===')){throw 'E004NT_SP7_PRIVATE_ORIGINAL_PHASE_INCOMPLETE'}
 $w0=[long]0xac71000+0xe00
 $w1=$w0+0x100
 # Absolute Windows DMA addresses never leave these local variables on SP7.
 $ym=LocalReg $raw ($w0+0x40)
 $yi=LocalReg $raw ($w0+0x04)
 $cm=LocalReg $raw ($w1+0x40)
 $ci=LocalReg $raw ($w1+0x04)
 foreach($v in @($ym,$yi,$cm,$ci)){
  if($v -eq 0 -or $v -eq 0x80000000){throw 'E004NT_UNTRUSTED_PRIVATE_DMA_REGISTER'}
 }
 $yincr=LocalReg $raw ($w0+0x08)
 $cincr=LocalReg $raw ($w1+0x08)
 $ys=LocalReg $raw ($w0+0x14)
 $cs=LocalReg $raw ($w1+0x14)
 $yg=LocalReg $raw ($w0+0x0c)
 $cg=LocalReg $raw ($w1+0x0c)
 $yo=$yi-$ym;$co=$ci-$cm;$cstart=$cm-$ym;$coGlobal=$ci-$ym
 $sum=$yincr+$cincr
 if($yincr -ne 0xa9d000 -or $cincr -ne 0x559000 -or
   $ys -ne 5120 -or $cs -ne 5120 -or
   $yg -ne 0x08700f00 -or $cg -ne 0x04380f00 -or
   $yo -le 0 -or $co -le 0 -or $cstart -lt 0 -or
   $yo -ge $yincr -or $co -ge $cincr -or
   $cstart -ne $yincr -or $coGlobal -ne ($cstart+$co) -or
   $sum -gt [long][uint32]::MaxValue -or
   $yo+$ys*2160 -gt $yincr -or
   $co+$cs*1080 -gt $cincr -or
   $coGlobal+$cs*1080 -gt $sum -or
   $ym%4096 -ne 0 -or $cm%4096 -ne 0){
  throw 'E004NT_REAR_WM0_WM1_RELATIVE_LAYOUT_OR_ROW_BOUNDS_INVALID'
 }
 $phases += [pscustomobject]@{
  phase=$phase
  y_metadata_relative_offset=0
  y_image_relative_offset=[long]$yo
  c_metadata_relative_offset=[long]$cstart
  c_image_relative_offset=[long]$coGlobal
  c_image_relative_to_c_metadata=[long]$co
  y_WM_frame_increment_bytes=[long]$yincr
  c_WM_frame_increment_bytes=[long]$cincr
  single_window_total_bytes=[long]$sum
  y_WM_hardware_stride_bytes=[long]$ys
  c_WM_hardware_stride_bytes=[long]$cs
  y_rows=2160
  c_rows=1080
  metadata_offsets_at_both_plane_starts_page_aligned=$true
  configured_row_extents_fit_in_each_WM_frame_increment=$true
 }
}
if(($phases[0]|ConvertTo-Json -Compress) -ne
   ($phases[1]|ConvertTo-Json -Compress).Replace('"LIVE2"','"LIVE1"')){
 throw 'E004NT_WINDOWS_TWO_CAPTURE_RELATIVE_LAYOUT_NOT_STABLE'
}
$r=[ordered]@{
 schema='sp11-e004nt-windows-rear-VFE1-FULL-WM0-WM1-RELATIVE-only-v1'
 origin='SP7 private E004nq dd /p snapshots of two separate same-SP11 Windows rear 4K OEM live sessions'
 interpretation='relative register deltas and hardware programmed frame increments; not proof of a Linux allocation, mapped RAM, or UBWC image quality'
 no_absolute_DMA_addresses_memory_pointers_or_pixels_exported=$true
 original_SP7_KD_logs_remain_private=$true
 phases=@($phases)
}
[pscustomobject]$r|ConvertTo-Json -Depth 7|Set-Content -LiteralPath $out -Encoding UTF8
Write-Output ('E004NT_REAR_4K_WM_RELATIVE_LAYOUT_TWO_PASSES_PASS exported_bytes='+(Get-Item $out).Length)
foreach($phase in $phases){
 Write-Output ($phase.phase+
  ' Y_data_off=0x'+$phase.y_image_relative_offset.ToString('x')+
  ' C_meta_off=0x'+$phase.c_metadata_relative_offset.ToString('x')+
  ' C_data_off=0x'+$phase.c_image_relative_offset.ToString('x')+
  ' total=0x'+$phase.single_window_total_bytes.ToString('x'))
}
