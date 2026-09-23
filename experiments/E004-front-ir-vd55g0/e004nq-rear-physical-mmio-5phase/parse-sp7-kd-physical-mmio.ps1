# E004nq same-machine SP7 KD dd /p five-phase physical-register scalar reducer.
# ONLY register configuration/geometry scalars; no image addresses, IOVAs or optical bytes.
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $MyInvocation.MyCommand.Path
$out=Join-Path $root 'E004NQ-SCALAR-RESULT.json'
if(Test-Path $out){throw 'E004NQ_ALREADY_REDUCED'}
$regions=[ordered]@{
 WRAPPER=@(0x0acb6000,0x1000)
 CSID0=@(0x0acb7000,0x2000)
 CSID1=@(0x0acb9000,0x2000)
 CSIPHY1=@(0x0ace6000,0x2000)
 VFE0=@(0x0ac62000,0x4000)
 VFE1=@(0x0ac71000,0x4000)
}
$phases=@('IDLE','LIVE1','POST','LIVE2','POST2')
$lineRx=[regex]'(?im)^00000000\x60([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]+([0-9a-f]{8})[ \t]*\r?$'
$maps=@{}
$private=@()
foreach($phase in $phases) {
  $path=Join-Path $root ('E004NQ_'+$phase+'.log')
  if(-not(Test-Path $path)){throw ('E004NQ_MISSING '+$phase)}
  $raw=[IO.File]::ReadAllText($path,[Text.Encoding]::Unicode)
  if(-not $raw.Contains('Closing open log file')){throw ('E004NQ_OPEN_TRACE '+$phase)}
  $parsed=@{}
  foreach($name in $regions.Keys) {
    $base=[uint64]$regions[$name][0]
    $size=[int]$regions[$name][1]
    $begin='===E004NQ_'+$phase+'_'+$name+'_BEGIN==='
    $end='===E004NQ_'+$phase+'_'+$name+'_END==='
    $bi=$raw.IndexOf($begin,[StringComparison]::Ordinal)
    $ei=$raw.IndexOf($end,[StringComparison]::Ordinal)
    if($bi -lt 0 -or $ei -lt ($bi+$begin.Length)){
      throw ('E004NQ_MISSING_PHASE_REGION '+$phase+' '+$name)
    }
    $body=$raw.Substring($bi+$begin.Length,$ei-$bi-$begin.Length)
    $rows=@($lineRx.Matches($body))
    $len=[int]($size/4)
    if($rows.Count -ne ($len/4)){throw ('E004NQ_BAD_DUMP_ROWS '+$phase+' '+$name+' '+$rows.Count)}
    $arr=[uint32[]]::new($len)
    $seen=[bool[]]::new($len)
    foreach($m in $rows){
      $address=[Convert]::ToUInt64($m.Groups[1].Value,16)
      if($address -lt $base -or $address -ge ($base+$size) -or ($address%16) -ne 0){
        throw ('E004NQ_BAD_PHYSICAL_ADDRESS '+$phase+' '+$name)
      }
      $start=[int](($address-$base)/4)
      for($k=0;$k -lt 4;$k++){
        $index=$start+$k
        if($seen[$index]){throw ('E004NQ_DUPLICATE_REGISTER '+$phase+' '+$name)}
        $seen[$index]=$true
        $arr[$index]=[Convert]::ToUInt32($m.Groups[$k+2].Value,16)
      }
    }
    if(@($seen|Where-Object {-not $_}).Count){throw ('E004NQ_MISSING_REGISTER '+$phase+' '+$name)}
    $parsed[$name]=$arr
  }
  $maps[$phase]=$parsed
  $private += [pscustomobject]@{phase=$phase;private_sp7_utf16_original_bytes=(Get-Item $path).Length;complete_physical_regions=$regions.Count}
}
function Get-Reg([uint32[]]$arr,[int]$off) {
 if($off -lt 0 -or ($off%4) -ne 0 -or ($off/4) -ge $arr.Length){throw 'BAD_DWORD_OFFSET'}
 return [uint32]$arr[[int]($off/4)]
}
function Hex32([uint32]$v){return ('0x{0:x8}' -f [uint64]$v)}
$stats=@()
foreach($name in $regions.Keys){
 $a=$maps.IDLE[$name];$b=$maps.LIVE1[$name];$c=$maps.POST[$name];$d=$maps.LIVE2[$name];$e=$maps.POST2[$name]
 $nonzero1=0;$nonzero2=0;$mismatch=0;$mismatch2=0;$livechange=0;$idlesentinel=0
 for($i=0;$i -lt $a.Length;$i++){
  if($a[$i] -eq [uint32]2147483648){$idlesentinel++}
  if($b[$i] -ne 0 -and $b[$i] -ne [uint32]2147483648){$nonzero1++}
  if($d[$i] -ne 0 -and $d[$i] -ne [uint32]2147483648){$nonzero2++}
  if($a[$i] -ne $c[$i]){$mismatch++}
  if($a[$i] -ne $e[$i]){$mismatch2++}
  if($b[$i] -ne $d[$i]){$livechange++}
 }
 $stats += [pscustomobject]@{
  region=$name;source_physical_base=('0x{0:x8}' -f [uint64]$regions[$name][0]);complete_dwords_each_phase=$a.Length
  idle_all_sentinel=($idlesentinel -eq $a.Length)
  LIVE1_nonzero_nonsentinel_dwords=$nonzero1;LIVE2_nonzero_nonsentinel_dwords=$nonzero2
  POST_vs_IDLE_dword_differences=$mismatch;POST2_vs_IDLE_dword_differences=$mismatch2
  LIVE1_vs_LIVE2_dword_differences=$livechange
 }
}
$details=@()
foreach($phase in @('LIVE1','LIVE2')){
 $w=$maps[$phase].WRAPPER
 $wrapper=@()
 for($i=0;$i -lt 3;$i++){$val=Get-Reg $w (4*$i);$wrapper += [pscustomobject]@{csid=$i;config=(Hex32 $val);output_ife_enable=(($val -band 0x100) -ne 0)}}
 $csid=@()
 foreach($idx in @(0,1)){
  $r=$maps[$phase]['CSID'+$idx]
  $cfg=Get-Reg $r 0x300;$cfg1=Get-Reg $r 0x310;$hc=Get-Reg $r 0x35c;$vc=Get-Reg $r 0x360;$fm=Get-Reg $r 0x388
  $csid += [pscustomobject]@{
   instance=$idx;rx_cfg0=(Hex32 (Get-Reg $r 0x200));rx_cfg1=(Hex32 (Get-Reg $r 0x204))
   ipp_cfg0=(Hex32 $cfg);ipp_cfg1=(Hex32 $cfg1)
   ipp_path_enabled=(($cfg -band [uint32]2147483648) -ne 0)
   raw10_csi_data_type=(($cfg -shr 16) -band 63)
   hcrop=(Hex32 $hc);x_start=($hc -band 0x3fff);x_end=(($hc -shr 16) -band 0xffff)
   vcrop=(Hex32 $vc);y_start=($vc -band 0x3fff);y_end=(($vc -shr 16) -band 0xffff)
   format_measure=(Hex32 $fm);measured_width=($fm -band 0xffff);measured_height=(($fm -shr 16) -band 0xffff)
  }
 }
 $vfe=@()
 foreach($idx in @(0,1)){
  $reg=$maps[$phase]['VFE'+$idx];$clients=@()
  $names=@('FULL_Y','FULL_C','DS4','DS16','DISP_Y','DISP_C','DISP_DS4','DISP_DS16','FD_Y','FD_C','PIXEL_RAW','STATS_BE0','STATS_BHIST0','STATS_TINTLESS_BG','STATS_AWB_BG','STATS_AWB_BFW','STATS_BAF','STATS_BHIST','STATS_RS','STATS_IHIST','SPARSE_PD','PDAF_PD_DATA','PDAF_SAD','LCR','RDI0','RDI1','RDI2','LTM_STATS')
  for($i=0;$i -lt 28;$i++){
   $off=0xe00+$i*0x100;$cfg=Get-Reg $reg $off
   if(($cfg -band 1) -ne 0){
    $sz=Get-Reg $reg ($off+0xc)
    $clients += [pscustomobject]@{
     wm=$i;name=$names[$i];config=(Hex32 $cfg);width=($sz -band 0xffff);height=(($sz -shr 16) -band 0xffff)
     stride=(Get-Reg $reg ($off+0x14));packer_config=(Hex32 (Get-Reg $reg ($off+0x18)))
     # Skip +0x04 image_addr, memory IOVAs and image addresses entirely.
    }
   }
  }
  $vfe += [pscustomobject]@{instance=$idx;hardware_version=(Hex32 (Get-Reg $reg 0));bus_version=(Hex32 (Get-Reg $reg 0xc00));enabled_clients=@($clients)}
 }
 $details += [pscustomobject]@{phase=$phase;wrapper=@($wrapper);csid=@($csid);vfe=@($vfe)}
}
if(@($stats|Where-Object {-not $_.idle_all_sentinel -or $_.POST_vs_IDLE_dword_differences -ne 0 -or $_.POST2_vs_IDLE_dword_differences -ne 0}).Count){
 throw 'E004NQ_INCOMPLETE_IDLE_RESTORATION_OR_INVALID_PHASE'
}
if(@($details|Where-Object {$_.wrapper[1].output_ife_enable -ne $true -or $_.wrapper[0].output_ife_enable -ne $false}).Count){throw 'E004NQ_ROUTE_NOT_REPRODUCIBLE'}
if(@($details|Where-Object {@($_.vfe[1].enabled_clients|Where-Object {$_.wm -eq 0 -or $_.wm -eq 1}).Count -ne 2 -or @($_.vfe[0].enabled_clients).Count -ne 0}).Count){throw 'E004NQ_VFE1_FULL_REPRODUCIBILITY_FAILED'}
$result=[ordered]@{
 schema='sp11-e004nq-rear-windows-physical-dd-slash-p-5phase-scalar-v1'
 parent_source_revision='eba30fea25c6fb770ad79f5bcf3abf67aa6626aa'
 acquisition='SP11 same-machine OEM Windows rear VideoRecord 3840x2160 NV12; SP7 KDNET WinDbg dd /p 5 phases'
 phases=$phases;source_private_SP7_KD_mmio_logs=@($private)
 region_stats=@($stats);live_physical_config=@($details)
 rear_OEM_Windows_VFE1_PIX_3840x2160_confirmed_across_two_live_passes=$true
 rear_OEM_Windows_CSID1_IPP_enabled_confirmed_across_two_live_passes=$true
 Linux_rear_native_4k_ISP_optical_frame_proven=$false
 image_dma_addresses_RAW_optical_pixels_images_thumbnails_hashes_exported=$false
}
[pscustomobject]$result|ConvertTo-Json -Depth 10|Set-Content -LiteralPath $out -Encoding UTF8
Write-Output ('E004NQ_FIVE_PHASE_PHYSICAL_SCALAR_PASS '+(Get-Item $out).Length+' bytes')
$stats|Select-Object region,LIVE1_nonzero_nonsentinel_dwords,LIVE2_nonzero_nonsentinel_dwords,LIVE1_vs_LIVE2_dword_differences,POST_vs_IDLE_dword_differences,POST2_vs_IDLE_dword_differences|Format-Table -AutoSize|Out-String|Write-Output
